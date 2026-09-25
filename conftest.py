import pytest

@pytest.fixture(autouse=True)
def enable_review_components(enable_custom_integrations):
    yield
