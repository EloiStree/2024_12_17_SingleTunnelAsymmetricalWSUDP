## Demo of how to use:
# https://github.com/EloiStree/2022_01_24_XOMI/tree/main/HowToUse



import asyncio
import struct
import websockets
import socket
import ssl
import requests
import uuid
import time
from web3 import Web3
import secrets
from eth_account.messages import encode_defunct
import tornado


## python /git/stream_game_tunnel_ws/RunServer.py

# Debian: /lib/systemd/system/stream_game_tunnel_ws.service
# Learn: https://youtu.be/nvx9jJhSELQ?t=279s

# sudo nano /lib/systemd/system/stream_game_tunnel_ws.service
"""
[Unit]
Description=Listen to all the given IID from the PI or the UDP outside if allowed.
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /git/stream_game_tunnel_ws/RunServer.py
Restart=always
User=root
WorkingDirectory=/git/stream_game_tunnel_ws

[Install]
WantedBy=multi-user.target
"""
#1h
# sudo nano /etc/systemd/system/stream_game_tunnel_ws.timer
"""
[Unit]
Description=Tunnel Auth time manager

[Timer]
OnBootSec=0min
OnUnitActiveSec=10s

[Install]
WantedBy=timers.target
"""
# Learn: https://youtu.be/nvx9jJhSELQ?t=368
# cd /lib/systemd/system/
# sudo systemctl daemon-reload
# sudo systemctl enable stream_game_tunnel_ws.service
# chmod +x /git/stream_game_tunnel_ws/RunServer.py
# sudo systemctl enable stream_game_tunnel_ws.service
# sudo systemctl start stream_game_tunnel_ws.service
# sudo systemctl status stream_game_tunnel_ws.service
# sudo systemctl stop stream_game_tunnel_ws.service
# sudo systemctl restart stream_game_tunnel_ws.service
# 
# sudo systemctl enable stream_game_tunnel_ws.timer
# sudo systemctl start stream_game_tunnel_ws.timer
#
# sudo systemctl list-timers | grep stream_game_tunnel_ws


"""
sudo systemctl stop stream_game_tunnel_ws.service
sudo systemctl stop stream_game_tunnel_ws.timer
"""

"""
sudo systemctl restart stream_game_tunnel_ws.service
sudo systemctl restart stream_game_tunnel_ws.timer

"""

"""
sudo systemctl list-timers | grep stream_game_tunnel_ws
"""

# openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem
path_ssh_certificat="/token/ssl_cert.pem"
path_ssh_private_key="/token/ssl_key.pem"
path_ssh_pfx="/token/ssl_window.pfx"


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile=path_ssh_certificat, keyfile=path_ssh_private_key)


# read and display part of the certificat for debug
with open(path_ssh_certificat, "r") as file:
    data = file.read()
    print(data[:50])

# read and display part of the private key for debug
with open(path_ssh_private_key, "r") as file:
    data = file.read()
    print(data[:50])

# Listen to any incoming UDP messages
LISTENER_UDP_IP = "0.0.0.0"
# Uncomment below to only allow the app on the Raspberry Pi
# LISTENER_UDP_IP = "127.0.0.1"
LISTENER_UDP_PORT = 3615
LISTENER_WEBSOCKET_PORT_WS = 3617
LISTENER_WEBSOCKET_PORT_WSS = 3717
bool_use_echo = True

SERVER_WS_PORT = 8765
bool_use_debug_print = True

# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
# -subj "/CN=193.150.14.47"

websocket_server_ip_ws="0.0.0.0"

bool_use_wss = True
#  https://193.150.14.47
websocket_server_ip_wss="wss://193.150.14.47:8765"
websocket_server_ip_wss="193.150.14.47"
websocket_server_ip_wss="0.0.0.0"
# IF SSL YOUR DOMAIn

# sudo netstat -tuln | grep 8765
# sudo ufw allow 8765/tcp
# sudo ufw status
# openssl s_client -connect 193.150.14.47:8765



allowed_public_addressses=["0x1Be31A94361a391bBaFB2a4CCd704F57dc04d4bb"]

clients = set()
only_negative_index_allowed=True

def debug_print(message):
    if bool_use_debug_print:
        print(message)

if bool_use_debug_print:
    print("PRINT IS DISABLE DON4T EXPECT PRINT.")


async def public_websocket_listener(listener_port ,ssl_given_context):
    """Listens for incoming WebSocket connections and relays messages to clients."""
    if ssl_given_context:   
        print(f"URL:", f"wss://{get_public_ip()}:{listener_port}")
    else:
        print(f"URL:", f"ws://{get_public_ip()}:{listener_port}")
    while True:
        try:
            async def echo(websocket, path):
                print (f"New WebSocket client connected: {websocket.remote_address} {path} ")
                try:
                    async for message in websocket:
                        int_length = len(message)
                        if int_length in {4, 8, 12, 16}:
                            await relay_to_clients(message)
                            if bool_use_echo:
                                    byte_message : bytes =message
                                    await websocket.send(byte_message)   
                        # else:
                        #     await websocket.send("Only messages of 4, 8, 12, or 16 characters are allowed")
                        #     await websocket.close()
                except Exception as e:
                    debug_print(f"Error in echo handler: {e}")
            if ssl_given_context:
                server = await websockets.serve(echo, websocket_server_ip_wss, listener_port,ssl=ssl_given_context)
            else:
                server = await websockets.serve(echo, websocket_server_ip_ws, listener_port)
            await server.wait_closed()
        except Exception as e:
            debug_print(f"Error in public_websocket_listener: {e}")
        await asyncio.sleep(4)  # Wait 4 seconds before trying again


