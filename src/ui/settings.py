import customtkinter as ctk
from src.utils.config import config
from src.utils.i18n import i18n
from src.core.pac_manager import PACManager

class SettingsFrame(ctk.CTkFrame):
    """
    Frame delle impostazioni (Lingua, Modalità, Whitelist).
    """
    def __init__(self, master, pac_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.pac_manager = pac_manager
        
        # Titolo
        lbl_title = ctk.CTkLabel(self, text=i18n.t("SETTINGS"), font=("Arial", 20, "bold"))
        lbl_title.pack(pady=20)

        # Creazione Tab
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tab_gen = self.tabview.add(i18n.t("TAB_GENERAL"))
        self.tab_wl = self.tabview.add(i18n.t("TAB_WHITELIST"))

        self._init_general_tab()
        self._init_whitelist_tab()

    def _init_general_tab(self):
        # Rimossi elementi spostati in Sidebar
        lbl_info = ctk.CTkLabel(self.tab_gen, text="Le impostazioni principali sono ora nella Sidebar.", text_color="gray")
        lbl_info.pack(pady=50)

    def _init_whitelist_tab(self):
        # Lista Domini
        self.txt_domains = ctk.CTkTextbox(self.tab_wl, height=250)
        self.txt_domains.pack(fill="x", padx=10, pady=10)
        
        current_wl = config.get("whitelist") or []
        self.txt_domains.insert("0.0", "\n".join(current_wl))
        
        lbl_info = ctk.CTkLabel(self.tab_wl, text="Inserisci un dominio per riga (es. google.com)", text_color="gray")
        lbl_info.pack()

        # Pulsante Salva Whitelist
        btn_save_wl = ctk.CTkButton(self.tab_wl, text=i18n.t("BTN_SAVE"), command=self.save_whitelist)
        btn_save_wl.pack(pady=20)

    def save_general(self):
        # Salva Lingua
        selected_lang_name = self.combo_lang.get()
        new_lang_code = self.reverse_lang_map.get(selected_lang_name, "it")
        config.set("language", new_lang_code)
        
        # Feedback visivo semplice
        if self.master.master: # App instance
             ctk.CTkLabel(self.tab_gen, text=i18n.t("SAVED"), text_color="green").pack()

    def save_whitelist(self):
        raw_text = self.txt_domains.get("1.0", "end")
        domains = [line.strip() for line in raw_text.split("\n") if line.strip()]
        
        config.set("whitelist", domains)
        self.pac_manager.update_whitelist(domains)
        
        if self.master.master:
             ctk.CTkLabel(self.tab_wl, text=i18n.t("SAVED"), text_color="green").pack()

    def select_whitelist_tab(self):
        """Passa al tab Whitelist."""
        self.tabview.set(i18n.t("TAB_WHITELIST"))
