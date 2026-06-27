# Product Requirement Document (PRD) & Auto-Execution Blueprint
## Project: Automated Federated Learning with TrustGuard Privacy Shield (TGPS)
## Environment Target: Apple Silicon (MacBook Air M2 / MPS Optimized)

---

## 1. Project Overview & Objective
Dokumen ini berisi instruksi spesifikasi mutlak untuk membangun, mengonfigurasi, dan menguji sistem purwarupa Federated Learning (FL) terautomasi yang dilengkapi dengan simulasi privasi TrustGuard Privacy Shield (TGPS). 

Sistem harus berjalan secara otonom dalam satu kali eksekusi perintah (Single-Command Execution). Sistem melatih model kecerdasan buatan secara lokal pada perangkat klien menggunakan akselerasi GPU Apple Silicon (MPS), mengekstrak bobot model menjadi format JSON, mengamankannya dengan enkripsi simetris Fernet, dan mengirimkannya ke server pusat untuk digabungkan menggunakan algoritma Federated Averaging (FedAvg) dalam 3 ronde otomatis.

---

## 2. Environment Setup & Dependency Instructions
Agentic AI wajib memastikan lingkungan pengujian siap dengan membuat file penyiapan atau mengeksekusi perintah instalasi pustaka berikut secara otomatis:

- **Runtime Environment:** Python 3.10 atau versi di atasnya.
- **Perintah Instalasi Dependensi:**
  ```bash
  pip install fastapi uvicorn torch cryptography requests
  ```

---

## 3. Project File Structure
Agentic AI harus menghasilkan struktur file proyek sebagai berikut di dalam direktori kerja:
```text
⚙️ tgps-federated-learning/
├── server_agregator.py      # Aplikasi Server FastAPI (Agregator)
├── klien_node_loop.py       # Skrip Klien Tunggal Parametrik
└── run_simulation.py        # Skrip Utama Orkestrator (Auto-Launcher)
```

---

## 4. Component Technical Specifications

### Component 1: Server Agregator Pusat (`server_agregator.py`)
Agentic AI harus membangun server web berbasis FastAPI dengan ketentuan logika berikut:
1. **Keamanan TGPS:** Inisialisasi pengunci kriptografi Fernet menggunakan kunci statis: `b'U5M1X_H4_M2_Ch1P_L4pt0p_41r_Str0ng_Key_1234='`.
2. **State Management:** Setel `TARGET_KLIEN_PER_ROUND = 2`, `putaran_saat_ini = 1`, dan kamus penyimpanan memori `gudang_bobot_node = {}`.
3. **Inisialisasi Model Global:** Buat struktur arsitektur model dasar (Linear Layer: 10 input, 2 output) berisikan angka acak bawaan.
4. **Endpoint `POST /update-bobot`:**
   - Menerima payload JSON: `node_id` (string), `round_number` (integer), dan `data_terenkripsi` (string).
   - Validasi nomor ronde. Jika `round_number != putaran_saat_ini`, kembalikan Error HTTP 400.
   - Dekripsi `data_terenkripsi` menggunakan Fernet, konversi kembali dari string JSON menjadi bentuk Python dictionary numerik.
   - Rekonstruksi array tersebut menjadi objek Tensor PyTorch dan simpan ke dalam `gudang_bobot_node[node_id]`.
   - Jika jumlah entri unik di dalam `gudang_bobot_node` mencapai `TARGET_KLIEN_PER_ROUND`, jalankan fungsi **FedAvg**:
     - Hitung rata-rata matematika dari setiap matriks tensor untuk semua layer yang tersedia.
     - Perbarui model global utama dengan nilai rata-rata baru tersebut.
     - Kosongkan isi `gudang_bobot_node` dan naikkan nilai variabel `putaran_saat_ini` sebesar 1 angka.
5. **Endpoint `GET /unduh-model-global`:**
   - Menyediakan data model global terbaru untuk diunduh klien.
   - Konversi tensor model global saat ini menjadi array list angka biasa (pindahkan dari memori akselerator ke CPU terlebih dahulu), ubah ke string JSON, enkripsi menggunakan kunci Fernet, lalu kembalikan dalam bentuk payload terenkripsi bersama nilai integer `round_server_saat_ini`.

