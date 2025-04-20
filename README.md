

# 2024_12_17_SingleTunnelAsymmetricalWSUDP


```
pip install web3 websockets
```


This project uses **Ethereum** and **MetaMask** to establish a Python-based tunnel between a server and a client, with added protection and encryption. The main code is designed to facilitate secure communication over WebSocket UDP.

For an RSA-based version of a similar tunnel, see [2024_06_21_SingleTunnelRsaWSUDP](https://github.com/EloiStree/2024_06_21_SingleTunnelRsaWSUDP).

---

## Context and Purpose

My home internet bandwidth is both **limited** and **unstable**, which creates issues when implementing a **Twitch Play game concept**. To ensure a stable and consistent experience, I need to host the game(s) on a **Shadow Tech** (or an equivalent cloud service) machine with a high-speed fiber optic connection.

However, cloud gaming providers typically impose **network protection measures**, making direct connections challenging. To solve this, I require a reliable client-server connection with **online relays** to bypass these limitations.

---

## Technical Details

1. **Private Key Handling**:  
   - The Ethereum private key must be securely stored in a file on both the server and the client devices.  
   - An **Elliptic Curve Cryptography (ECC)** handshake is used to establish secure communication.

2. **Relay System**:  
   - Since small-town ISPs (like mine) do not provide the required **1 Gbps bandwidth**, the solution relies on **5-10 relays** to utilize the available bandwidth efficiently for a Twitch Play game.  
   - This helps mitigate network instability and balance the load across multiple connections.

3. **Performance Constraints**:  
   - While achieving 1 Gbps bandwidth is essential, other bottlenecks (such as CPU and GPU limitations) will also need to be addressed separately in the future.

---

## Use Case

If you simply need a secure **tunnel** between two computers for data transmission, this code can be useful. It is designed to prioritize security, reliability, and modularity in scenarios requiring consistent network performance.
