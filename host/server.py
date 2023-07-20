#!/bin/env python
import sys
import json
import struct
import asyncio
import socket
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler
from io import BytesIO


tabs_future = None
browser = None


async def send_to_browser(message):
    if browser:
        await send_message(browser, message)


async def get_tabs():
    global tabs_future
    if tabs_future is None or tabs_future.done():
        tabs_future = asyncio.Future()
    await send_to_browser({'type': 'tabs'})
    tabs = await tabs_future
    tabs_future = None
    return tabs


async def send_message(writer, message):
    encoded_content = json.dumps(message).encode('utf-8')
    encoded_length = struct.pack('@I', len(encoded_content))
    writer.write(encoded_length)
    writer.write(encoded_content)
    await writer.drain()


async def send_to_browser(message):
    await send_message(browser, message)


async def read_message(reader):
    text_length_bytes = await reader.readexactly(4)
    text_length = struct.unpack('@I', text_length_bytes)[0]
    text = (await reader.readexactly(text_length)).decode('utf-8')
    return json.loads(text)


async def start_extension_server(handler):
    global browser
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    transport, _ = await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    writer_transport, writer_protocol =\
        await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
    browser = writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, loop)
    while True:
        await handler(reader, writer)


async def handle_extension(reader, writer):
    message = await read_message(reader)
    message_type = message['type']
    if message_type == 'ping':
        await send_message(writer, {'type': 'pong'})
    elif message_type == 'tabs':
        if tabs_future and not tabs_future.done():
            tabs_future.set_result(message['data'])


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()


def format_tab(tab):
    url = tab["url"].replace("http://", "").replace("https://", "").replace("www.", "")
    return f'{tab["title"]} {url}'


async def handle_command(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data = b''
    while True:
        chunk = await reader.read(100)
        data += chunk
        if not chunk or b'\r\n\r\n' in chunk:
            break

    if data:
        response = 'ok'
        request = HTTPRequest(data)
        query = parse_qs(request.path.lstrip('/').lstrip('?'))

        try:
            if request.command == 'POST':
                await send_to_browser({'type': 'open', 'data': query['url'][0]})

            elif request.command == 'GET':
                tabs = await get_tabs()
                response = '\n'.join((f'{i + 1}: {format_tab(tab)}' for i, tab in enumerate(tabs)))

            elif request.command == 'DELETE':
                tabs = await get_tabs()
                if 'after' in query:
                    index = int(query['index'][0])
                    to_delete = tabs[index:]
                    await asyncio.gather(*(
                        send_to_browser({'type': 'close', 'data': tab['id']}) for tab in to_delete
                    ))
                else:
                    index = int(query['index'][0]) - 1
                    to_delete = tabs[index]
                    await send_to_browser({'type': 'close', 'data': to_delete['id']})
            elif request.command == 'PUT':
                index = int(query['index'][0]) - 1
                tabs = await get_tabs()
                to_open = tabs[index]
                await send_to_browser({'type': 'switch', 'data': to_open['id']})
        except Exception as e:
            response = str(e)

        writer.write('\n'.join((
            'HTTP/1.1 200 OK',
            'Content-Type: text/plain',
            f'Content-Length: {len(response.encode())}',
            'Connection: close',
            '',
            f'{response}'
        )).strip().encode())
        await writer.drain()

    writer.close()


async def main():
    command_server = asyncio.start_server(handle_command, '127.0.0.1', 9222)
    extension_server = start_extension_server(handle_extension)
    await asyncio.gather(command_server, extension_server)


asyncio.run(main())
