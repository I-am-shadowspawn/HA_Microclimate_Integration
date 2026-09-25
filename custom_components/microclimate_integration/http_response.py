"""Bound buffered/decompressed response bodies before parsing or diagnostic logging."""
async def read_body(response, limit):
    body = bytearray()
    async for chunk in response.content.iter_chunked(8192):
        body.extend(chunk)
        if len(body) > limit:
            raise ValueError('Response body exceeds size limit')
    return bytes(body)