async def udp_listener():

    print("Starting UDP Listener ", LISTENER_UDP_PORT)       
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




def is_message_signed_from_clipboard_text(given_message):
    """
    This function checks if the given message is signed by the given address.
    The format of the text must be as follows:
    message|address|signature
    """
    split_message = given_message.split("|")
    if len(split_message) < 3:
        return False
    message = split_message[0]
    address = split_message[1]
    signature = split_message[2]
    return is_message_signed_from_params(message, address, signature)


def is_message_signed_from_params(message, address, signature):
    """
    This function checks if the given message is signed by the given public address.
    """
    w3 = Web3()
    encoded_message = encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(encoded_message, signature=signature)
    return recovered_address.lower() == address.lower()

bool_refuse_message_over_16_bytes=True

def debug_data_as_iid(data):
    if len(data) == 4:
        integer = struct.unpack("<i", data)[0]
        debug_print(f"Received IID: {integer}")
    elif len(data) == 8:
        index, integer = struct.unpack("<ii", data)
        debug_print(f"Received IID: {index} - {integer}")
    elif len(data) == 12:
        integer, timestamp = struct.unpack("<iQ", data)
        debug_print(f"Received IID:  {integer} - {timestamp}")
    elif len(data) == 16:
        index, integer, timestamp= struct.unpack("<iiQ", data)
        debug_print(f"Received IID: {index} - {integer} - {timestamp} ")
        
        
def only_guest_id(data):
    if len(data) == 8:
        index, integer = struct.unpack("<ii", data)
        if integer < 0:
            return data
        else:
            return struct.pack("<ii", -index, integer)
    elif len(data) == 16:
        index, integer, timestamp= struct.unpack("<iiQ", data)
        if integer < 0:
            return data
        else:
            return struct.pack("<iiQ", -index, integer, timestamp)

async def relay_to_clients(data):
    if data is None or len(data) == 0:
        return
    if bool_refuse_message_over_16_bytes and len(data) > 16:
        debug_print(f"Message too long: {len(data)} bytes")
        return
    """Relays the given data to all connected WebSocket clients."""
    if not clients:
        debug_print("No clients connected to relay data.")
        return
    
    if only_negative_index_allowed:
        data=only_guest_id(data)
    
    disconnected_clients = set()
    for client in clients:
        try:
            if client and not client.closed:
                await client.send(data)

                debug_data_as_iid(data)
                debug_print(f"Sent {len(data)} bytes to client: {data}")
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

    bool_signed_received_and_validate = False
    try:
        # Send handshake GUID to the client
        handshake_guid = str(uuid.uuid4())
        await websocket.send(f"GUID:{handshake_guid}")
        debug_print(f"Sent handshake GUID to client: {handshake_guid}")

        # Listen for client messages
        async for message in websocket:
            if not bool_signed_received_and_validate and  message.startswith("SIGNED:"):
                debug_print(f"Received SIGNED message from client: {message}")
                message.strip()
                t = message[7:].split("|")
                if len(t) == 3:
                    message = t[0]
                    address = t[1]
                    signature = t[2]
                    if is_message_signed_from_params(message, address, signature):
                        bool_signed_received_and_validate=True
                        await websocket.send(f"HELLO {address}")
                        
                        if not(address in allowed_public_addressses):
                            await websocket.send(f"Client is not in the allowed list: {address}")
                            await websocket.close()
                        
                    else:
                        debug_print(f"Invalid signature from client: {address}")
                else:
                    debug_print(f"Invalid SIGNED message from client: {message}")
            else:
                if len(message) == 4 and message[0]=="p" and message[1]=="i" and message[2]=="n" and message[3]=="g":                    
                    await websocket.send("pong")
                    continue
                debug_print(f"Unknown message from client: {message}")
                if bool_signed_received_and_validate:
                    debug_print(f"KICK: {message}")
                    await websocket.send(f"Server don't allows message accept IID and SignIn. You have been kick out.")
                    await websocket.close()
           
    
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
        
        ws_public_task = asyncio.create_task(public_websocket_listener(listener_port=LISTENER_WEBSOCKET_PORT_WS , ssl_given_context =None))
        if bool_use_wss:
            wss_public_task = asyncio.create_task(public_websocket_listener(listener_port=LISTENER_WEBSOCKET_PORT_WSS ,ssl_given_context= ssl_context))
        ws_server = await websockets.serve(ws_handler, websocket_server_ip_wss, SERVER_WS_PORT,ssl=ssl_context)
        
        debug_print(f"WebSocket server running on ws://{get_public_ip()}:{SERVER_WS_PORT}")
        await asyncio.gather(udp_task,ws_public_task,wss_public_task, ws_server.wait_closed())
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
    debug_print(f"Starting WebSocket server on wss://{public_ip}:{SERVER_WS_PORT}")
    asyncio.run(main())
