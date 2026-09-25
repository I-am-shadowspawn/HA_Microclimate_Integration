"""One-shot HTTP behavior, bounded streams and credential-safe failures."""
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import quote, quote_plus
import pytest
from yarl import URL
from custom_components.microclimate_integration.write_transport import update_pin, UpdateResult, MAX_BODY, retry_after_seconds
from custom_components.microclimate_integration.api_client import fetch_data, EvoDeviceDataError, redact_response


def response(status,body=b'',headers=None):
    async def chunks(_size):
        for i in range(0,len(body),8192):yield body[i:i+8192]
    r=Mock(status=status,headers=headers or {},content=Mock(iter_chunked=chunks))
    cm=AsyncMock();cm.__aenter__.return_value=r
    return cm


@pytest.mark.parametrize('status,body,expected',[(200,b'','acknowledged'),(200,b'{}','acknowledged'),
    (200,b'{"error":{"message":"wrong pin"}}','rejected'),(400,b'bad','rejected'),
    (400,b'{"error":{"message":"Invalid token."}}','invalid_auth'),(401,b'','invalid_auth'),
    (429,b'','rate_limited'),(503,b'','uncertain'),(302,b'','uncertain'),(200,b'bad','uncertain'),
    (200,b'x'*(MAX_BODY+1),'uncertain')])
async def test_update_once(status,body,expected):
    session=Mock(get=Mock(return_value=response(status,body,{'Retry-After':'2'})))
    value='7200\0'+'7200\0Europe/London\0'+'0'
    result=await update_pin('fake','v32',value,session=session)
    assert result.outcome==expected
    assert session.get.call_count==1
    args=session.get.call_args
    assert args.args==('https://microclimate.blynk.cc/external/api/update',)
    assert args.kwargs['allow_redirects'] is False
    assert args.kwargs['params']=={'token':'fake','v32':value}
    url=URL(args.args[0]).with_query(args.kwargs['params'])
    assert '%00' in str(url) and '%2500' not in str(url)
    assert url.query['v32']==value
    if status==429:assert result.retry_after==2


@pytest.mark.parametrize('err',[TimeoutError('token secret'),RuntimeError('token secret')])
async def test_transport_uncertain_sanitized(err):
    session=Mock();session.get.side_effect=err
    assert await update_pin('secret','v20','09/02',session=session)==UpdateResult('uncertain')
    assert session.get.call_count==1


async def test_cancellation_and_invalid_target():
    session=Mock();session.get.side_effect=asyncio.CancelledError()
    with pytest.raises(asyncio.CancelledError):await update_pin('secret','v20','09/02',session=session)
    session.get.reset_mock()
    assert (await update_pin('secret','http://bad','x',session=session)).outcome=='rejected'
    session.get.assert_not_called()


@pytest.mark.parametrize('body',[b'x'*(1024*1024+1),b'notjson',b'[]'])
async def test_bounded_invalid_reads(body):
    session=Mock(get=Mock(return_value=response(200,body)))
    with pytest.raises(EvoDeviceDataError):await fetch_data('secret',session=session)
    assert session.get.call_args.kwargs['allow_redirects'] is False


def test_encoded_token_redaction_and_retry_after():
    token='secret /+?'
    for text in [token,quote(token,safe=''),quote_plus(token,safe=''),quote(token,safe='').replace('%2F','%2f')]:
        assert redact_response({'value':text},token)=={'value':'[REDACTED]'}
    assert retry_after_seconds('9999')==60
    assert retry_after_seconds('nan')==0
    assert retry_after_seconds('bad')==0


@pytest.mark.parametrize('body',[b'{"error":{"message":"Backend unavailable"}}',b'{"error":{"message":"Invalid token."}}'])
async def test_5xx_error_body_still_uncertain(body):
    session=Mock(get=Mock(return_value=response(503,body)))
    assert (await update_pin('fake','v20','09/02',session=session)).outcome=='uncertain'
    assert session.get.call_count==1
