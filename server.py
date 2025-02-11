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

def split_file(file_path):
    """Splits file into chunks and assigns sequence numbers."""
    chunks = []
    with open(file_path, 'rb') as f:
        seq_num = 0
        while chunk := f.read(CHUNK_SIZE):
            chunks.append((seq_num, chunk))
            seq_num += 1
    return chunks

def start_server(host='0.0.0.0', port=12345):
    """Starts the file transfer server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    file_path = conn.recv(1024).decode()
    if not os.path.exists(file_path):
        conn.sendall(b"ERROR: File not found")
        conn.close()
        return

    print(f"Sending file: {file_path}")
    chunks = split_file(file_path)
    checksum = calculate_checksum(file_path)

    # Send total chunks count
    conn.sendall(str(len(chunks)).encode())
    conn.recv(1024)  # Wait for ACK

    # Send checksum
    conn.sendall(checksum.encode())
    conn.recv(1024)  # Wait for ACK

    # Send file chunks
    for seq_num, chunk in chunks:
        conn.sendall(f"{seq_num}:".encode() + chunk)
        conn.recv(1024)  # Wait for ACK

    print("File transfer complete.")
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
