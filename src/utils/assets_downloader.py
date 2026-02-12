import os
import requests

# Base URL per Twemoji (CDN affidabile)
BASE_URL = "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/"

# Directory di destinazione
ASSETS_DIR = os.path.join("assets", "img")
FLAGS_DIR = os.path.join(ASSETS_DIR, "flags")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")

# Mappa Unicode -> Nome File
# Nota: La sintassi Twemoji è lowercase hex. Le bandiere sono composte da due codici regionali.
# IT: 1f1ee-1f1f9
# EN (GB): 1f1ec-1f1e7
# DE: 1f1e9-1f1ea
# FR: 1f1eb-1f1f7
# ES: 1f1ea-1f1f8

ASSETS = {
    # Bandiere
    "flag_it": {"code": "1f1ee-1f1f9", "category": "flags"},
    "flag_en": {"code": "1f1ec-1f1e7", "category": "flags"},
    "flag_de": {"code": "1f1e9-1f1ea", "category": "flags"},
    "flag_fr": {"code": "1f1eb-1f1f7", "category": "flags"},
    "flag_es": {"code": "1f1ea-1f1f8", "category": "flags"},
    
    # Icone Stato
    "status_on": {"code": "2705", "category": "icons"},      # ✅
    "status_off": {"code": "26d4", "category": "icons"},     # ⛔
    "status_wl": {"code": "1f6e1", "category": "icons"},     # 🛡️
    
    # Icone Pulsanti / UI
    "icon_settings": {"code": "2699", "category": "icons"},  # ⚙️
    "icon_edit": {"code": "270f", "category": "icons"},      # ✏️
    "icon_download": {"code": "1f4e5", "category": "icons"}, # 📥
    "icon_lock": {"code": "1f512", "category": "icons"},     # 🔒
    "icon_unlock": {"code": "1f513", "category": "icons"},   # 🔓
    
    # Extra (per sicurezza futura)
    "icon_check": {"code": "2714", "category": "icons"},     # ✔️
    "icon_cross": {"code": "274c", "category": "icons"},     # ❌
    "icon_warning": {"code": "26a0", "category": "icons"},   # ⚠️
}

def ensure_dirs():
    os.makedirs(FLAGS_DIR, exist_ok=True)
    os.makedirs(ICONS_DIR, exist_ok=True)
    print(f"Cartelle create: {FLAGS_DIR}, {ICONS_DIR}")

def download_asset(name, data):
    code = data["code"]
    category = data["category"]
    url = f"{BASE_URL}{code}.png"
    
    target_dir = FLAGS_DIR if category == "flags" else ICONS_DIR
    filename = f"{name}.png"
    filepath = os.path.join(target_dir, filename)
    
    if os.path.exists(filepath):
        print(f"Esiste già: {name}")
        return

    print(f"Scaricando {name} da {url}...")
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(r.content)
        print(f"Salvatato: {filepath}")
    except Exception as e:
        print(f"ERRORE scaricando {name}: {e}")

def main():
    ensure_dirs()
    print("Inizio download asset...")
    for name, data in ASSETS.items():
        download_asset(name, data)
    print("Fatto.")

if __name__ == "__main__":
    main()
