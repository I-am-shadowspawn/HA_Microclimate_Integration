"""Stream adapter for existing fake HTTP JSON responses."""
import json
from unittest.mock import Mock


def json_stream(response):
    async def chunks(_size):
        yield json.dumps(await response.json()).encode()
    response.content = Mock(iter_chunked=chunks)
    return response
