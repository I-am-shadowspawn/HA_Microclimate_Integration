async def test_hass_fixture(hass):
    hass.states.async_set('sensor.review_probe', 'ok')
    assert hass.states.get('sensor.review_probe').state == 'ok'
