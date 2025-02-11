import socket
import hashlib
import os

CHUNK_SIZE = 1024  # 1 KB

def calculate_checksum(file_path):
    """Computes SHA-256 checksum of the given file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()

def start_client(server_ip, port, file_path):
    """Starts the file transfer client."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    # Send file request
    client_socket.sendall(file_path.encode())

    # Receive total chunks count
    total_chunks = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"ACK")

    # Receive checksum
    expected_checksum = client_socket.recv(1024).decode()
    client_socket.sendall(b"ACK")

    # Receive file chunks
    received_chunks = {}
    for _ in range(total_chunks):
        data = client_socket.recv(1024 + 10)  # Extra space for seq_num
        seq_num, chunk = data.split(b":", 1)
        received_chunks[int(seq_num)] = chunk
        client_socket.sendall(b"ACK")

    # Reassemble file in correct order
    output_file = "received_" + os.path.basename(file_path)
    with open(output_file, 'wb') as f:
        for i in range(total_chunks):
            f.write(received_chunks[i])

    # Verify checksum
    received_checksum = calculate_checksum(output_file)
    if received_checksum == expected_checksum:
        print("✅ Transfer Successful! Checksum matched.")
    else:
        print("❌ Transfer Failed! Checksum mismatch.")

    client_socket.close()

if __name__ == "__main__":
    server_ip = "127.0.0.1"  # Change if server is on another machine
    port = 12345
    file_path = "sample.txt"  # Change to desired file

    start_client(server_ip, port, file_path)
