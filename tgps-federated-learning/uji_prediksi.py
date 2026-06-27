import torch
import torch.nn as nn
import requests
import os

# 1. Konfigurasi Lingkungan M2
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f" Menggunakan perangkat untuk pengujian: {device}")

# 2. Definisikan Struktur Model yang Sama Sesuai Arsitektur 768
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(768, 5)
    def forward(self, x):
        return self.linear(x)

# Inisialisasi model kosong dan muat bobot hasil gabungan FL (8 KB)
model = SimpleModel().to(device)
try:
    folder_sekarang = os.path.dirname(os.path.abspath(__file__))
    path_file_pt = os.path.join(folder_sekarang, "model_global_final.pt")
    bobot_global = torch.load(path_file_pt, map_location=device)
    model.load_state_dict(bobot_global)
    model.eval()  # Setel model ke mode evaluasi/prediksi
    print(" Berhasil memuat model_global_final.pt (8 KB) ke dalam memori.")
except Exception as e:
    print(f" Gagal memuat file .pt: {str(e)}")
    exit(1)

# 3. Simulasi Input Data Rekam Medis Baru yang Belum Pernah Dilihat AI
print("\n=======================================================")
print("  SISTEM DIKONEKSIKAN: DIAGNOSIS KLINIS OTOMATIS TGPS  ")
print("=======================================================")
print("Contoh format teks input bebas:")
print(" - Nama: Anto, Ureum: 22.4 mg/dL")
print(" - Nama: Budi, Gula Darah Sewaktu: 280 mg/dL")
print(" - Kondisi Renal Optimal")
print("-------------------------------------------------------")

# Meminta input teks medis dari terminal pengguna
input_pengguna = input("Masukkan teks rekam medis pasien (Tekan ENTER untuk data default):\n> ")

# Data default jika input dari pengguna kosong
TEKS_DEFAULT = "Nama: Budi,  Ureum: 104.8 mg/dL"

if input_pengguna.strip() == "":
    teks_pasien = TEKS_DEFAULT
    print(f"\n[INFO] Menggunakan data default: '{teks_pasien}'")
else:
    teks_pasien = input_pengguna
    print(f"\n[INFO] Memproses data input Anda: '{teks_pasien}'")

# 4. Ubah teks pasien baru menjadi Vektor 768 via Ollama Lokal
print(" Melakukan embedding teks pasien via Ollama Nomic...")
try:
    res = requests.post("http://localhost:11434/api/embeddings", json={
        "model": "nomic-embed-text",
        "prompt": teks_pasien
    }, timeout=5)
    
    if res.status_code == 200:
        vektor_input = res.json()["embedding"]
        # Konversi ke bentuk tensor dan kirim ke perangkat GPU M2
        tensor_input = torch.tensor([vektor_input], dtype=torch.float32).to(device)
        
        # 5. Jalankan Prediksi AI dengan Softmax (Mendukung 5 Kelas)
        with torch.no_grad():
            hasil_output = model(tensor_input)
            probabilitas = torch.softmax(hasil_output, dim=1).cpu().numpy()[0] # Ambil baris pertama
            
        print("\n=== HASIL PREDIKSI MODEL GLOBAL FINAL ===")
        print(f"Probabilitas Kelas 0 (Ginjal Bagus/Normal) : {probabilitas[0] * 100:.2f}%")
        print(f"Probabilitas Kelas 1 (Gagal Ginjal Akut)   : {probabilitas[1] * 100:.2f}%")
        print(f"Probabilitas Kelas 2 (Hiperkolesterolemia) : {probabilitas[2] * 100:.2f}%")
        print(f"Probabilitas Kelas 3 (Diabetes Melitus)    : {probabilitas[3] * 100:.2f}%")
        print(f"Probabilitas Kelas 4 (Kondisi Lain)        : {probabilitas[4] * 100:.2f}%")
        
        # Ekstrak indeks kelas dengan nilai probabilitas tertinggi
        kelas_tertinggi = torch.argmax(hasil_output, dim=1).item()
        
        # ✅ PERBAIKAN UTAMA: Pemetaan teks diagnosis harus tepat sesuai 5 indeks kelas
        list_diagnosis = [
            "✅ HASIL: Fungsi Ginjal Pasien Normal dan Bagus. Pertahankan pola hidup sehat!",
            "🚨 HASIL: Terdeteksi Risiko Gagal Ginjal Akut (Kondisi Kritis). Segera periksa ke dokter!",
            "⚠️ HASIL: Terdeteksi Risiko Hiperkolesterolemia (Kolesterol Tinggi). Perhatikan konsumsi lemak.",
            "⚠️ HASIL: Terdeteksi Risiko Diabetes Melitus (Gula Darah Tinggi). Kontrol konsumsi gula harian.",
            "⚪ HASIL: Kondisi Pasien Dinyatakan Normal / Masuk Kategori Risiko Umum Lainnya."
        ]
        
        print("\n=== KESIMPULAN DIAGNOSIS OTOMATIS TGPS ===")
        print(list_diagnosis[kelas_tertinggi])
        print("=======================================================")
        print("Model berhasil mengekstrak keputusan klinis terdistribusi!")
    else:
        print(f" Ollama bermasalah, status code: {res.status_code}")
except Exception as e:
    print(f" Gagal melakukan testing karena kendala teknis: {str(e)}")
