from PIL import Image
import customtkinter as ctk
import os

class Assets:
    """
    Gestore centralizzato delle risorse grafiche (Icone, Bandiere).
    Carica le immagini una sola volta e le restituisce come CTkImage.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Assets, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.images = {}
        
        # Percorsi base
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.assets_dir = os.path.join(self.base_dir, "assets", "img")
        self.flags_dir = os.path.join(self.assets_dir, "flags")
        self.icons_dir = os.path.join(self.assets_dir, "icons")
        
    def load_image(self, name, category="icons", size=(24, 24)):
        """Carica un'immagine e la cachea."""
        key = f"{category}_{name}_{size}"
        if key in self.images:
            return self.images[key]
            
        try:
            folder = self.flags_dir if category == "flags" else self.icons_dir
            path = os.path.join(folder, f"{name}.png")
            
            if not os.path.exists(path):
                print(f"⚠️ EXIT: Asset non trovato: {path}")
                return None
                
            img = Image.open(path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            self.images[key] = ctk_img
            return ctk_img
        except Exception as e:
            print(f"❌ ERRORE caricamento asset {name}: {e}")
            return None

    def get_flag(self, country_code, size=(30, 30)):
        """Restituisce l'immagine della bandiera."""
        return self.load_image(f"flag_{country_code.lower()}", category="flags", size=size)
        
    def get_icon(self, name, size=(24, 24)):
        """Restituisce un'icona di sistema."""
        return self.load_image(f"icon_{name}", category="icons", size=size)
        
    def get_status_icon(self, status, size=(24, 24)):
        """Restituisce l'icona di stato (on, off, wl)."""
        return self.load_image(f"status_{status.lower()}", category="icons", size=size)

assets = Assets()
