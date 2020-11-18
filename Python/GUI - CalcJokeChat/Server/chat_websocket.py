import asyncio
import websockets

CLIENTS = set()


async def send_message_to_all_clients(message):
    if CLIENTS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([client.send(message) for client in CLIENTS])


async def register_client(websocket):
    CLIENTS.add(websocket)


async def unregister_client(websocket):
    CLIENTS.remove(websocket)


async def relaying_messages_to_all_clients(websocket, path):
    await register_client(websocket)
    try:
        async for message in websocket:
            await send_message_to_all_clients(message)
    finally:
        await unregister_client(websocket)


if __name__ == "__main__":
    start_server = websockets.serve(relaying_messages_to_all_clients, "localhost", 9876)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
