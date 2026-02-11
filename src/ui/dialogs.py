import customtkinter as ctk
from src.utils.i18n import i18n

class ExitDialog(ctk.CTkToplevel):
    """
    Dialogo di uscita personalizzato.
    - 2 Pulsanti: Mantieni Blocco vs Rimuovi Blocco.
    - Tasto X: Annulla l'uscita (ritorna None).
    """
    def __init__(self, master, title, message):
        super().__init__(master)
        
        self.result = None # True (Sblocca), False (Mantieni), None (Annulla)
        
        # Titolo Finestra
        self.title(title)
        
        # Geometria e Aspetto
        self.geometry("420x220")
        self.resizable(False, False)
        
        # Centra rispetto alla finestra principale
        self.update_idletasks()
        try:
            x = master.winfo_x() + (master.winfo_width() // 2) - 210
            y = master.winfo_y() + (master.winfo_height() // 2) - 110
            self.geometry(f"+{x}+{y}")
        except:
            pass # Fallback se master non calcolabile
        
        # Rendilo modale
        self.grab_set()
        
        # Gestione X della finestra
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1) # Messaggio
        self.grid_rowconfigure(1, weight=0) # Pulsanti
        
        # Messaggio (Body)
        self.lbl_msg = ctk.CTkLabel(self, text=message, font=("Arial", 14), text_color="gray90", wraplength=380, justify="center")
        self.lbl_msg.grid(row=0, column=0, columnspan=2, pady=20, padx=20)
        
        # Pulsanti (Footer)
        # Button 1: RIMUOVI BLOCCO (Azione 'Positiva' -> Sblocca e Esci)
        self.btn_remove = ctk.CTkButton(
            self, text=i18n.t("BTN_REMOVE_BLOCK"), width=160, height=40,
            command=self.on_remove, fg_color="#009900", hover_color="#007700", font=("Arial", 12, "bold")
        )
        self.btn_remove.grid(row=1, column=0, padx=10, pady=(0, 20))
        
        # Button 2: MANTIENI BLOCCO (Azione 'Negativa' -> Esci lasciando bloccato)
        self.btn_keep = ctk.CTkButton(
            self, text=i18n.t("BTN_KEEP_BLOCK"), width=160, height=40,
            command=self.on_keep, fg_color="#CC0000", hover_color="#990000", font=("Arial", 12, "bold")
        )
        self.btn_keep.grid(row=1, column=1, padx=10, pady=(0, 20))

    def on_remove(self):
        self.result = True # True significa "Sblocca"
        self.destroy()

    def on_keep(self):
        self.result = False # False significa "Non sbloccare" (ma esci)
        self.destroy()

    def on_cancel(self):
        self.result = None # None significa "Non uscire"
        self.destroy()

    def show(self):
        """Blocca e aspetta input utente. Ritorna True, False o None."""
        self.wait_window()
        return self.result
