import asyncio
import websockets
import os
import time
import ssl
import struct
import random

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

player_index = random.randint(-100, -1)
if player_index > 0:
    player_index = -player_index

queue_bytes :bytes=[]

async def send_random_bytes():
    while True:
        await asyncio.sleep(1)
        int_value= random.randint(0, 100)
        bytes = struct.pack("<ii", player_index, int_value)
        queue_bytes.append(bytes)
        
class UDPListenerProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        print(f"Received {data} from {addr}")
        bytes_array = bytes(data)
        queue_bytes.append(bytes_array)

async def listen_to_udp():
    udp_ip = "127.0.0.1"
    udp_port = 3615
    loop = asyncio.get_event_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPListenerProtocol(),
        local_addr=(udp_ip, udp_port)
    )

    print(f"Listening for UDP packets on {udp_ip}:{udp_port}")

    try:
        while True:
            await asyncio.sleep(3600)  # Keep the listener running
    except asyncio.CancelledError:
        transport.close()
    
            
            
async def push_queue_to_wss():
    uri = "wss://193.150.14.47:3717"
    while True:
        try:
            async with websockets.connect(uri, ssl=ssl_context, ping_interval=20, ping_timeout=300) as websocket:
                while True:
                    while len(queue_bytes) > 0:
                        b : bytes = queue_bytes.pop(0)
                        await websocket.send(b)
                        print(f"Sent: {b}")
                    await asyncio.sleep(0.001)
        except (websockets.ConnectionClosed, websockets.InvalidURI, websockets.InvalidHandshake, ssl.SSLError) as e:
            print(f"Connection lost due to {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(asyncio.gather(
        send_random_bytes(),
        listen_to_udp(),
        push_queue_to_wss()
    ))
    asyncio.get_event_loop().run_forever()
    
    