import socket
import threading
import time

# Fungsi untuk klien meminta file ke server dan mencatat metrik
def client_request(server_host, server_port, filename, client_id, results):
    try:
        start_connect = time.time()  # Waktu mulai koneksi
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_host, server_port))  # Koneksi ke server
            latency = time.time() - start_connect  # Hitung latensi

            s.sendall(f"GET:{filename}".encode())  # Kirim permintaan GET

            # Menerima file dan menghitung throughput
            start_download = time.time()
            total_bytes = 0

            with open(f"downloaded_{client_id}_{filename}", 'wb') as f:
                print(f"[Client-{client_id}] Receiving '{filename}' from server...")
                while True:
                    data = s.recv(1024)  # Terima data
                    if not data:
                        break
                    f.write(data)
                    total_bytes += len(data)

            end_download = time.time()
            response_time = end_download - start_connect  # Waktu respons
            download_time = end_download - start_download  # Waktu unduhan
            throughput = (total_bytes / 1024) / download_time  # KB/s

            # Simpan hasil dalam dictionary
            results[client_id] = {
                "latency": latency,
                "response_time": response_time,
                "throughput": throughput,
                "total_bytes": total_bytes / 1024  # Simpan dalam KB
            }

        print(f"[Client-{client_id}] File '{filename}' downloaded successfully.")
    except ConnectionRefusedError:
        print(f"[Client-{client_id}] Cannot connect to server at {server_host}:{server_port}.")
    except TimeoutError:
        print(f"[Client-{client_id}] Connection to server timed out.")

# Fungsi untuk mensimulasikan banyak klien menyerang server secara bersamaan
def simulate_clients(num_clients, server_host, server_port, filename):
    threads = []
    results = {}  # Dictionary untuk menyimpan hasil setiap klien

    # Membuat dan menjalankan thread untuk setiap klien
    for i in range(num_clients):
        t = threading.Thread(
            target=client_request, 
            args=(server_host, server_port, filename, i + 1, results), 
            name=f"Client-{i + 1}"
        )
        threads.append(t)
        t.start()
        time.sleep(0.05)  # Jeda singkat agar permintaan datang hampir bersamaan

    # Menunggu semua thread selesai
    for t in threads:
        t.join()

    print(f"All {num_clients} clients have finished downloading.")
    print_summary(results)  # Cetak rangkuman hasil

# Fungsi untuk mencetak rangkuman hasil
def print_summary(results):
    total_latency = sum(result["latency"] for result in results.values())
    total_response_time = sum(result["response_time"] for result in results.values())
    total_throughput = sum(result["throughput"] for result in results.values())
    total_data = sum(result["total_bytes"] for result in results.values())

    avg_latency = total_latency / len(results)
    avg_response_time = total_response_time / len(results)
    avg_throughput = total_throughput / len(results)

    print("\n--- Summary ---")
    print(f"Total Latency: {total_latency:.4f} seconds")
    print(f"Average Latency: {avg_latency:.4f} seconds")
    print(f"Total Response Time: {total_response_time:.4f} seconds")
    print(f"Average Response Time: {avg_response_time:.4f} seconds")
    print(f"Total Throughput: {total_throughput:.2f} KB/s")
    print(f"Average Throughput: {avg_throughput:.2f} KB/s")
    print(f"Total Data Transferred: {total_data:.2f} KB")
    print("----------------")

# Fungsi utama
if __name__ == "__main__":
    # IP dan port server
    server_host = input("Enter server IP (e.g., 10.2.55.187): ").strip()
    server_port = int(input("Enter server port (e.g., 5002): ").strip())

    # Input jumlah klien dan nama file
    num_clients = int(input("Enter number of clients (e.g., 5, 10, 20): "))
    filename = input("Enter filename to download: ").strip()

    # Mulai simulasi
    simulate_clients(num_clients, server_host, server_port, filename)
