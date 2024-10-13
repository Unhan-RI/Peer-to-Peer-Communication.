# Pengujian P2P dengan flooding menggunakan Stress tools
# p2p_node.py 
Kode ini mengimplementasikan jaringan P2P sederhana. Node dalam jaringan dapat berfungsi sebagai klien dan server. Salah satu fitur utama kode ini adalah pencarian file menggunakan metode flooding, di mana permintaan pencarian dikirim ke semua peer.

Bagian Flooding (search_file function)
Berikut adalah kode untuk fungsi flooding :

    def search_file(filename):
     for peer in PEERS:
        try:
        
           with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
           
                s.connect(peer)
                s.sendall(f'SEARCH:{filename}'.encode())
                response = s.recv(1024).decode()
                
                if response.startswith('FOUND'):
                    print(f'File {filename} found at {peer}')
                    return peer

        except ConnectionRefusedError:
            print(f'Cannot connect to {peer}')

    print(f'File {filename} not found in the network.')
    return None

Pada kode di atas, setiap node mengirim permintaan pencarian ke seluruh peer dalam daftar PEERS. Jika file ditemukan, proses pencarian berhenti dan node yang memiliki file tersebut dikembalikan. Jika tidak ditemukan, pencarian terus berjalan hingga semua peer diperiksa.
# p2p_stress tools.py - Pengujian Jaringan dengan Stress Tool
Setelah jaringan P2P diimplementasikan menggunakan metode flooding, kinerja jaringan dapat diuji menggunakan kode stress tool. Kode ini mensimulasikan banyak klien yang mengunduh file dari server secara bersamaan untuk mengukur metrik seperti latensi, throughput, dan waktu respons.

# Simulasi Pengujian Jaringan
Fungsi utama untuk simulasi klien adalah sebagai berikut:

    def simulate_clients(num_clients, server_host, server_port, filename):
    threads = []
    results = {}

    for i in range(num_clients):
        t = threading.Thread(target=client_request, args=(server_host, server_port, filename, i + 1, results))
        threads.append(t)
        t.start()
        time.sleep(0.05)

    for t in threads:
        t.join()

    print(f'All {num_clients} clients have finished downloading.')
    print_summary(results)

Kode di atas menciptakan beberapa thread untuk mensimulasikan banyak klien yang mengunduh file dari server secara bersamaan. Ini berguna untuk mengevaluasi seberapa baik jaringan P2P dapat menangani beban tinggi dengan banyak permintaan.





