import os
import subprocess
from datetime import datetime

# -----------------------------
# CONFIGURAZIONE
# -----------------------------
REPO_PATH = r"C:\Users\Thomas\Desktop\Lavoro_050325\1) Progetti In Corso\Prova_Software_APV"
COMMIT_MESSAGE = f"Aggiornamento app {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
REQUIREMENTS_FILE = "requirements.txt"

# -----------------------------
# FUNZIONE DI ESECUZIONE COMANDI
# -----------------------------
def run_command(cmd, cwd=None):
    """Esegue un comando shell e stampa l'output."""
    print(f"Eseguo: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"❌ Errore:\n{result.stderr}")
        raise Exception(f"Comando fallito: {' '.join(cmd)}")
    print(result.stdout)

# -----------------------------
# 0️⃣ Aggiorna pip e installa pipreqs
# -----------------------------
print("➡️ Aggiornamento pip e installazione pipreqs...")
run_command(["python", "-m", "pip", "install", "--upgrade", "pip"])
run_command(["pip", "install", "pipreqs"])

# -----------------------------
# 1️⃣ Genera requirements.txt automaticamente con pipreqs
# -----------------------------
print("➡️ Generazione automatica di requirements.txt con pipreqs...")
run_command(["pipreqs", ".", "--force", "--encoding=utf-8"], cwd=REPO_PATH)
print("✅ requirements.txt generato automaticamente in base alle importazioni effettive.")

# -----------------------------
# 2️⃣ Controlla modifiche git
# -----------------------------
print("➡️ Verifica modifiche locali...")
result = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_PATH, text=True, capture_output=True)
if result.stdout.strip() == "":
    print("✅ Nessuna modifica da commit. Streamlit Cloud rimarrà aggiornato.")
else:
    # -----------------------------
    # 3️⃣ Git add, commit e push
    # -----------------------------
    print("➡️ Aggiornamento repository Git...")
    run_command(["git", "add", "."], cwd=REPO_PATH)
    run_command(["git", "commit", "-m", COMMIT_MESSAGE], cwd=REPO_PATH)
    run_command(["git", "push"], cwd=REPO_PATH)
    print("✅ Repository aggiornato su GitHub!")

# -----------------------------
# 4️⃣ Deploy su Streamlit Cloud
# -----------------------------
print("➡️ Deploy su Streamlit Cloud completato!")
print("ℹ️ Streamlit Cloud aggiornerà automaticamente l'app dal repository GitHub.")
print("✅ Processo di deploy completato con successo.")