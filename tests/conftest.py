import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import mock_integration


# Use the pytest fixture to get the Home Assistant instance for testing
# @pytest.fixture
# async def hass():
#     """Create and provide a Home Assistant instance for testing."""
#     hass_instance = HomeAssistant()
#
#     # Optionally mock integrations if needed
#     await mock_integration(hass_instance, "microclimate_integration")
#
#     return hass_instance
#
from pytest_homeassistant_custom_component.common import async_test_home_assistant
@pytest.fixture()#autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield


# @pytest.fixture
# async def hass():#autouse=True):
#     """Provide a Home Assistant test instance."""
#     print("Creating Home Assistant instance...")
#     async with async_test_home_assistant() as hass_instance:
#         print("Starting Home Assistant instance...")
#         await hass_instance.async_start()
#         print("Home Assistant instance started.")
#         yield hass_instance
#         print("Stopping Home Assistant instance...")
#         await hass_instance.async_stop()
#         print("Home Assistant instance stopped.")
#
# @pytest.fixture
# def hass2():
#     """Provide a Home Assistant test instance."""
#     hass_instance = async_test_home_assistant()  # Call it synchronously for debugging
#     hass_instance.async_start()  # Ensure HA is started
#     return hass_instance



# Now, you can use this fixture in your test cases
async def test_example(hass):
    """Test Home Assistant functionality"""
    assert hass is not None
    # You can perform actions like service calls or entity state checks here
