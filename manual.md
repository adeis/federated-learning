# Panduan Pengujian Manual API Agregator Federated Learning

Dokumen ini berisi panduan untuk melakukan pengujian API pada server agregator pusat (`server_agregator.py`) secara mandiri menggunakan `curl`.

---

## 1. Menjalankan Server
Pastikan Server FastAPI telah aktif pada alamat `127.0.0.1:8000` dengan menjalankan shortcut script:
```bash
./run_server.sh
```

---

## 2. Langkah-Langkah Pengujian

### Langkah 1: Mengunduh Model Global (`GET /unduh-model-global`)
Klien melakukan panggilan ke endpoint ini untuk mengunduh bobot model global terbaru dalam bentuk terenkripsi.

Jalankan perintah berikut pada terminal baru:
```bash
curl -X GET http://127.0.0.1:8000/unduh-model-global
```

**Respon JSON yang diharapkan:**
```json
{
  "data_terenkripsi": "gAAAAAB...",
  "round_server_saat_ini": 1
}
```
*Salin (Copy) string acak dari `"data_terenkripsi"` di atas untuk digunakan pada pengujian berikutnya.*

---

### Langkah 2: Mengunggah Bobot Klien Pertama (`POST /update-bobot` - Node 1)
Mengirimkan bobot terenkripsi dari `Node_Manual_1` untuk ronde yang sedang aktif (`1`).

Jalankan perintah berikut (ganti `<SALIN_STRING_TERENKRIPSI>` dengan data dari Langkah 1):
```bash
curl -X POST http://127.0.0.1:8000/update-bobot \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "Node_Manual_1",
    "round_number": 1,
    "data_terenkripsi": "<SALIN_STRING_TERENKRIPSI>"
  }'
```

**Respon JSON yang diharapkan:**
```json
{
  "status": "success",
  "message": "Bobot berhasil diunggah dan diverifikasi"
}
```

---

### Langkah 3: Memicu Agregasi FedAvg (`POST /update-bobot` - Node 2)
Karena server dikonfigurasi untuk `TARGET_KLIEN_PER_ROUND = 2`, kita harus mengirimkan pembaruan kedua dari node yang berbeda agar FedAvg terpicu.

Jalankan perintah berikut (ganti `<SALIN_STRING_TERENKRIPSI>` dengan data dari Langkah 1):
```bash
curl -X POST http://127.0.0.1:8000/update-bobot \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "Node_Manual_2",
    "round_number": 1,
    "data_terenkripsi": "<SALIN_STRING_TERENKRIPSI>"
  }'
```

**Perilaku Server yang diharapkan:**
- Respon JSON akan sukses seperti Langkah 2.
- Pada log terminal tempat server berjalan, Anda akan melihat pesan agregasi FedAvg dan kenaikan putaran:
  ```text
  [SERVER] Berhasil menerima dan mendekripsi bobot dari Node_Manual_2 untuk putaran 1.
  [SERVER] Memicu agregasi FedAvg untuk putaran 1...
  [SERVER] Model global berhasil diperbarui untuk putaran 1.
  [SERVER] Putaran server kini berpindah ke ronde 2.
  ```

---

### Langkah 4: Verifikasi Perpindahan Ronde
Lakukan panggilan `GET` sekali lagi untuk memastikan ronde server telah berpindah ke ronde `2`:
```bash
curl -X GET http://127.0.0.1:8000/unduh-model-global
```

**Respon JSON yang diharapkan:**
```json
{
  "data_terenkripsi": "...",
  "round_server_saat_ini": 2
}
```
---

## 3. Pengujian Otomatis (Automated Testing)
Untuk melakukan pengujian alur Federated Learning secara penuh (3 ronde) secara otomatis tanpa intervensi manual, Anda dapat menggunakan orkestrator yang disediakan.

### Langkah Eksekusi:
Cukup jalankan perintah shortcut script dari root direktori proyek Anda:
```bash
./run.sh
```

### Alur Kerja Otomatis:
1. **Inisialisasi Server:** Meluncurkan FastAPI server agregator pada latar belakang (background).
2. **Sinkronisasi Jaringan:** Memberikan jeda 3 detik agar server siap menerima koneksi.
3. **Menyalakan Node Klien:** Meluncurkan secara paralel `Node_1` dan `Node_2` menggunakan subprocess.
4. **Eksekusi 3 Ronde:** Klien secara dinamis mengunduh model, menambahkan derau (noise), mengenkripsi, mengirimkan bobot, dan berlanjut ke ronde berikutnya setelah agregasi FedAvg server berhasil.
5. **Penyimpanan Hasil:** Setelah Ronde 3 selesai, server akan menyimpan model global final sebagai `model_global_final.pt` menggunakan `torch.save()`.
6. **Pembersihan Port:** Menghentikan proses server FastAPI secara aman untuk membebaskan port 8000.

### Kriteria Kelulusan (Success Criteria):
Sistem dianggap sukses jika output terminal berakhir dengan:
```text
[CLIENT_2] [Node_2] Alur federated learning selesai dengan sukses!
[CLIENT_1] [Node_1] Alur federated learning selesai dengan sukses!
[ORCHESTRATOR] Klien 1 selesai dengan kode keluar: 0
[ORCHESTRATOR] Klien 2 selesai dengan kode keluar: 0
[ORCHESTRATOR] Menghentikan Server Agregator secara aman...
[ORCHESTRATOR] Seluruh simulasi selesai.
```
Dan berkas biner `model_global_final.pt` tercipta di direktori `tgps-federated-learning/`.
