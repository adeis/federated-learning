import torch
import torch.nn as nn
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.fernet import Fernet
import threading

app = FastAPI()

# 1. Keamanan TGPS: Kunci statis
FERNET_KEY = b'U5M1X_H4_M2_Ch1P_L4pt0p_41r_Str0ng_Key_1234='
cipher = Fernet(FERNET_KEY)

# 2. Inisialisasi Model Global (Linear Layer: 10 input, 2 output)
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(768, 5)
    
    def forward(self, x):
        return self.linear(x)

global_model = SimpleModel()
state_lock = threading.Lock()

# 3. State Management
TARGET_KLIEN_PER_ROUND = 2
putaran_saat_ini = 1
gudang_bobot_node = {}  # {node_id: state_dict}

class UpdatePayload(BaseModel):
    node_id: str
    round_number: int
    data_terenkripsi: str

@app.post("/update-bobot")
async def update_bobot(payload: UpdatePayload):
    global putaran_saat_ini, gudang_bobot_node
    
    with state_lock:
        # Validasi nomor ronde
        if payload.round_number != putaran_saat_ini:
            raise HTTPException(
                status_code=400, 
                detail=f"Putaran tidak cocok. Server berada pada putaran {putaran_saat_ini}, klien mengirim untuk putaran {payload.round_number}."
            )
        
        try:
            # Dekripsi data_terenkripsi menggunakan Fernet
            decrypted_bytes = cipher.decrypt(payload.data_terenkripsi.encode('utf-8'))
            decrypted_str = decrypted_bytes.decode('utf-8')
            state_dict_raw = json.loads(decrypted_str)
            
            # Rekonstruksi array tersebut menjadi objek Tensor PyTorch
            node_state_dict = {}
            for k, v in state_dict_raw.items():
                node_state_dict[k] = torch.tensor(v, dtype=torch.float32)
                
            gudang_bobot_node[payload.node_id] = node_state_dict
            print(f"[SERVER] Berhasil menerima dan mendekripsi bobot dari {payload.node_id} untuk putaran {payload.round_number}.", flush=True)
            
            # Jika jumlah entri unik mencapai TARGET_KLIEN_PER_ROUND, jalankan FedAvg
            if len(gudang_bobot_node) >= TARGET_KLIEN_PER_ROUND:
                print(f"[SERVER] Memicu agregasi FedAvg untuk putaran {putaran_saat_ini}...", flush=True)
                
                # Hitung rata-rata matematika dari setiap matriks tensor untuk semua layer
                averaged_state_dict = {}
                keys = global_model.state_dict().keys()
                
                for key in keys:
                    tensors = [node_state[key] for node_state in gudang_bobot_node.values()]
                    averaged_state_dict[key] = torch.stack(tensors).mean(dim=0)
                
                # Perbarui model global utama
                global_model.load_state_dict(averaged_state_dict)
                print(f"[SERVER] Model global berhasil diperbarui untuk putaran {putaran_saat_ini}.", flush=True)
                
                # Simpan model global jika mencapai ronde akhir (Ronde 3)
                if putaran_saat_ini == 3:
                    torch.save(global_model.state_dict(), "model_global_final.pt")
                    print("[SERVER] Berhasil menyimpan model global final ke 'model_global_final.pt'", flush=True)
                
                # Kosongkan isi gudang_bobot_node dan naikkan putaran_saat_ini sebesar 1
                gudang_bobot_node.clear()
                putaran_saat_ini += 1
                print(f"[SERVER] Putaran server kini berpindah ke ronde {putaran_saat_ini}.", flush=True)
                
            return {"status": "success", "message": "Bobot berhasil diunggah dan diverifikasi"}
            
        except Exception as e:
            print(f"[SERVER] Gagal mendekripsi atau memproses bobot dari {payload.node_id}: {str(e)}", flush=True)
            raise HTTPException(status_code=400, detail=f"Gagal memproses payload: {str(e)}")

@app.get("/unduh-model-global")
async def unduh_model_global():
    with state_lock:
        try:
            # Sediakan data model global terbaru
            state_dict = global_model.state_dict()
            
            # Pindahkan dari memori akselerator ke CPU terlebih dahulu, ubah ke list array angka biasa
            serializable_state = {k: v.cpu().tolist() for k, v in state_dict.items()}
            
            # Ubah ke string JSON
            json_str = json.dumps(serializable_state)
            
            # Enkripsi menggunakan kunci Fernet
            encrypted_bytes = cipher.encrypt(json_str.encode('utf-8'))
            encrypted_str = encrypted_bytes.decode('utf-8')
            
            return {
                "data_terenkripsi": encrypted_str,
                "round_server_saat_ini": putaran_saat_ini
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gagal menyiapkan model global: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Jalankan server
    uvicorn.run("server_agregator:app", host="127.0.0.1", port=8000, log_level="warning")
