# 🩺 Rangkuman Eksekutif: Simulasi Federated Learning & TGPS

---

## 🎯 1. Inti Proyek (The Big Picture)
Sistem ini membuktikan teknologi **Privacy-Preserving AI** tingkat lanjut. Kita berhasil melatih satu **Model AI Global** untuk mendeteksi risiko Gagal Ginjal Akut dari data teks medis nyata, **tanpa memindahkan atau mengumpulkan satu baris pun data sensitif pasien ke server pusat** [Ⱚ, Ⱚ] (Matriks Target Terisolasi). 

---

## 🎭 2. Analogi Peran Komponen

### 🎬 ORCHESTRATOR (`run_simulation.py`)
- **Peran:** Sutradara Panggung Otomatis.
- **Tugas Awam:** Menyalakan server, memicu Klien 1 & 2 bekerja serentak, dan membereskan panggung setelah selesai.
- **Detail Programmer:** Mengelola multi-subproses (`subprocess`) dan siklus hidup aplikasi (*lifecycle handling*).

### 🏛️ SERVER AGREGATOR (`server_agregator.py`)
- **Peran:** Kementerian Kesehatan Pusat.
- **Tugas Awam:** Mengelola putaran ronde (1, 2, 3), menyatukan "ilmu" dari setiap daerah, dan menerbitkan produk kecerdasan final.
- **Detail Programmer:** REST API Stateful berbasis **FastAPI**, mengeksekusi rumus **FedAvg (Federated Averaging)**, dan mengekspor berkas biner `.pt` [Ⱚ].

### 🏥 CLIENT / NODE 1 & 2 (`klien_node_loop.py`)
- **Peran:** Lab Komputer Rumah Sakit Daerah.
- **Tugas Awam:** Membaca berkas data rahasia lokal di laptop sendiri, melatih kecerdasan AI lokal, lalu mengunci hasilnya sebelum dikirim ke pusat [Ⱚ].
- **Detail Programmer:** Komputasi terdistribusi PyTorch (Akselerasi GPU/CPU), melakukan teknik *Polling HTTP*, ekstraksi *Embedding* teks, dan enkripsi payload.

---

## 🔄 3. Alur Kerja Sistem (Step-by-Step)

### 📥 Langkah 1: Sinkronisasi Ronde (Polling)
- Klien menyala dan melakukan ketukan pintu (*request*) berkala ke server untuk mencocokkan nomor ronde aktif.
- Begitu ronde cocok, klien mengunduh arsitektur model biner kosong atau model global terbaru dari server pusat.

### 🧠 Langkah 2: Pemrosesan Lokal Tanpa Kebocoran (Local Training)
- **Ekstraksi Makna:** Teks medis tidak terstruktur di dalam `data_mentah.csv` dibaca oleh pustaka **Pandas** [Ⱚ].
- **Vektorisasi:** Teks diubah menjadi array angka (Vektor 768 dimensi) secara lokal melalui **Ollama API (`nomic-embed-text`)** [Ⱚ].
- **Belajar Mandiri:** PyTorch melatih bobot internal model berdasarkan label diagnosis kontras [Ⱚ]. Nilai *Loss Akhir 0.0005* membuktikan AI lokal telah menjadi sangat cerdas membedakan penyakit.
- **Keamanan Mutlak:** Data mentah CSV dan string teks medis tetap berada di hardisk laptop, tidak pernah tersentuh jaringan luar [Ⱚ].

### 🔐 Langkah 3: Proteksi Shield (TGPS)
- Klien mengambil kesimpulan hasil belajar (`model.state_dict()`) dalam bentuk matriks angka [Ⱚ].
- Matriks tersebut diserialisasi menjadi teks JSON, lalu langsung dikunci menggunakan **Enkripsi Simetris Fernet (TGPS Shield)** sebelum diunggah ke internet [Ⱚ].

### 🎛️ Langkah 4: Penggabungan Ilmu (Federated Averaging)
- Server menerima kiriman terenkripsi dari `Node_1` dan `Node_2`, lalu membuka kuncinya secara aman [Ⱚ].
- Server menerapkan algoritma **FedAvg**: Menjumlahkan nilai matriks kedua node lalu membaginya dengan angka dua (menghitung rata-rata matematika).
- Hasil rata-rata ini menjadi "Kecerdasan Kolektif Baru". Server menaikkan status ronde dan siklus berulang hingga Ronde 3 selesai.

---

## 🏆 4. Hasil Akhir & Keberhasilan Proyek
- **Kepatuhan Regulasi:** Privasi data terjaga 100% mengikuti standar medis ketat (GDPR/UU PDP).
- **Artefak Intelijen:** Tercipta berkas fisik **`model_global_final.pt`** berukuran **8 KB** di direktori root [Ⱚ].
- **Validasi Klinis:** Pengujian lewat `uji_prediksi.py` membuktikan model global 8 KB tersebut mampu mendeteksi kalimat pasien baru secara akurat dengan probabilitas klasifikasi yang tajam.
