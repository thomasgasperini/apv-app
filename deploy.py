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
        print(f"Errore:\n{result.stderr}")
        raise Exception(f"Comando fallito: {' '.join(cmd)}")
    print(result.stdout)

# -----------------------------
# 0️⃣ Aggiorna pip
# -----------------------------
print("➡️ Aggiornamento pip...")
run_command(["python", "-m", "pip", "install", "--upgrade", "pip"])

# -----------------------------
# 1️⃣ Genera requirements.txt aggiornato
# -----------------------------
print("➡️ Generazione requirements.txt...")
requirements_path = os.path.join(REPO_PATH, REQUIREMENTS_FILE)
with open(requirements_path, "w") as f:
    result = subprocess.run(["pip", "freeze"], text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Errore pip freeze:\n{result.stderr}")
        raise Exception("Impossibile generare requirements.txt")
    f.write(result.stdout)
print(f"✅ {REQUIREMENTS_FILE} aggiornato.")

# -----------------------------
# 2️⃣ Aggiorna le librerie nel virtual environment
# -----------------------------
print("➡️ Aggiornamento librerie...")
run_command(["pip", "install", "--upgrade", "-r", REQUIREMENTS_FILE])

# -----------------------------
# 3️⃣ Controlla se ci sono modifiche da commit
# -----------------------------
print("➡️ Verifica modifiche locali...")
result = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_PATH, text=True, capture_output=True)
if result.stdout.strip() == "":
    print("✅ Nessuna modifica da commit. Streamlit Cloud rimarrà aggiornato con l'ultima versione.")
else:
    # -----------------------------
    # 4️⃣ Git add, commit e push
    # -----------------------------
    print("➡️ Aggiornamento repository Git...")
    run_command(["git", "add", "."], cwd=REPO_PATH)
    run_command(["git", "commit", "-m", COMMIT_MESSAGE], cwd=REPO_PATH)
    run_command(["git", "push"], cwd=REPO_PATH)
    print("✅ Repository aggiornato su GitHub!")

# -----------------------------
# 5️⃣ Deploy su Streamlit Cloud
# -----------------------------
print("➡️ Deploy su Streamlit Cloud completato!")
print("Nota: Streamlit Cloud aggiornerà automaticamente l'app dal repository GitHub.")
