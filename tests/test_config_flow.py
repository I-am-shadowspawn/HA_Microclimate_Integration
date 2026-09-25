from unittest.mock import patch, AsyncMock
import pytest
from homeassistant import data_entry_flow
from custom_components.microclimate_integration.config_flow import  MicroclimateConfigFlow  # Import the config flow directly
from custom_components.microclimate_integration.const import MODEL_OPTIONS  # Import the constants if needed
from homeassistant.data_entry_flow import FlowResultType
import voluptuous as vol

@pytest.mark.asyncio
async def test_async_step_user_form_displayed():
    """Test that the user form is displayed when no user input is provided."""

    flow = MicroclimateConfigFlow()
    result = await flow.async_step_user(None)  # Pass None for user input

    # Check that the result is showing the form
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert "evo_device" in result["data_schema"].schema
    assert "token" in result["data_schema"].schema
    assert "model" in result["data_schema"].schema


@pytest.mark.asyncio
async def test_async_step_user_create_entry(hass):
    """Test that a config entry is created when valid user input is provided."""

    user_input = {
        "evo_device": "Device_123",
        "token": "valid_token",
        "model": "Evo Connect",  # Assume this is in MODEL_OPTIONS
    }

    flow = MicroclimateConfigFlow()

    flow.hass = hass
    flow.context = {"source": "user"}

    expected_result = {
        "type": FlowResultType.CREATE_ENTRY,
        "title": "Microclimate Evo Device: Device_123",
        "data": {
            "evo_device": "Device_123",
            "token": "valid_token",
            "model": "Evo Connect",
        },
    }
    # Mock async_create_entry to track if it's called
    with patch.object(flow, "async_create_entry", return_value=expected_result) as mock_create_entry:
        result = await flow.async_step_user(user_input)

        # Ensure the async_create_entry method was called with the expected data
        mock_create_entry.assert_called_once_with(
            title="Microclimate Evo Device: Device_123",
            data={
                "evo_device": "Device_123",
                "token": "valid_token",
                "model": "Evo Connect",
            }
        )

        # Ensure the result is a flow result with type create_entry
        assert result["type"] == FlowResultType.CREATE_ENTRY


@pytest.mark.asyncio
async def test_async_step_user_missing_field():
    """Test that an error is raised if required fields are missing."""

    user_input = {
        "evo_device": "Device_123",
        #"token": "valid_token",
        # Missing "model" field
    }

    flow = MicroclimateConfigFlow()

    result = await flow.async_step_user(user_input)

    # Check if the form is shown again due to missing required fields
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert "model" in result["data_schema"].schema



@pytest.mark.asyncio
async def test_async_step_user_invalid_model():
    """Test that an invalid model results in form being shown again."""

    user_input = {
        "evo_device": "Device_123",
        "token": "valid_token",
        "model": "Invalid_Model",  # Invalid model, should not be in MODEL_OPTIONS
    }

    flow = MicroclimateConfigFlow()

    # Mock async_create_entry to track if it's called
    with patch.object(flow, "async_create_entry", return_value=None) as mock_create_entry:
        result = await flow.async_step_user(user_input)

        # Ensure async_create_entry is NOT called due to invalid model
        mock_create_entry.assert_not_called()

        # Ensure the result is a flow result with type FORM (as the model is invalid)
        assert result["type"] == data_entry_flow.FlowResultType.FORM

@pytest.mark.asyncio
async def test_async_step_user_default_model(hass):
    """Test that the default model is selected if not provided."""

    # Correct user input with missing model
    user_input = {
        "evo_device": "Device_123",
        "token": "valid_token",
    }

    flow = MicroclimateConfigFlow()
    flow.hass = hass
    flow.context = {"source": "user"}

    expected_result = {
        "type": FlowResultType.CREATE_ENTRY,
        "title": "Microclimate Evo Device: Device_123",
        "data": {
            "evo_device": "Device_123",
            "token": "valid_token",
            "model": next(iter(MODEL_OPTIONS)),  # Default model should be used
        },
    }
    # Mock async_create_entry to track if it's called
    with patch.object(flow, "async_create_entry", return_value=expected_result) as mock_create_entry:
        result = await flow.async_step_user(user_input)

        # Ensure async_create_entry method is called with the default model
        mock_create_entry.assert_called_once_with(
            title="Microclimate Evo Device: Device_123",
            data={
                "evo_device": "Device_123",
                "token": "valid_token",
                "model": next(iter(MODEL_OPTIONS)),  # Default model should be used
            }
        )

        # Ensure the result is a flow result with type create_entry
        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY

def test_get_data_schema_valid():
    """Test that the schema contains the expected fields and choices for 'model'."""
    flow = MicroclimateConfigFlow()
    schema = flow._get_data_schema()

    assert isinstance(schema, vol.Schema)  # ✅ Ensure it returns a valid schema
    schema_dict = schema.schema  # Get the underlying schema definition

    assert "evo_device" in schema_dict  # ✅ Ensure 'evo_device' is a required field
    assert "token" in schema_dict  # ✅ Ensure 'token' is a required field
    assert "model" in schema_dict  # ✅ Ensure 'model' field exists

    # ✅ Check that 'model' field enforces valid choices
    assert isinstance(schema_dict["model"], vol.In)  # Ensure 'model' uses vol.In()
    assert set(schema_dict["model"].container) == set(MODEL_OPTIONS)  # Ensure correct options

def test_get_data_schema_default_model():
    """Test that the first model in MODEL_OPTIONS is set as the default."""
    flow = MicroclimateConfigFlow()
    schema = flow._get_data_schema()

    expected_default = next(iter(MODEL_OPTIONS), None)  # ✅ First model as default

    # ✅ Provide required fields except "model" to let voluptuous apply defaults
    validated_data = schema({"evo_device": "test_device", "token": "test_token"})

    assert validated_data["model"] == expected_default  # ✅ Ensure correct default model is applied

def test_get_data_schema_no_models():
    """Test that an error is raised when MODEL_OPTIONS is empty."""
    with patch("custom_components.microclimate_integration.config_flow.MODEL_OPTIONS", []):
        flow = MicroclimateConfigFlow()
        with pytest.raises(vol.Invalid, match="No valid models available."):
            flow._get_data_schema()


@pytest.fixture(autouse=True)
def mock_validation_transport():
    with patch("custom_components.microclimate_integration.api_client.fetch_data", new=AsyncMock(return_value={})):
        yield
