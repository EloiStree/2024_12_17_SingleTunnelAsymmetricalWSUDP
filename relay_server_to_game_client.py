## Demo of how to use:
# https://github.com/EloiStree/2022_01_24_XOMI/tree/main/HowToUse

import asyncio
import websockets
import socket
import requests
import uuid
import time

# Listen to any incoming UDP messages
LISTENER_UDP_IP = "0.0.0.0"
# Uncomment below to only allow the app on the Raspberry Pi
# LISTENER_UDP_IP = "127.0.0.1"
LISTENER_UDP_PORT = 3615
SERVER_WS_PORT = 6777

bool_use_debug_print = True



clients = set()

def debug_print(message):
    if bool_use_debug_print:
        print(message)
    

async def udp_listener():
    
    while True:
        """Listens for incoming UDP messages and relays them to WebSocket clients."""
        # debug_print(f"Starting UDP listener on {LISTENER_UDP_IP}:{LISTENER_UDP_PORT}")
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(),
            local_addr=(LISTENER_UDP_IP, LISTENER_UDP_PORT)
        )
        try:
            await asyncio.sleep(3600)  # Keep the listener running
        finally:
            transport.close()

class UDPServerProtocol:
    def connection_made(self, transport):
        self.transport = transport
    def datagram_received(self, data, addr):
        debug_print(f"Received {len(data)} bytes from {addr}")
        asyncio.create_task(relay_to_clients(data))
    def connection_lost(self, exc):
        debug_print("UDP connection closed.")



async def relay_to_clients(data):
    """Relays the given data to all connected WebSocket clients."""
    if not clients:
        debug_print("No clients connected to relay data.")
        return
    
    disconnected_clients = set()
    for client in clients:
        try:
            if client and not client.closed:
                await client.send(data)
                debug_print(f"Sent {len(data)} bytes to client.")
            else:
                disconnected_clients.add(client)
        except Exception as e:
            debug_print(f"Error sending to client: {e}")
            disconnected_clients.add(client)
    
    # Clean up closed or problematic clients
    for client in disconnected_clients:
        clients.discard(client)
        debug_print(f"Removed disconnected client: {client}")

async def ws_handler(websocket, path):
    """Handles new WebSocket connections, handshakes, and messages."""
    clients.add(websocket)
    debug_print(f"New WebSocket client connected: {websocket.remote_address}")
    
    try:
        # Send handshake GUID to the client
        handshake_guid = str(uuid.uuid4())
        await websocket.send(f"GUID:{handshake_guid}")
        debug_print(f"Sent handshake GUID to client: {handshake_guid}")

        # Listen for client messages
        async for message in websocket:
            if message.startswith("SIGNED:"):
                debug_print(f"Received SIGNED message from client: {message}")
                await websocket.send(f"HELLO: {message}")
            else:
                debug_print(f"Unknown message from client: {message}")
    
    except websockets.exceptions.ConnectionClosedError as e:
        debug_print(f"WebSocket closed with error: {e.code} - {e.reason}")
    except Exception as e:
        debug_print(f"WebSocket handler error: {e}")
    finally:
        clients.remove(websocket)
        debug_print(f"WebSocket client disconnected: {websocket.remote_address}")

async def main():
    """Main function to start UDP listener and WebSocket server."""
    try:
        udp_task = asyncio.create_task(udp_listener())
        ws_server = await websockets.serve(ws_handler, "0.0.0.0", SERVER_WS_PORT)
        debug_print(f"WebSocket server running on ws://{get_public_ip()}:{SERVER_WS_PORT}")
        await asyncio.gather(udp_task, ws_server.wait_closed())
    except Exception as e:
        debug_print(f"Main Error: {e}")

def get_public_ip():
    """Fetches the public IP of the device."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        return "Unavailable"

if __name__ == "__main__":
    public_ip = get_public_ip()
    debug_print(f"Device Public IP: {public_ip}")
    debug_print(f"Starting UDP listener on {LISTENER_UDP_IP}:{LISTENER_UDP_PORT}")
    debug_print(f"Starting WebSocket server on ws://{public_ip}:{SERVER_WS_PORT}")
    asyncio.run(main())
