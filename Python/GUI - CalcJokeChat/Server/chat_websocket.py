import os
import logging
import asyncio
import websockets

file_dir = os.path.dirname(os.path.realpath(__file__))
log_file_name = "ws_logs.log"
log_file_path = os.path.join(file_dir, log_file_name)

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)


CLIENTS = set()


async def send_message_to_all_clients(message):
    if CLIENTS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([client.send(message) for client in CLIENTS])
        client_identifiers = ", ".join([str(client.remote_address[1]) for client in CLIENTS])
        logging.info(f"Sending message to {len(CLIENTS)} clients ({client_identifiers}).")
        logging.info(f"Message: '{message}'")


async def register_client(websocket):
    CLIENTS.add(websocket)
    client_ip = websocket.request_headers.get("X-Forwarded-For", "unknown")
    identifier = websocket.remote_address[1]
    info = (
        f"Registering new client: ip={client_ip}, identifier: {identifier}. "
        f"Current amount: {len(CLIENTS)}"
    )
    logging.info(info)


async def unregister_client(websocket):
    CLIENTS.remove(websocket)
    client_ip = websocket.request_headers.get("X-Forwarded-For", "unknown")
    identifier = websocket.remote_address[1]
    info = (
        f"Removing a client: ip={client_ip}, identifier: {identifier}. "
        f"Current amount: {len(CLIENTS)}"
    )
    logging.info(info)


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
