import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.utils.config import config
from src.utils.i18n import i18n
from src.core.pac_manager import PACManager
from src.core.veyon_manager import veyon
from src.core.update_manager import UpdateManager # [NEW]
from src.utils.version import APP_VERSION, APP_AUTHOR, APP_LICENSE, APP_COPYRIGHT, APP_REPO
import webbrowser

class SettingsFrame(ctk.CTkFrame):
    """
    Frame delle impostazioni (Lingua, Modalità, Whitelist, Veyon).
    """
    def __init__(self, master, pac_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.pac_manager = pac_manager
        self.update_manager = UpdateManager() # [NEW] Istanza locale o passata? Meglio nuova tanto è leggera
        
        # Titolo
        lbl_title = ctk.CTkLabel(self, text=i18n.t("SETTINGS"), font=("Arial", 20, "bold"))
        lbl_title.pack(pady=20)

        # Creazione Tab
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 🎓 DIDATTICA: Il tab "Generali" è stato rimosso perché le impostazioni
        # sono state spostate nella sidebar per un accesso più rapido.
        self.tab_wl = self.tabview.add(i18n.t("TAB_WHITELIST"))
        self.tab_veyon = self.tabview.add("Veyon")
        self.tab_about = self.tabview.add(i18n.t("TAB_ABOUT"))

        self._init_whitelist_tab()
        self._init_veyon_tab()
        self._init_about_tab()

    def _init_about_tab(self):
        """Inizializza il tab 'About' con info versione e legali."""
        # Frame centrale per allineamento
        center_frame = ctk.CTkFrame(self.tab_about, fg_color="transparent")
        center_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Titolo App
        ctk.CTkLabel(center_frame, text="Lab Internet Control", font=("Arial", 24, "bold")).pack(pady=(10, 5))
        
        # Versione (Elegante, magari con badge style se possibile, qui testo semplice ma curato)
        ver_text = f"v{APP_VERSION}"
        ctk.CTkLabel(center_frame, text=ver_text, font=("Arial", 16), text_color="#3B8ED0").pack(pady=(0, 20))
        
        # Info Autore
        info_text = f"{i18n.t('LBL_AUTHOR')}: {APP_AUTHOR}\n{APP_COPYRIGHT}"
        ctk.CTkLabel(center_frame, text=info_text, text_color="gray80").pack(pady=5)
        
        # Licenza
        ctk.CTkLabel(center_frame, text=f"{i18n.t('LBL_LICENSE')}: {APP_LICENSE}", font=("Arial", 11)).pack(pady=5)
        
        # GitHub Link
        link_lbl = ctk.CTkLabel(center_frame, text="GitHub Repository", font=("Arial", 11, "underline"), text_color="#3B8ED0", cursor="hand2")
        link_lbl.pack(pady=5)
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open(APP_REPO))
        
        # [NEW] Pulsante Controllo Aggiornamenti Manuale
        self.btn_check_updates = ctk.CTkButton(center_frame, text="Controlla Aggiornamenti", command=self.manual_check_updates, width=150, height=25)
        self.btn_check_updates.pack(pady=(15, 5))
        
        # Separatore visivo (Linea)
        ctk.CTkFrame(center_frame, height=2, fg_color="gray40").pack(fill="x", pady=20, padx=40)
        
        # Note Legali (Scrollable se lunghe, o solo Label)
        ctk.CTkLabel(center_frame, text="Info Legali:", font=("Arial", 12, "bold")).pack(anchor="w", padx=40)
        
        legal_msg = i18n.t("LEGAL_NOTES")
        check_legal = ctk.CTkTextbox(center_frame, height=80, fg_color="transparent", text_color="gray70", wrap="word")
        check_legal.insert("0.0", legal_msg)
        check_legal.configure(state="disabled") # Read-only
        check_legal.pack(fill="x", padx=40, pady=5)

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

    def _init_veyon_tab(self):
        # Titolo Tab Veyon
        ctk.CTkLabel(self.tab_veyon, text="Gestione Lab e Postazioni (Veyon)", font=("Arial", 16, "bold")).pack(pady=15)

        # Frame Pulsanti per centrarli
        frame_actions = ctk.CTkFrame(self.tab_veyon, fg_color="transparent")
        frame_actions.pack(pady=20)

        # Pulsante Export
        btn_export = ctk.CTkButton(
            frame_actions, 
            text="Esporta CSV", 
            command=self.export_veyon_csv,
            fg_color="#3B8ED0", 
            hover_color="#36719F"
        )
        btn_export.pack(pady=10, fill="x")

        # [NEW] Pulsante Download Template (Esempio)
        btn_template = ctk.CTkButton(
            frame_actions, 
            text=i18n.t("BTN_DOWNLOAD_TEMPLATE"), 
            command=self.download_veyon_template,
            fg_color="transparent", 
            border_width=1
        )
        btn_template.pack(pady=10, fill="x")

        # Pulsante Import
        btn_import = ctk.CTkButton(
            frame_actions, 
            text="Importa CSV", 
            command=self.import_veyon_csv,
            fg_color="#E0a526", 
            hover_color="#D09516", 
            text_color="black"
        )
        btn_import.pack(pady=10, fill="x")

        # Help Text
        msg = (
            "NOTA: L'importazione permette di caricare un elenco di PC da un file CSV.\n"
            "Il formato atteso è quello standard di export di Veyon.\n"
            "Sarà possibile scegliere se sovrascrivere l'attuale configurazione."
        )
        ctk.CTkLabel(self.tab_veyon, text=msg, text_color="gray70", justify="center").pack(pady=20)


    def save_whitelist(self):
        raw_text = self.txt_domains.get("1.0", "end")
        domains = [line.strip() for line in raw_text.split("\n") if line.strip()]
        
        config.set("whitelist", domains)
        self.pac_manager.update_whitelist(domains)
        
        if self.master.master:
             ctk.CTkLabel(self.tab_wl, text=i18n.t("SAVED"), text_color="green").pack()

    def has_unsaved_changes(self):
        """Verifica se ci sono modifiche pendenti nella textbox della Whitelist."""
        # 1. Recupera contenuto textbox (pulito)
        raw_text = self.txt_domains.get("1.0", "end")
        current_domains = [line.strip() for line in raw_text.split("\n") if line.strip()]
        
        # 2. Recupera config salvata
        saved_domains = config.get("whitelist") or []
        
        # 3. Confronta (ordinando per sicurezza, anche se l'ordine utente conta... 
        # ma config load/save preserva ordine. Confrontiamo le liste dirette.)
        return current_domains != saved_domains

    def select_whitelist_tab(self):
        """Passa al tab Whitelist."""
        self.tabview.set(i18n.t("TAB_WHITELIST"))

    def export_veyon_csv(self):
        """Handler per esportare la configurazione."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Esporta Configurazione Veyon"
        )
        if not file_path:
            return

        success, msg = veyon.export_csv(file_path)
        if success:
            messagebox.showinfo("Export Veyon", msg)
        else:
            messagebox.showerror("Errore Export", msg)

    def import_veyon_csv(self):
        """Handler per importare la configurazione."""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Importa Configurazione Veyon"
        )
        if not file_path:
            return

        # Chiedi se cancellare esistente
        answer = messagebox.askyesno(
            "Import Veyon", 
            "Vuoi cancellare TUTTA la configurazione attuale del laboratorio prima di importare?\n\n"
            "SÌ: Cancella tutto e importa (Consigliato per ripristino).\n"
            "NO: Aggiungi/Aggiorna i PC dal file."
        )
        
        success, msg = veyon.import_csv(file_path, clear_existing=answer)
        
        if success:
            messagebox.showinfo("Import Veyon", msg)
        else:
            messagebox.showerror("Errore Import", msg)

    def download_veyon_template(self):
        """Handler per scaricare un file CSV di esempio."""
        # 🎓 DIDATTICA: Proponiamo il Desktop come cartella di default per comodità utente.
        import os
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        
        file_path = filedialog.asksaveasfilename(
            initialdir=desktop,
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Salva Esempio CSV",
            initialfile="esempio_pc_laboratorio.csv"
        )
        if not file_path:
            return

        success, msg = veyon.get_template_csv(file_path)
        if success:
            messagebox.showinfo("Template CSV", i18n.t("MSG_TEMPLATE_SAVED"))
        else:
            messagebox.showerror("Errore", msg)

    def manual_check_updates(self):
        """Controlla aggiornamenti su richiesta utente (No Popup)."""
        self.btn_check_updates.configure(state="disabled", text="Controllo in corso...")
        
        import threading
        def _check():
            has_update, tag, url = self.update_manager.check_for_updates()
            self.after(0, lambda: self._post_manual_check(has_update, tag, url))
            
        threading.Thread(target=_check, daemon=True).start()

    def _post_manual_check(self, has_update, tag, url):
        self.btn_check_updates.configure(state="normal", text="Controlla Aggiornamenti")
        
        if has_update:
            # Niente Popup -> Cambia testo pulsante o aggiungi label sotto
            self.btn_check_updates.configure(text=f"Aggiorna a {tag} ⬇️", fg_color="#2CC02C", command=lambda: self.update_manager.open_download_page(url))
        else:
            # Niente Popup -> Feedback visuale temporaneo sul bottone
            original_text = "Controlla Aggiornamenti"
            self.btn_check_updates.configure(text="✅ Nessun aggiornamento", fg_color="gray")
            self.after(3000, lambda: self.btn_check_updates.configure(text=original_text, fg_color=("summary_theme", "blue"))) # Reset (colore default ctk è 'blue' o theme)

