import subprocess
import time
import threading
import sys
import os

# Fungsi pembaca log secara real-time dari output stream sub-proses
def log_reader(pipe, prefix):
    try:
        for line in iter(pipe.readline, ''):
            if not line:
                break
            print(f"[{prefix}] {line.strip()}", flush=True)
    except Exception as e:
        print(f"[ORCHESTRATOR] Error saat membaca log {prefix}: {str(e)}", flush=True)
    finally:
        pipe.close()

def main():
    # Pastikan direktori kerja aktif adalah direktori skrip ini
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Menentukan Python executable dari virtual environment (jika ada)
    venv_python = os.path.abspath(os.path.join(script_dir, "..", "venv", "bin", "python"))
    if not os.path.exists(venv_python):
        # Fallback ke executable Python saat ini
        venv_python = sys.executable
    
    print(f"[ORCHESTRATOR] Menggunakan Python executable: {venv_python}", flush=True)

    # 1. Inisialisasi Server Agregator
    print("[ORCHESTRATOR] Memulai Server Agregator (FastAPI)...", flush=True)
    server_proc = subprocess.Popen(
        [venv_python, "server_agregator.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Jalankan background thread pembaca log server
    threading.Thread(target=log_reader, args=(server_proc.stdout, "SERVER"), daemon=True).start()

    # 2. Jeda Waktu Jaringan (Sleep 3 detik)
    print("[ORCHESTRATOR] Menunggu 3 detik agar server aktif...", flush=True)
    time.sleep(3)

    # 3. Penyalaan Node Klien Serentak
    print("[ORCHESTRATOR] Memulai Klien Node_1...", flush=True)
    client1_proc = subprocess.Popen(
        [venv_python, "klien_node_loop.py", "Node_1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    threading.Thread(target=log_reader, args=(client1_proc.stdout, "CLIENT_1"), daemon=True).start()

    print("[ORCHESTRATOR] Memulai Klien Node_2...", flush=True)
    client2_proc = subprocess.Popen(
        [venv_python, "klien_node_loop.py", "Node_2"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    threading.Thread(target=log_reader, args=(client2_proc.stdout, "CLIENT_2"), daemon=True).start()

    # 4. Pemantauan Status & Terminasi
    print("[ORCHESTRATOR] Menunggu seluruh proses klien selesai...", flush=True)
    
    c1_code = client1_proc.wait()
    c2_code = client2_proc.wait()
    
    print(f"[ORCHESTRATOR] Klien 1 selesai dengan kode keluar: {c1_code}", flush=True)
    print(f"[ORCHESTRATOR] Klien 2 selesai dengan kode keluar: {c2_code}", flush=True)

    # Mematikan proses server FastAPI secara aman
    print("[ORCHESTRATOR] Menghentikan Server Agregator secara aman...", flush=True)
    server_proc.terminate()
    try:
        server_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print("[ORCHESTRATOR] Server tidak merespon penghentian, memaksa keluar (SIGKILL)...", flush=True)
        server_proc.kill()
        
    print("[ORCHESTRATOR] Seluruh simulasi selesai.", flush=True)
    
    # Keluar dengan kode kesalahan jika ada klien yang gagal
    if c1_code != 0 or c2_code != 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
