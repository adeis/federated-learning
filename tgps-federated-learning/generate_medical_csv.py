import pandas as pd
import random

def generate_medical_csv(total_data=1000):
    # 📌 Bank data variasi diagnosis klinis, termasuk kondisi ginjal yang sehat/bagus
    diagnosa_list = [
        # Kategori 0: Ginjal Bagus / Normal (Ureum sehat: 15.0 - 40.0)
        ("Fungsi Ginjal Normal", "Ureum", 15.0, 40.0, "mg/dL"),
        ("Ginjal Sehat dan Bagus", "Ureum", 18.0, 38.0, "mg/dL"),
        ("Kondisi Renal Optimal", "Ureum", 20.0, 35.0, "mg/dL"),
        
        # Kategori 1: Gagal Ginjal Akut / AKI (Ureum tinggi: > 50.0)
        ("Gagal Ginjal Akut", "Ureum", 55.0, 150.0, "mg/dL"),
        ("Acute Kidney Injury (AKI)", "Ureum", 60.0, 140.0, "mg/dL"),
        ("Kerusakan Ginjal Mendadak", "Ureum", 52.0, 130.0, "mg/dL"),
        
        # Kategori 2: Hiperkolesterolemia / Lemak Darah (Kolesterol tinggi: > 200.0)
        ("Hiperkolesterolemia", "Kolesterol Total", 205.0, 290.0, "mg/dL"),
        ("Kolesterol Tinggi", "Kolesterol Total", 210.0, 280.0, "mg/dL"),
        ("Hiperlipidemia / Lemak Darah Tinggi", "Kolesterol Total", 200.0, 270.0, "mg/dL"),
        
        # Kategori 3: Diabetes Melitus / Kencing Manis (Gula Darah Sewaktu tinggi: > 140.0)
        ("Diabetes Melitus", "Gula Darah Sewaktu", 150.0, 320.0, "mg/dL"),
        ("Kencing Manis", "Gula Darah Sewaktu", 145.0, 300.0, "mg/dL"),
        ("Hiperglikemia / Gula Darah Tinggi", "Gula Darah Sewaktu", 160.0, 280.0, "mg/dL")
    ]
    
    records = []
    for i in range(1, total_data + 1):
        # Memilih secara acak pola diagnosis di atas
        diag, komp, min_v, max_v, satuan = random.choice(diagnosa_list)
        
        # Menghasilkan nilai uji lab sesuai parameter penyakit
        nilai = round(random.uniform(min_v, max_v), 1)
        
        # Menyusun data teks tidak terstruktur (unstructured text)
        teks = f"Nama: Pasien_{i}, Diagnosis: {diag}, {komp}: {nilai} {satuan}"
        records.append({"id": i, "data_sensitif": teks})
        
    df = pd.DataFrame(records)
    df.to_csv("data_mentah.csv", index=False)
    print(f"✅ Berhasil meng-generate {total_data} data bervariasi (termasuk Ginjal Sehat) ke 'data_mentah.csv'")

# Silakan jalankan pembuatan 1000 data
generate_medical_csv(1000)
