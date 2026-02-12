
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from src.ui.widgets import PCWidget, ActionButton, PCRow
from src.ui.dialogs import ExitDialog # [NEW]
from src.ui.settings import SettingsFrame  # [NEW]
from src.utils.config import config
from src.utils.i18n import i18n  # [NEW]
from src.core.command_dispatcher import dispatcher
from src.core.pac_manager import PACManager
from src.core.pac_manager import PACManager
from src.core.veyon_manager import veyon
from src.core.update_manager import UpdateManager # [NEW]
from src.utils.version import APP_VERSION

class App(ctk.CTk):
    """
    Finestra principale dell'applicazione.
    """
    def __init__(self, pac_manager):
        super().__init__()

        self.pac_manager = pac_manager
        self.update_manager = UpdateManager() # [NEW]

        self.title(i18n.t("APP_TITLE"))
        self.geometry("1000x700")
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === Sidebar (Sinistra) ===
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="Lab Control", font=("Arial", 20, "bold"))
        self.lbl_title.pack(pady=20)

        # [NEW] Status Panel
        self.lbl_status_main = ctk.CTkLabel(self.sidebar, text="UNKNOWN", font=("Arial", 16, "bold"), text_color="gray")
        self.lbl_status_main.pack(pady=(0, 5))
        self.lbl_status_detail = ctk.CTkLabel(self.sidebar, text="", font=("Arial", 12), text_color="gray70")
        self.lbl_status_detail.pack(pady=(0, 20))
        
        # Pulsante Dashboard (per tornare alla vista PC)
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="💻 Dashboard", command=self.show_classroom, fg_color="transparent", border_width=1)
        self.btn_dashboard.pack(pady=10, padx=20, fill="x")

        # Pulsanti Azione (Testi Localizzati)
        self.btn_block = ActionButton(self.sidebar, text=i18n.t("BLOCK"), command=self.action_block, color="#CC0000")
        self.btn_block.pack(pady=(10, 5), padx=20, fill="x")

        # [NEW] Selettore Modalità Blocco
        # Forziamo sempre "Restart" all'avvio come richiesto
        config.set("block_mode", "restart")
        self.block_mode_var = ctk.StringVar(value=i18n.t("MODE_RESTART"))
        self.opt_block_mode = ctk.CTkOptionMenu(
            self.sidebar, 
            values=[i18n.t("MODE_RESTART"), i18n.t("MODE_MANUAL")],
            command=self.on_change_block_mode,
            variable=self.block_mode_var,
            font=("Arial", 11),
            fg_color="#555555",
            button_color="#444444"
        )
        self.opt_block_mode.pack(pady=(0, 20), padx=20, fill="x")

        self.btn_unblock = ActionButton(self.sidebar, text=i18n.t("UNBLOCK"), command=self.action_unblock, color="#009900")
        self.btn_unblock.pack(pady=10, padx=20, fill="x")

        self.btn_whitelist = ActionButton(self.sidebar, text=i18n.t("WL_ON"), command=self.action_whitelist, color="#CCCC00")
        self.btn_whitelist.pack(pady=(10, 5), padx=20, fill="x")
        self.btn_whitelist.configure(text_color="black")

        # [NEW] Pulsante Edit Whitelist
        self.btn_edit_wl = ctk.CTkButton(self.sidebar, text=i18n.t("BTN_EDIT_WL"), command=self.open_whitelist_settings, fg_color="transparent", border_width=1, font=("Arial", 11))
        self.btn_edit_wl.pack(pady=(0, 20), padx=20, fill="x")

        # [NEW] Selettore Lingua (Bandierine) in basso
        self.sidebar_bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_bottom.pack(side="bottom", fill="x", padx=10, pady=10)

        current_lang_code = config.get("language") or "it"
        lang_map = {k: v for k, v in i18n.LANGUAGES.items()}
        self.reverse_lang_map = {v: k for k, v in lang_map.items()}

        self.opt_lang = ctk.CTkOptionMenu(
            self.sidebar_bottom,
            values=list(lang_map.values()),
            command=self.on_change_language,
            font=("Arial", 12),
            fg_color="#333333",
            button_color="#222222"
        )
        self.opt_lang.set(lang_map.get(current_lang_code, "🇮🇹 Italiano"))
        self.opt_lang.pack(side="left", fill="x", expand=True)

        # Pulsante Settings (Ridotto a icona piccola)
        self.btn_settings = ctk.CTkButton(self.sidebar_bottom, text="⚙️", command=self.show_settings, width=30, fg_color="transparent", border_width=1)
        self.btn_settings.pack(side="right", padx=(5, 0))

        # === Container Principale (Destra) ===
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # -- Vista Classroom (Table Header + Scrollable) --
        self.view_classroom_container = ctk.CTkFrame(self.container, fg_color="transparent")
        
        # Header Tabella
        self.header_frame = ctk.CTkFrame(self.view_classroom_container, height=40, corner_radius=0, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 5))
        self.header_frame.grid_columnconfigure(0, weight=0, minsize=50)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(self.header_frame, text="Stato", font=("Arial", 12, "bold")).grid(row=0, column=0)
        ctk.CTkLabel(self.header_frame, text="Hostname", font=("Arial", 12, "bold"), anchor="w").grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(self.header_frame, text="Utente", font=("Arial", 12, "bold"), anchor="w").grid(row=0, column=2, sticky="w", padx=10)
        ctk.CTkLabel(self.header_frame, text="Modalità", font=("Arial", 12, "bold"), anchor="e").grid(row=0, column=3, sticky="e", padx=10)

        # Scrollable Area per le righe
        self.view_classroom = ctk.CTkScrollableFrame(self.view_classroom_container, label_text="")
        self.view_classroom.pack(fill="both", expand=True)

        # [NEW] Etichetta Notifiche (Toast) in basso
        self.lbl_notification = ctk.CTkLabel(self.view_classroom_container, text="", height=30, corner_radius=5, fg_color="transparent")
        self.lbl_notification.pack(fill="x", pady=(10, 0))

        # -- Vista Settings --
        self.view_settings = SettingsFrame(self.container, self.pac_manager)

        # Stato iniziale
        self.pc_widgets = {}
        self.whitelist_active = False
        self.is_blocked = False # [NEW] State tracking
        
        # Inizializza stato UI ripristinando l'ultimo stato noto
        last_state = config.get("last_state", "ON")
        self.update_gui_status(last_state)
        
        # [NEW] Gestione Chiusura App
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.show_classroom()
        
        # [NEW] Restore & Enforce: Se eravamo bloccati/WL, riapplichiamo il comando ai PC trovati
        # per garantire che lo stato UI corrisponda alla realtà (es. PC 11-20 accesi ora)
        if last_state != "ON":
            self.after(500, lambda: self.enforce_state(last_state))

        # [NEW] Avvio Scansione Periodica Stato (Agent-less)
        self.start_status_scan()

    def enforce_state(self, mode):
        """Riapplica lo stato salvato all'avvio (senza notifica)."""
        if not self.pc_widgets: return
        hosts = list(self.pc_widgets.keys())

        if mode == "OFF":
            block_mode = config.get("block_mode") or "restart"
            dispatcher.block_internet(hosts, mode=block_mode)
        elif mode == "WL":
            pac_url = f"http://{config.get('lab_ip', '192.168.1.100')}:{config.get('http_port')}/proxy.pac"
            dispatcher.apply_whitelist(hosts, pac_url)

    def update_gui_status(self, mode):
        """
        Aggiorna l'indicatore di stato globale e i pulsanti.
        mode: "ON" (Sbloccato), "OFF" (Bloccato), "WL" (Whitelist)
        """
        # [NEW] Persistenza stato
        config.set("last_state", mode)

        if mode == "ON":
            self.lbl_status_main.configure(text=i18n.t("STATUS_ON"), text_color="#00FF00")
            self.lbl_status_detail.configure(text="")
            self.btn_whitelist.configure(text=i18n.t("WL_ON"), fg_color="#CCCC00", hover_color="#AAAA00") 
            self.whitelist_active = False
            self.is_blocked = False
        elif mode == "OFF":
            self.lbl_status_main.configure(text=i18n.t("STATUS_OFF"), text_color="#FF0000")
            # Controlla modalità attuale per dettaglio
            block_mode = config.get("block_mode")
            if block_mode == "manual":
                self.lbl_status_detail.configure(text=i18n.t("STATUS_DETAIL_MANUAL"))
            else:
                self.lbl_status_detail.configure(text=i18n.t("STATUS_DETAIL_RESTART"))
            
            self.btn_whitelist.configure(text=i18n.t("WL_ON"), fg_color="#CCCC00", hover_color="#AAAA00")
            self.whitelist_active = False
            self.is_blocked = True
        elif mode == "WL":
            self.lbl_status_main.configure(text=i18n.t("STATUS_WL"), text_color="#FFFF00")
            self.lbl_status_detail.configure(text="") # O magari "Accesso Limitato"
            # Pulsante Whitelist diventa "Disattiva" e cambia stile
            self.btn_whitelist.configure(text=i18n.t("WL_OFF"), fg_color="#D4AF37", hover_color="#B5962F") # Gold/Dark Yellow
            self.whitelist_active = True
            self.is_blocked = True # Tecnicamente è bloccato (in whitelist)

    def show_notification(self, message, color="green", text_color="white"):
        """Mostra una notifica temporanea (Toast) senza bloccare l'UI."""
        self.lbl_notification.configure(text=message, fg_color=color, text_color=text_color)
        # Nascondi dopo 3 secondi
        self.after(3000, lambda: self.lbl_notification.configure(text="", fg_color="transparent"))

    def show_classroom(self):
        self.view_settings.grid_forget()
        self.view_classroom_container.grid(row=0, column=0, sticky="nsew") # Mostra container (Header + List)
        self.btn_dashboard.configure(fg_color=("gray75", "gray25")) # Highlight
        self.btn_settings.configure(fg_color="transparent")
        
        # Ricarichiamo se vuoto (es. primo avvio)
        if not self.pc_widgets:
            self.load_pc_table()

    def show_settings(self):
        self.view_classroom_container.grid_forget()
        self.view_settings.grid(row=0, column=0, sticky="nsew")
        self.btn_dashboard.configure(fg_color="transparent")
        self.btn_settings.configure(fg_color=("gray75", "gray25")) # Highlight

    def load_pc_table(self):
        hosts = veyon.get_hosts()
        hosts.sort() # Ordine Alfabetico

        for widget in self.view_classroom.winfo_children():
            widget.destroy()
        self.pc_widgets = {}

        if not hosts:
            lbl = ctk.CTkLabel(self.view_classroom, text="Nessun PC trovato.", text_color="orange")
            lbl.pack(pady=20)
            return
            
        # from src.ui.widgets import PCRow # Già importato

        for i, hostname in enumerate(hosts):
            # Alterna colori per leggibilità (Opzionale, ctk gestisce theme, ma possiamo dare un tocco)
            bg_color = "transparent" # Lasciamo default per clean look
            
            row = PCRow(self.view_classroom, hostname=hostname, status="UNKNOWN", fg_color=bg_color)
            row.pack(fill="x", pady=2, padx=5)
            self.pc_widgets[hostname] = row

    def on_change_block_mode(self, choice):
        """Callback: Aggiorna config quando cambia la modalità."""
        code = "restart" if choice == i18n.t("MODE_RESTART") else "manual"
        config.set("block_mode", code)

    def on_change_language(self, choice):
        """Callback: Aggiorna lingua e avvisa riavvio."""
        new_code = self.reverse_lang_map.get(choice, "it")
        config.set("language", new_code)
        messagebox.showinfo("Lingua", i18n.t("LBL_LANG")) # "Lingua (Riavvio richiesto)"

    def open_whitelist_settings(self):
        """Apre le impostazioni al tab Whitelist."""
        self.show_settings()
        self.view_settings.select_whitelist_tab()

    # I metodi action_ rimangono uguali, ma usano self.pc_widgets che ora è popolato in load_pc_grid
    def action_block(self):
        if not self.pc_widgets: return
        
        # Reset Whitelist Toggle
        self.whitelist_active = False
        self.btn_whitelist.configure(text=i18n.t("WL_ON"))
        
        hosts = list(self.pc_widgets.keys())
        mode = config.get("block_mode") or "restart"
        dispatcher.block_internet(hosts, mode=mode)
        
        # Notifica specifica per modalità
        msg = i18n.t("MSG_BLOCK_RESTART") if mode == "restart" else i18n.t("MSG_BLOCK_MANUAL")
        self.show_notification(msg, color="#CC0000")
        
        self.update_gui_status("OFF")


    def on_close(self):
        """Gestisce la chiusura dell'applicazione con controlli di sicurezza."""
        if self.whitelist_active:
            # Whitelist attiva -> Accesso parziale
            dialog = ExitDialog(self, i18n.t("EXIT_TITLE"), i18n.t("EXIT_MSG_WL"))
            answer = dialog.show()
            
            if answer is None: return # [FIX] Annulla uscita
            if answer:
                self.action_unblock() # Sblocca tutto prima di uscire
        
        elif self.is_blocked: # [NEW] Controllo tramite variabile di stato
            # Blocco attivo -> Controlla modalità
            mode = config.get("block_mode")
            if mode == "manual":
                # Blocco Manuale (Permanente)
                dialog = ExitDialog(self, i18n.t("EXIT_TITLE"), i18n.t("EXIT_MSG_MANUAL"))
                answer = dialog.show()
                
                if answer is None: return # [FIX] Annulla uscita
                if answer:
                    self.action_unblock()
            else:
                # Blocco Restart (RunOnce) -> Si sblocca al riavvio, ma chiediamo lo stesso
                dialog = ExitDialog(self, i18n.t("EXIT_TITLE"), i18n.t("EXIT_MSG_RESTART"))
                answer = dialog.show()
                
                if answer is None: return # [FIX] Annulla uscita
                if answer:
                    self.action_unblock()
        
        # Procedi alla chiusura
        self.destroy()

    def action_unblock(self):
        if not self.pc_widgets: return

        # Reset Whitelist Toggle
        self.whitelist_active = False
        self.btn_whitelist.configure(text=i18n.t("WL_ON"))

        hosts = list(self.pc_widgets.keys())
        dispatcher.unblock_internet(hosts)
        self.show_notification(i18n.t("MSG_UNBLOCK").format(len(hosts)), color="#009900")
        self.update_gui_status("ON")

    def action_whitelist(self):
        if not self.pc_widgets: return
        hosts = list(self.pc_widgets.keys())

        if not self.whitelist_active:
            # ATTIVA WHITELIST
            
            # [NEW] Check modifiche non salvate
            if self.view_settings.has_unsaved_changes():
                answer = messagebox.askyesnocancel(
                    i18n.t("UNSAVED_CHANGES_TITLE"),
                    i18n.t("UNSAVED_CHANGES_MSG")
                )
                if answer is None: # Cancel
                    return
                elif answer is True: # Yes -> Salva
                    self.view_settings.save_whitelist()
                    # Procedi con l'attivazione
                # elif answer is False: # No -> Procedi con vecchia config
            
            pac_url = f"http://{config.get('lab_ip', '192.168.1.100')}:{config.get('http_port')}/proxy.pac"
            dispatcher.apply_whitelist(hosts, pac_url)
            
            self.show_notification(i18n.t("MSG_WHITELIST").format(len(hosts)), color="#CCCC00", text_color="black")
            self.update_gui_status("WL")
        else:
            # DISATTIVA WHITELIST -> TORNA A BLOCCATO (o Blocca tutto per sicurezza)
            mode = config.get("block_mode") or "restart"
            dispatcher.block_internet(hosts, mode=mode)
            
            self.show_notification("Whitelist Disattivata. Internet BLOCCATO.", color="#CC0000")
            self.update_gui_status("OFF")


    def update_pc_status(self, hostname, status, user=None):
        for name, widget in self.pc_widgets.items():
            if name.lower() == hostname.lower():
                widget.update_status(status, user)
                return

    def start_status_scan(self):
        """
        Loop periodico: "Punzecchia" i PC via Veyon per farsi mandare lo stato via UDP.
        Non richiede installazione agenti -> Sfrutta PowerShell remoto.
        """
        if not self.pc_widgets:
            # Se la lista è vuota (es. simulazione avviata dopo), riproviamo a caricare
            self.load_pc_table()
            
        if self.pc_widgets:
            hosts = list(self.pc_widgets.keys())
            # Esegui scansione in un thread separato per non bloccare UI mentre itera i comandi Veyon?
            # dispatcher.scan_status è veloce (fire and forget), ma se ci sono tanti host meglio thread.
            # Per ora lo chiamiamo direttamente, dispatcher usa subprocess.
            
            # [FIX] Eseguiamo la scansione in un thread separato per non bloccare l'UI
            import threading
            scan_thread = threading.Thread(
                target=dispatcher.scan_status,
                args=(hosts, config.get("udp_port")),
                daemon=True
            )
            scan_thread.start()
            
        # Ripeti ogni 10 secondi
        self.after(10000, self.start_status_scan)
