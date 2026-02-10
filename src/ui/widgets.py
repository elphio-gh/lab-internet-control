import customtkinter as ctk

class PCWidget(ctk.CTkFrame):
    """
    Rappresenta un singolo PC nella dashboard.
    Mostra il nome, l'utente collegato e un LED colorato per lo stato.
    """
    def __init__(self, master, hostname, status="UNKNOWN", user=None, **kwargs):
        super().__init__(master, **kwargs)
        self.hostname = hostname
        self.status = status
        self.user = user
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        
        # Etichetta Nome PC
        self.lbl_name = ctk.CTkLabel(self, text=hostname, font=("Arial", 14, "bold"))
        self.lbl_name.grid(row=0, column=0, padx=5, pady=(5, 0))

        # [NEW] Etichetta Utente (più piccola)
        self.lbl_user = ctk.CTkLabel(self, text=user if user else "---", font=("Arial", 11), text_color="gray")
        self.lbl_user.grid(row=1, column=0, padx=5, pady=(0, 5))
        
        # LED Stato (Canvas circolare)
        self.canvas = ctk.CTkCanvas(self, width=20, height=20, highlightthickness=0, bg=self._apply_appearance_mode(self._bg_color))
        self.canvas.grid(row=2, column=0, pady=5)
        self.led = self.canvas.create_oval(2, 2, 18, 18, fill="gray")
        
        self.update_status(status, user)

    def update_status(self, new_status, new_user=None):
        """Aggiorna stato e (opzionalmente) utente."""
        self.status = new_status
        if new_user:
            self.user = new_user
            self.lbl_user.configure(text=new_user)
        
        color = "gray"
        if new_status == "ON":
            color = "#00FF00"  # Verde
        elif new_status == "OFF":
            color = "#FF0000"  # Rosso
        elif new_status == "WL":
            color = "#FFFF00"  # Giallo
        elif new_status == "UNKNOWN":
            color = "gray"
            
        self.canvas.itemconfig(self.led, fill=color)

        self.canvas.itemconfig(self.led, fill=color)

class PCRow(ctk.CTkFrame):
    """
    Rappresenta un singolo PC nella dashboard in formato tabellare.
    [LED] [Hostname] [User] [Status]
    """
    def __init__(self, master, hostname, status="UNKNOWN", user=None, **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        self.hostname = hostname
        self.status = status
        self.user = user
        
        # Layout Griglia: 4 colonne
        self.grid_columnconfigure(0, weight=0, minsize=50)  # LED
        self.grid_columnconfigure(1, weight=1)              # Hostname
        self.grid_columnconfigure(2, weight=1)              # User
        self.grid_columnconfigure(3, weight=1)              # Status Text

        # 1. LED Stato
        self.canvas = ctk.CTkCanvas(self, width=16, height=16, highlightthickness=0, bg=self._apply_appearance_mode(self._bg_color))
        self.led = self.canvas.create_oval(2, 2, 14, 14, fill="gray")
        self.canvas.grid(row=0, column=0, padx=10, pady=5)

        # 2. Hostname
        self.lbl_name = ctk.CTkLabel(self, text=hostname, font=("Arial", 14, "bold"), anchor="w")
        self.lbl_name.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # 3. User
        self.lbl_user_val = user if user else "---"
        self.lbl_user = ctk.CTkLabel(self, text=self.lbl_user_val, font=("Arial", 12), text_color="gray", anchor="w")
        self.lbl_user.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # 4. Status Text
        self.lbl_status = ctk.CTkLabel(self, text=status, font=("Arial", 12, "bold"), text_color="gray", anchor="e")
        self.lbl_status.grid(row=0, column=3, padx=10, pady=5, sticky="e")
        
        self.update_status(status, user)

    def update_status(self, new_status, new_user=None):
        """Aggiorna stato e (opzionalmente) utente."""
        self.status = new_status
        if new_user:
            self.user = new_user
            self.lbl_user.configure(text=new_user)
        
        color = "gray"
        text = "UNKNOWN"
        text_color = "gray"
        
        if new_status == "ON":
            color = "#00FF00"  # Verde
            text = "SBLOCCATO"
            text_color = "#00DD00"
        elif new_status == "OFF":
            color = "#FF0000"  # Rosso
            text = "BLOCCATO"
            text_color = "#FF3333"
        elif new_status == "WL":
            color = "#FFFF00"  # Giallo
            text = "WHITELIST"
            text_color = "#DDDD00"
            
        self.canvas.itemconfig(self.led, fill=color)
        self.lbl_status.configure(text=text, text_color=text_color)

class ActionButton(ctk.CTkButton):
    def __init__(self, master, text, command, color, **kwargs):
        super().__init__(master, text=text, command=command, fg_color=color, hover_color=color, height=60, font=("Arial", 18, "bold"), **kwargs)