### Component 2: Skrip Klien Tunggal Parametrik (`klien_node_loop.py`)
Agentic AI harus membangun skrip klien dinamis yang menerima argumen baris perintah (`sys.argv`) untuk menentukan identitasnya, dengan spesifikasi logika sebagai berikut:
1. **Parameterisasi input:** Skrip harus membaca argumen baris perintah pertama sebagai `NODE_ID` (Contoh: `python klien_node_loop.py Node_1`).
2. **Konfigurasi Lingkungan:** Atur perangkat komputasi PyTorch secara eksplisit ke `"mps"` (jika tersedia akselerasi Apple Silicon) atau jatuh kembali ke `"cpu"`. Inisialisasi struktur model linear yang sama dengan server (10 input, 2 output).
3. **Logika Putaran Otomatis (Looping Ronde $r$ dari 1 sampai 3):**
   - **Mekanisme Polling (Sinkronisasi Ronde):** Lakukan pemanggilan `GET /unduh-model-global` secara berulang setiap 2 detik. Loop penahanan ini hanya boleh dilewati jika nilai ronde yang dilaporkan server sudah cocok dengan ronde $r$ klien.
   - **Penerapan Model Global:** Unduh payload model terenkripsi, dekripsi dengan kunci Fernet yang sama, rekonstruksi menjadi Tensor PyTorch, arahkan memori objek ke perangkat akselerator (`mps`), lalu muat bobot tersebut ke model lokal menggunakan metode `load_state_dict`.
   - **Simulasi Pelatihan Lokal:** Lakukan modifikasi bobot dan bias model secara acak (tambahkan gangguan matriks kecil berbasis `torch.randn`) untuk mensimulasikan proses latihan lokal tanpa membutuhkan file dataset eksternal.
   - **Ekstraksi & Proteksi TGPS:** Ekstrak bobot model lokal terbaru. Wajib memindahkan tensor dari memori `"mps"` ke `"cpu"`, ubah menjadi list array angka biasa, ubah ke string JSON, dan enkripsi menggunakan kunci Fernet.
   - **Pengunggahan:** Kirim hasil enkripsi ke endpoint `POST /update-bobot` server bersama data `node_id` dan nilai ronde $r$ saat ini.

---

## 5. Automated Orchestrator Script (`run_simulation.py`)
Untuk memastikan pengujian berjalan langsung tanpa intervensi manual dari pengguna, Agentic AI **wajib membuat sebuah skrip launcher utama** menggunakan modul `subprocess` dan `time` Python dengan urutan alur kerja otomatis sebagai berikut:

1. **Inisialisasi Server:** Jalankan file `server_agregator.py` sebagai proses latar belakang (*background process*).
2. **Jeda Waktu Jaringan:** Berikan jeda tidur (*sleep*) selama 3 detik untuk memastikan server FastAPI telah sepenuhnya aktif mendengarkan port jaringan `127.0.0.1:8000`.
3. **Penyalaan Node Klien Serentak:** 
   - Jalankan proses sub-proses baru untuk Klien Pertama: `python klien_node_loop.py Node_1`.
   - Jalankan proses sub-proses baru untuk Klien Kedua: `python klien_node_loop.py Node_2`.
4. **Pemantauan Status & Terminasi:** 
   - Pantau keluaran (*output stream logs*) dari semua sub-proses dan cetak ke terminal utama pengguna.
   - Tunggu hingga kedua skrip klien menyelesaikan seluruh loop pelatihan 3 ronde dan keluar dengan status sukses.
   - Setelah simulasi selesai, matikan proses server FastAPI secara aman untuk membebaskan port jaringan.

---

## 6. Validation & Success Criteria for Execution
Sistem dinyatakan sukses lulus uji secara otonom jika:
- Skrip `run_simulation.py` dapat dipanggil langsung dan mengeksekusi seluruh rangkaian skrip di atas tanpa menghasilkan galat (*zero-error code execution*).
- Server berhasil mendeteksi kontribusi terenkripsi dari `Node_1` dan `Node_2`, memicu kalkulasi agregasi FedAvg otomatis pada ronde 1, 2, dan 3, serta menutup seluruh proses secara bersih setelah tujuan simulasi tercapai.

- Setelah nilai `putaran_saat_ini` mencapai ronde akhir (Ronde 3) dan FedAvg selesai, wajib simpan objek tensor `model_global_saat_ini` menjadi file biner fisik lokal bernama 'model_global_final.pt' menggunakan fungsi bawaan `torch.save()`.
