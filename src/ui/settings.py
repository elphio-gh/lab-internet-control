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

    def _init_whitelist_tab(self):
        """Inizializza il tab Whitelist."""
        # Descrizione
        ctk.CTkLabel(self.tab_wl, text=i18n.t("LBL_WL_DESC") + ":", anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        
        # Text Area per i domini
        self.txt_whitelist = ctk.CTkTextbox(self.tab_wl, height=200)
        self.txt_whitelist.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Carica valori attuali
        current_wl = config.get("whitelist", [])
        self.txt_whitelist.insert("0.0", "\n".join(current_wl))
        
        # Pulsanti Azione
        frame_actions = ctk.CTkFrame(self.tab_wl, fg_color="transparent")
        frame_actions.pack(fill="x", padx=20, pady=20)
        
        self.btn_save_wl = ctk.CTkButton(frame_actions, text="Salva Whitelist", command=self.save_whitelist, fg_color="#2CC985", text_color="white")
        self.btn_save_wl.pack(side="right")
        
        ctk.CTkLabel(frame_actions, text="Una riga per dominio (es. wikipedia.org)", text_color="gray", font=("Arial", 11)).pack(side="left")

    def _init_veyon_tab(self):
        """Inizializza il tab Veyon."""
        # Info
        ctk.CTkLabel(self.tab_veyon, text="Gestione PC (Veyon)", font=("Arial", 16, "bold")).pack(pady=(20, 10))
        
        # [FIX] Caricamento Asincrono della lista PC
        # Non chiamiamo veyon.get_hosts() qui perché blocca l'avvio dell'app.
        self.lbl_veyon_count = ctk.CTkLabel(self.tab_veyon, text="PC Rilevati: ???", font=("Arial", 14))
        self.lbl_veyon_count.pack(pady=5)
        
        self.btn_refresh_veyon = ctk.CTkButton(self.tab_veyon, text="🔄 Carica Lista PC", command=self.load_veyon_hosts_async)
        self.btn_refresh_veyon.pack(pady=5)

        # Frame Pulsanti Import/Export
        frame_io = ctk.CTkFrame(self.tab_veyon, fg_color="transparent")
        frame_io.pack(pady=20)
        
        ctk.CTkButton(frame_io, text="Scarica Template CSV", command=self.download_csv_template).pack(side="left", padx=10)
        ctk.CTkButton(frame_io, text="Importa da CSV", command=self.import_csv_veyon).pack(side="left", padx=10)
        ctk.CTkButton(frame_io, text="Esporta su CSV", command=self.export_csv_veyon).pack(side="left", padx=10)
        
        # Note
        note = "Nota: L'importazione su Veyon richiede privilegi di amministratore.\nSe fallisce, prova a eseguire l'app come Admin o usa Veyon Configurator."
        ctk.CTkLabel(self.tab_veyon, text=note, text_color="orange", font=("Arial", 11)).pack(pady=20)

    def load_veyon_hosts_async(self):
        """Carica la lista host in background per non bloccare la UI."""
        self.btn_refresh_veyon.configure(state="disabled", text="Caricamento...")
        
        import threading
        def _load():
            hosts = veyon.get_hosts()
            count = len(hosts)
            # Update UI in Main Thread
            self.after(0, lambda: self.lbl_veyon_count.configure(text=f"PC Rilevati: {count}"))
            self.after(0, lambda: self.btn_refresh_veyon.configure(state="normal", text="🔄 Ricarica Lista"))
            
        threading.Thread(target=_load, daemon=True).start()

    def save_whitelist(self):
        """Salva la whitelist dalla text area alla config."""
        content = self.txt_whitelist.get("0.0", "end").strip()
        # Filtra righe vuote
        domains = [line.strip() for line in content.split("\n") if line.strip()]
        
        # Aggiorna Config
        config.set("whitelist", domains)
        # Aggiorna PAC Manager (runtime)
        self.pac_manager.update_whitelist(domains)
        
        self.btn_save_wl.configure(text="Salvato! ✅", fg_color="green")
        self.after(2000, lambda: self.btn_save_wl.configure(text="Salva Whitelist", fg_color="#2CC985"))

    def has_unsaved_changes(self):
        """Controlla se ci sono modifiche non salvate nella whitelist."""
        current_gui = self.txt_whitelist.get("0.0", "end").strip()
        saved_list = config.get("whitelist", [])
        saved_text = "\n".join(saved_list).strip()
        return current_gui != saved_text

    def select_whitelist_tab(self):
        self.tabview.set(i18n.t("TAB_WHITELIST"))
        self.txt_whitelist.focus_set()

    def download_csv_template(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile="template_lab.csv")
        if path:
            ok, msg = veyon.get_template_csv(path)
            if ok:
                messagebox.showinfo("Successo", msg)
            else:
                messagebox.showerror("Errore", msg)

    def import_csv_veyon(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            if messagebox.askyesno("Conferma", "Vuoi importare questo file in Veyon?\nAttenzione: La lista attuale verrà sovrascritta (Consigliato)."):
                ok, msg = veyon.import_csv(path, clear_existing=True)
                if ok:
                    messagebox.showinfo("Successo", f"{msg}\nRiavvia l'applicazione per vedere i nuovi PC.")
                else:
                    messagebox.showerror("Errore Import", msg)

    def export_csv_veyon(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile="backup_veyon.csv")
        if path:
            ok, msg = veyon.export_csv(path)
            if ok:
                messagebox.showinfo("Successo", msg)
            else:
                messagebox.showerror("Errore Export", msg)

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
        
        # [NEW] Progress Bar (inizialmente nascosta)
        self.progress = ctk.CTkProgressBar(center_frame, width=200, height=10)
        self.progress.set(0)
        # self.progress.pack() # Pack solo quando serve

        # Separatore visivo (Linea)
        ctk.CTkFrame(center_frame, height=2, fg_color="gray40").pack(fill="x", pady=20, padx=40)
        
        # Note Legali (Scrollable se lunghe, o solo Label)
        ctk.CTkLabel(center_frame, text="Info Legali:", font=("Arial", 12, "bold")).pack(anchor="w", padx=40)
        
        legal_msg = i18n.t("LEGAL_NOTES")
        check_legal = ctk.CTkTextbox(center_frame, height=80, fg_color="transparent", text_color="gray70", wrap="word")
        check_legal.insert("0.0", legal_msg)
        check_legal.configure(state="disabled") # Read-only
        check_legal.pack(fill="x", padx=40, pady=5)

    # ... (altri metodi esistenti) ...

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
            # Se l'URL finisce con .exe, possiamo scaricarlo direttamente
            if url and url.lower().endswith(".exe"):
                self.btn_check_updates.configure(
                    text=f"Scarica e Installa {tag} ⬇️", 
                    fg_color="#2CC02C", 
                    command=lambda: self.confirm_and_download(tag, url)
                )
            else:
                # Fallback: apre pagina web
                self.btn_check_updates.configure(
                    text=f"Aggiorna a {tag} (Web) ⬇️", 
                    fg_color="#2CC02C", 
                    command=lambda: self.update_manager.open_download_page(url)
                )
        else:
            # Niente Popup -> Feedback visuale temporaneo sul bottone
            original_text = "Controlla Aggiornamenti"
            self.btn_check_updates.configure(text="✅ Nessun aggiornamento", fg_color="gray")
            self.after(3000, lambda: self.btn_check_updates.configure(text=original_text, fg_color=("summary_theme", "blue"))) # Reset (colore default ctk è 'blue' o theme)

    def confirm_and_download(self, tag, url):
        """Chiede conferma e avvia il download."""
        if messagebox.askyesno("Aggiornamento", f"Vuoi scaricare e installare la versione {tag}?\nL'applicazione verrà chiusa."):
            self.start_download_update(url)

    def start_download_update(self, url):
        """Avvia il download in un thread separato."""
        self.btn_check_updates.configure(state="disabled", text="Avvio download...")
        self.progress.pack(pady=(0, 10)) # Mostra barra
        self.progress.set(0)
        
        import threading
        def _download():
            # Callback di progresso sicura per thread
            def _on_progress(p):
                self.after(0, lambda: self.progress.set(p))
                self.after(0, lambda: self.btn_check_updates.configure(text=f"Download: {int(p*100)}%"))

            file_path = self.update_manager.download_installer(url, progress_callback=_on_progress)
            self.after(0, lambda: self._post_download(file_path))
            
        threading.Thread(target=_download, daemon=True).start()

    def _post_download(self, file_path):
        """Fine download: avvia installer o mostra errore."""
        self.progress.pack_forget()
        
        if file_path:
            self.btn_check_updates.configure(text="Avvio Installer...")
            # Un piccolo delay per far vedere il 100%
            self.after(500, lambda: self.update_manager.run_installer(file_path))
        else:
            messagebox.showerror("Errore", "Download fallito. Controlla la connessione o scarica manualmente.")
            self.btn_check_updates.configure(state="normal", text="Riprova Aggiornamento")

