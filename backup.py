import os
import shutil
import asyncio
from datetime import datetime

DATA_FILE = "data.json"
BACKUP_FOLDER = "backups"
BACKUP_INTERVAL = 300  # secondi (5 minuti)
MAX_BACKUPS = 20


def cleanup_backups():
    """Mantiene solo gli ultimi MAX_BACKUPS file."""
    try:
        files = sorted(
            [f for f in os.listdir(BACKUP_FOLDER) if f.startswith("backup_")]
        )
        while len(files) > MAX_BACKUPS:
            oldest = files.pop(0)
            os.remove(os.path.join(BACKUP_FOLDER, oldest))
    except Exception as e:
        print("[BACKUP] Errore cleanup:", e)


async def auto_backup(bot):
    """Esegue backup automatici finché il bot è attivo."""
    await bot.wait_until_ready()

    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    while not bot.is_closed():
        try:
            if os.path.exists(DATA_FILE):
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_name = os.path.join(
                    BACKUP_FOLDER, f"backup_{timestamp}.json"
                )
                shutil.copy(DATA_FILE, backup_name)
                cleanup_backups()
                print(f"[BACKUP] Creato: {backup_name}")
            else:
                print("[BACKUP] data.json non trovato")
        except Exception as e:
            print("[BACKUP] Errore:", e)

        await asyncio.sleep(BACKUP_INTERVAL)
