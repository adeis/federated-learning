import sys
import time
import requests
import json
import torch
import torch.nn as nn
from cryptography.fernet import Fernet

# 1. Parameterisasi input
if len(sys.argv) < 2:
    print("[ERROR] Gunakan: python klien_node_loop.py <NODE_ID>", file=sys.stderr)
    sys.exit(1)

NODE_ID = sys.argv[1]
print(f"[{NODE_ID}] Memulai node klien...", flush=True)

# 2. Keamanan TGPS: Kunci statis yang sama dengan server
FERNET_KEY = b'U5M1X_H4_M2_Ch1P_L4pt0p_41r_Str0ng_Key_1234='
cipher = Fernet(FERNET_KEY)

# Konfigurasi Lingkungan: Apple Silicon MPS / CPU
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"[{NODE_ID}] Menggunakan perangkat: {device}", flush=True)

# Inisialisasi struktur model linear yang sama dengan server (768 input, 2 output)
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(768, 5)
    def forward(self, x):
        return self.linear(x)

model = SimpleModel().to(device)

SERVER_URL = "http://127.0.0.1:8000"

# 3. Logika Putaran Otomatis (Ronde 1 sampai 3)
for r in range(1, 4):
    print(f"[{NODE_ID}] --- Memulai Putaran {r} ---", flush=True)
    
    # Mekanisme Polling (Sinkronisasi Ronde)
    encrypted_model_data = None
    while True:
        try:
            response = requests.get(f"{SERVER_URL}/unduh-model-global", timeout=5)
            if response.status_code == 200:
                data = response.json()
                server_round = data.get("round_server_saat_ini")
                
                # Loop penahanan dilewati hanya jika ronde server cocok dengan ronde r klien
                if server_round == r:
                    print(f"[{NODE_ID}] Cocok! Ronde server: {server_round}. Keluar dari antrean polling.", flush=True)
                    encrypted_model_data = data.get("data_terenkripsi")
                    break
                else:
                    print(f"[{NODE_ID}] Polling... Ronde server ({server_round}) belum cocok dengan ronde klien ({r}). Menunggu...", flush=True)
            else:
                print(f"[{NODE_ID}] Gagal mengunduh model. Status code: {response.status_code}. Mencoba lagi...", flush=True)
        except Exception as e:
            print(f"[{NODE_ID}] Gagal menghubungi server: {str(e)}. Mencoba lagi...", flush=True)
        
        time.sleep(2)
        
    # Penerapan Model Global
    try:
        # Dekripsi menggunakan Fernet
        decrypted_bytes = cipher.decrypt(encrypted_model_data.encode('utf-8'))
        decrypted_str = decrypted_bytes.decode('utf-8')
        state_dict_raw = json.loads(decrypted_str)
        
        # Rekonstruksi menjadi Tensor PyTorch dan arahkan ke perangkat akselerator
        state_dict = {k: torch.tensor(v, dtype=torch.float32).to(device) for k, v in state_dict_raw.items()}
        model.load_state_dict(state_dict)
        print(f"[{NODE_ID}] Model global berhasil dimuat ke lokal.", flush=True)
    except Exception as e:
        print(f"[{NODE_ID}] Gagal memuat model global: {str(e)}", file=sys.stderr, flush=True)
        sys.exit(1)
        
    # Simulasi Pelatihan Lokal
    # Tambahkan gangguan matriks kecil berbasis torch.randn
    print(f"[{NODE_ID}] Menjalankan simulasi pelatihan lokal...", flush=True)
    #with torch.no_grad():
    #    for param in model.parameters():
    #        # Generate noise pada device yang sama
    #        noise = torch.randn(param.size(), device=device) * 0.01
    #        param.add_(noise)
    #        
    # Ekstraksi & Proteksi TGPS
    # =========================================================================
    # PROSES PELATIHAN NYATA: EMBEDDING NOMIC LOKAL + DATA CSV SENSITIF
    # =========================================================================
    print(f"[{NODE_ID}] Membaca data_mentah.csv dan melakukan embedding lokal via Nomic...", flush=True)
    
    import pandas as pd
    import torch.optim as optim

    OLLAMA_URL = "http://localhost:11434/api/embeddings"

    try:
        # 1. Muat berkas CSV lokal
        df_lokal = pd.read_csv("data_mentah.csv")
        daftar_teks = df_lokal['data_sensitif'].tolist()
        
        # ✅ LOGIKA PELABELAN OTOMATIS:
        # 1. BUAT TEKS ACUAN UNTUK MASING-MASING KELAS DIAGNOSIS
        teks_acuan = {
            0: "Fungsi ginjal sehat bagus normal ureum rendah",
            1: "Gagal ginjal akut akut kidney injury kerusakan ginjal mendadak ureum tinggi",
            2: "Hiperkolesterolemia kolesterol tinggi lemak darah tinggi",
            3: "Diabetes melitus kencing manis gula darah tinggi"
        }
        
        # 2. EKSTRAKSI VEKTOR ACUAN VIA OLLAMA (Dapatkan Vektor Template)
        vektor_acuan = {}
        for kelas, teks_pemicu in teks_acuan.items():
            res_acuan = requests.post(OLLAMA_URL, json={"model": "nomic-embed-text", "prompt": teks_pemicu}, timeout=10)
            if res_acuan.status_code == 200:
                vektor_acuan[kelas] = torch.tensor(res_acuan.json()["embedding"]).to(device)
        
        # 3. EKSTRAKSI VEKTOR DATA MEDIS PASIEN ASLI & HITUNG KEMIRIPANNYA
        vektor_list = []
        daftar_label = []
        
        print(f"[{NODE_ID}] Memproses embedding dan pelabelan otonom untuk {len(daftar_teks)} pasien...", flush=True)
        for teks in daftar_teks:
            res_pasien = requests.post(OLLAMA_URL, json={"model": "nomic-embed-text", "prompt": teks}, timeout=10)
            if res_pasien.status_code == 200:
                v_pasien = torch.tensor(res_pasien.json()["embedding"]).to(device)
                vektor_list.append(v_pasien.cpu().numpy().tolist()) # Simpan untuk input training
                
                # Hitung Cosine Similarity antara data pasien dengan 4 Kelas Acuan
                skor_kemiripan = {}
                for kelas, v_template in vektor_acuan.items():
                    # Rumus Cosine Similarity di PyTorch
                    cos_sim = torch.dot(v_pasien, v_template) / (torch.norm(v_pasien) * torch.norm(v_template))
                    skor_kemiripan[kelas] = cos_sim.item()
                
                # Pilih kelas yang memiliki nilai kemiripan makna tertinggi (Argmax)
                kelas_paling_mirip = max(skor_kemiripan, key=skor_kemiripan.get)
                daftar_label.append(kelas_paling_mirip)
                
        # 4. KONVERSI KE TENSOR UNTUK PELATIHAN MODEL FL
        inputs = torch.tensor(vektor_list, dtype=torch.float32).to(device)
        targets = torch.tensor(daftar_label, dtype=torch.long).to(device)
        
        # 5. JALANKAN PELATIHAN MODEL LINIER (Input: 768, Output: 4)
        print(f"[{NODE_ID}] Menjalankan pelatihan model 4 kelas hasil pelabelan vektor...", flush=True)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=0.1)
        
        model.train()
        for epoch in range(15):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
        print(f"[{NODE_ID}] Pelatihan data CSV selesai. Loss Akhir: {loss.item():.4f}", flush=True)
        
    except Exception as e:
        print(f"[{NODE_ID}] Gagal memproses pelabelan vektor: {str(e)}", file=sys.stderr, flush=True)
        sys.exit(1)
        
    except Exception as e:
        print(f"[{NODE_ID}] Gagal memproses data CSV atau embedding: {str(e)}", file=sys.stderr, flush=True)
        sys.exit(1)
    # ===================================================================
    try:
        # Wajib memindahkan tensor dari memori akselerator (mps/cuda) ke CPU
        local_state_dict = model.state_dict()
        serializable_state = {k: v.cpu().tolist() for k, v in local_state_dict.items()}
        
        # Ubah menjadi list array angka biasa, ubah ke string JSON, dan enkripsi
        json_str = json.dumps(serializable_state)
        encrypted_bytes = cipher.encrypt(json_str.encode('utf-8'))
        encrypted_str = encrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"[{NODE_ID}] Gagal mengekstrak dan mengenkripsi model lokal: {str(e)}", file=sys.stderr, flush=True)
        sys.exit(1)
        
    # Pengunggahan
    uploaded = False
    while not uploaded:
        try:
            payload = {
                "node_id": NODE_ID,
                "round_number": r,
                "data_terenkripsi": encrypted_str
            }
            response = requests.post(f"{SERVER_URL}/update-bobot", json=payload, timeout=5)
            if response.status_code == 200:
                print(f"[{NODE_ID}] Berhasil mengunggah bobot terenkripsi untuk putaran {r}.", flush=True)
                uploaded = True
            else:
                print(f"[{NODE_ID}] Gagal mengunggah bobot. Server merespon: {response.text}. Mencoba lagi...", flush=True)
                time.sleep(2)
        except Exception as e:
            print(f"[{NODE_ID}] Gagal mengunggah bobot karena gangguan jaringan: {str(e)}. Mencoba lagi...", flush=True)
            time.sleep(2)

print(f"[{NODE_ID}] Alur federated learning selesai dengan sukses!", flush=True)
