import socket
import threading
import os
import time

# Daftar peer di jaringan (sesuaikan dengan IP dan port yang tersedia)
PEERS = [('10.2.55.89', 5001), ('10.2.55.187', 5002)]

# Fungsi untuk memindai direktori dan subdirektori untuk mencari file
def scan_files(base_dir='.'):
    shared_files = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            shared_files[file] = file_path  # Simpan path absolut untuk setiap file
    return shared_files

# Fungsi untuk menjalankan server pada setiap node
def run_server(host, port, shared_files):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))  # Bind ke IP dan port node ini
    server_socket.listen(5)
    print(f"Node running as server on {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr, shared_files)).start()

# Fungsi untuk menangani permintaan dari client
def handle_client(conn, addr, shared_files):
    print(f"Connected by {addr}")
    data = conn.recv(1024).decode()
    command, filename = data.split(':')

    if command == "SEARCH":
        if filename in shared_files:
            conn.sendall(f"FOUND:{filename}".encode())
        else:
            conn.sendall("NOT_FOUND".encode())

    elif command == "GET":
        if filename in shared_files:
            with open(shared_files[filename], 'rb') as f:
                print(f"Sending file '{filename}' to {addr}")
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    conn.sendall(chunk)
            print(f"File '{filename}' sent to {addr}")
        else:
            conn.sendall("FILE_NOT_FOUND".encode())

    conn.close()

# Fungsi untuk mencari file dengan flooding ke semua peer
def search_file(filename):
    for peer in PEERS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(peer)
                s.sendall(f"SEARCH:{filename}".encode())
                response = s.recv(1024).decode()

                if response.startswith("FOUND"):
                    print(f"File '{filename}' found at {peer}")
                    return peer

        except ConnectionRefusedError:
            print(f"Cannot connect to {peer}")

    print(f"File '{filename}' not found in the network.")
    return None

# Fungsi untuk mengunduh file dari peer yang ditemukan
def get_file(peer, filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(peer)
        s.sendall(f"GET:{filename}".encode())

        with open(f"downloaded_{filename}", 'wb') as f:
            print(f"Receiving file '{filename}' from {peer}...")
            while True:
                data = s.recv(1024)
                if not data:
                    break
                f.write(data)

    print(f"File '{filename}' downloaded successfully.")

# Fungsi utama untuk menjalankan node
def run_node(host, port):
    shared_files = scan_files()  # Pindai file yang tersedia di direktori lokal

    threading.Thread(target=run_server, args=(host, port, shared_files)).start()

    time.sleep(1)  # Tunggu sebentar agar server siap menerima koneksi

    while True:
        command = input("Enter command (search <filename> / exit): ").strip()
        if command.startswith("search"):
            _, filename = command.split()
            peer = search_file(filename)
            if peer:
                get_file(peer, filename)
        elif command == "exit":
            break

# Jalankan node
if __name__ == "__main__":
    # Masukkan IP dan port dari node ini
    HOST = input("Enter this node's IP address (e.g., 10.2.55.89): ").strip()
    PORT = int(input("Enter this node's port (e.g., 5001): ").strip())

    run_node(HOST, PORT)
