import os
import subprocess
from datetime import datetime

# -----------------------------
# CONFIGURAZIONE
# -----------------------------
REPO_PATH = r"C:\Users\Thomas\Desktop\Lavoro_050325\1) Progetti In Corso\Prova_Software_APV"
COMMIT_MESSAGE = f"Aggiornamento app {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
REQUIREMENTS_FILE = "requirements.txt"

# Librerie essenziali per Streamlit app
ESSENTIAL_LIBS = [
    "streamlit",
    "pandas",
    "numpy",
    "Pillow",
    "rich",
    "markdown-it-py",
    "mdurl",
    "pygments"
]

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
# 1️⃣ Leggi pip freeze
# -----------------------------
print("➡️ Lettura delle librerie installate...")
result = subprocess.run(["pip", "freeze"], text=True, capture_output=True)
if result.returncode != 0:
    raise Exception("Errore durante pip freeze:\n" + result.stderr)

installed_packages = result.stdout.strip().split("\n")

# -----------------------------
# 2️⃣ Filtra solo librerie essenziali
# -----------------------------
filtered_packages = []
for pkg in installed_packages:
    name = pkg.split("==")[0].lower()
    if name in [lib.lower() for lib in ESSENTIAL_LIBS]:
        filtered_packages.append(pkg)

# -----------------------------
# 3️⃣ Scrivi requirements.txt
# -----------------------------
requirements_path = os.path.join(REPO_PATH, REQUIREMENTS_FILE)
print(f"➡️ Scrittura di {REQUIREMENTS_FILE}...")
with open(requirements_path, "w") as f:
    f.write("\n".join(filtered_packages))
print(f"✅ {REQUIREMENTS_FILE} generato con librerie essenziali.")

# -----------------------------
# 4️⃣ Controlla modifiche git
# -----------------------------
print("➡️ Verifica modifiche locali...")
result = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_PATH, text=True, capture_output=True)
if result.stdout.strip() == "":
    print("✅ Nessuna modifica da commit. Streamlit Cloud rimarrà aggiornato.")
else:
    # -----------------------------
    # 5️⃣ Git add, commit e push
    # -----------------------------
    print("➡️ Aggiornamento repository Git...")
    run_command(["git", "add", "."], cwd=REPO_PATH)
    run_command(["git", "commit", "-m", COMMIT_MESSAGE], cwd=REPO_PATH)
    run_command(["git", "push"], cwd=REPO_PATH)
    print("✅ Repository aggiornato su GitHub!")

# -----------------------------
# 6️⃣ Deploy su Streamlit Cloud
# -----------------------------
print("➡️ Deploy su Streamlit Cloud completato!")
print("Nota: Streamlit Cloud aggiornerà automaticamente l'app dal repository GitHub.")
