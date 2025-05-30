import socket
import string
import random
import time
import struct

def random_bytes():
    return struct.pack("<ii", random.randint(0, 100), random.randint(0, 100))

def random_text(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def push_data(ip, port, data: bytes):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        print (f"Pushing data to {ip}:{port}| {data}")
        s.sendto(data, (ip, port))

while True:
    string_ddns_server= "apint.ddns.net"
    try:
        string_ipv4_server = socket.gethostbyname(string_ddns_server)
        print(f"Resolved {string_ddns_server} to {string_ipv4_server}")
    except socket.gaierror as e:
        print(f"Failed to resolve {string_ddns_server}: {e}")
        string_ipv4_server = "127.0.0.1"  # Fallback to localhost

    # Push eight random bytes to 127.0.0.1:3615
    data_bytes = random_bytes()
    push_data(string_ipv4_server, 3615, data_bytes)
    
    # Uncomment the following lines to push random text of 6 characters to 127.0.0.1:3614
    # data_text = random_text(6).encode('utf-8')
    # push_data('127.0.0.1', 3614, data_text)
    
    time.sleep(1)  # Sleep for a second to avoid overwhelming the server
