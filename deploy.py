import os
import subprocess
from datetime import datetime

REPO_PATH = r"C:\Users\Thomas\Desktop\Lavoro_251125\1) Progetti In Corso\Prova_Software_APV"

def run_command(cmd, cwd=None):
    """Esegue un comando shell e stampa l'output."""
    print(f"Eseguo: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"❌ Errore:\n{result.stderr}")
        raise Exception(f"Comando fallito: {' '.join(cmd)}")
    print("✅ Comando eseguito con successo")
    return result

# 1. Genera requirements.txt
print("➡️ Generazione requirements.txt...")
run_command(["pipreqs", ".", "--force", "--encoding=utf-8"], cwd=REPO_PATH)

# 2. Controlla e push modifiche
print("➡️ Verifica modifiche...")
result = run_command(["git", "status", "--porcelain"], cwd=REPO_PATH)

if result.stdout.strip():
    commit_msg = f"Aggiornamento app {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run_command(["git", "add", "."], cwd=REPO_PATH)
    run_command(["git", "commit", "-m", commit_msg], cwd=REPO_PATH)
    run_command(["git", "push"], cwd=REPO_PATH)
    print("✅ Repository aggiornato su GitHub!")
else:
    print("✅ Nessuna modifica da commitare")

print("🎉 Deploy completato! Streamlit Cloud si aggiornerà automaticamente.")