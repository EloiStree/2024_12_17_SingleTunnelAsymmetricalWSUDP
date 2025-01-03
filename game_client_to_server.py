import asyncio
from web3 import Web3
import secrets
from eth_account.messages import encode_defunct
import websockets
import socket
import os
import sys

# Look Like this 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdek
PRIVATE_KEY_ETH = ""
ADDRESS_ETH = ""

bool_display_udp_broadcast=True

private_key_path = "private_key.txt"

# uri =["ws://193.150.14.47:6777" ,"ws://81.240.94.97:433"]
uri= "ws://193.150.14.47:6777"
uri= "ws://81.240.94.97:433"



for i in range(1, len(sys.argv)):
    if sys.argv[i].startswith("ws://"):
        uri = sys.argv[i]


# check if file exists
if not os.path.exists(private_key_path):
    with open(private_key_path, "w") as file:
        private_key = secrets.token_hex(32)
        file.write(private_key)
        print(f"Private key file created at {private_key_path[5:]}")

# read the private key from the file
with open(private_key_path, "r") as file:
    PRIVATE_KEY_ETH = file.read().strip()
    print(f"Private key read from file: {PRIVATE_KEY_ETH[5:]}")


LOCAL_PORT =[3615,7000]


ENQUEUE_INTEGER_TO_DIFFUSE = list()



async def stack_bytes_array_to_diffuse(bytes_array):
    print(f"Stacking bytes: {bytes_array} Waiting:{len(ENQUEUE_INTEGER_TO_DIFFUSE)}")
    ENQUEUE_INTEGER_TO_DIFFUSE.append(bytes_array)





async def diffuse_received_bytes(data):
    print(f"Received bytes: {data}")
    for PORT in LOCAL_PORT:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.sendto(data, ('localhost', PORT))
            print(f"Sent bytes to local server on port {PORT}")
            s.close()
        except ConnectionRefusedError:
            print(f"Local server on port {PORT} is down")
            


async def sign_message_with_ethereum(message_to_sign: str):
    print(f"Signing message: {message_to_sign}")
    w3 = Web3()
    account = w3.eth.account.from_key(PRIVATE_KEY_ETH)
    # message_hash = w3.keccak(text=message_to_sign)
    encoded_message = encode_defunct(text=message_to_sign)
    signed_message = w3.eth.account.sign_message(encoded_message, private_key=PRIVATE_KEY_ETH)
    address= account.address
    signe_message_as_hex = signed_message.signature.hex()
    return f"{message_to_sign}|{address}|{signe_message_as_hex}"

async def connect_to_server(uri):
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    response = await websocket.recv()

                    # If the response is in bytes, forward it via UDP
                    if isinstance(response, bytes):
                        if bool_display_udp_broadcast:
                            print (f"Received Byte{len(response)}: {response}")
                            
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use SOCK_DGRAM for UDP
                        sock.sendto(response, ('127.0.0.1', 3615))
                        sock.close()
                    
                    # Handle text responses from the server
                    else:
                        print(f"Received text from server: {response}")

                        if response.startswith("GUID:"):
                            signed_response = await sign_message_with_ethereum(response[5:])
                            
                            print(f"SIGNED: {signed_response}")
                            await websocket.send("SIGNED:" + signed_response)

                        elif response.startswith("VALIDE"):
                            print("Server is verified")
                        
                        
        except websockets.exceptions.ConnectionClosedError  as e:

            print(f"Connection closed, retrying in 5 seconds... {e}")
            await asyncio.sleep(5)

        except Exception as e:
            print(f"An error occurred: {type(e).__name__} - {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)

# Assuming you call the function in your main asyncio event loop like this:
# asyncio.run(connect_to_server())

asyncio.get_event_loop().run_until_complete(connect_to_server(uri))

async def connect_multiple_clients():
    tasks = [connect_to_server() for _ in range(1)]
    await asyncio.gather(*tasks)

asyncio.get_event_loop().run_until_complete(connect_multiple_clients())
