# Lab Internet Control

Strumento desktop per docenti per controllare l'accesso a Internet nei laboratori scolastici.

## Panoramica

Questo software permette ai docenti di:
- Bloccare e sbloccare l'accesso a Internet sui PC degli studenti.
- Impostare una "Whitelist" (elenco di siti consentiti).
- Monitorare lo stato dei PC (Internet ON/OFF) tramite una dashboard visiva.

Sviluppato in Python con interfaccia grafica moderna (CustomTkinter). **Versione: v0.3.5**

## Caratteristiche Principali

- **Fail-safe**: Internet viene ripristinato automaticamente al riavvio del PC studente.
- **Interfaccia Semplice & Intuitiva**: Dashboard con indicatori visivi chiari (Verde/Rosso/Giallo) per lo stato di Internet.
- **Whitelist Intelligente**: Modalità "Sito Consentito" con visual feedback immediato e controllo modifiche non salvate.
- **Gestione Veyon & CSV**: 
    - Import/Export configurazione PC.
    - Template CSV scaricabile per facilitare l'importazione.
- **Cross-Platform**: Sviluppato su Linux, destinato a Windows 10/11.
    - **Nota Dev**: Su Linux l'app parte in modalità "No-Op" (nessuna modifica al sistema, dashboard vuota se non c'è Veyon).
- **Sincronizzazione Veyon**: La lista dei PC viene letta all'avvio. Se si aggiungono PC su Veyon, è necessario riavviare l'applicazione per vederli.
- **Nessuna installazione server**: Funziona peer-to-peer (Docente -> Veyon -> Studenti).

## Installazione (Sviluppo)

1.  Clonare il repository.
2.  Creare un ambiente virtuale Python:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux
    venv\Scripts\activate     # Windows
    ```
3.  Installare le dipendenze:
    ```bash
    pip install -r requirements.txt
    # Nota per Arch Linux: installa anche tk con 'sudo pacman -S tk'
    ```
4.  Avviare l'applicazione:
    ```bash
    python src/main.py
    ```

## Struttura del Progetto

- `src/main.py`: Punto di ingresso.
- `src/core/`: Logica di business (Registro, PAC, Veyon).
- `src/ui/`: Interfaccia grafica.
- `src/network/`: Server UDP (telemetria) e HTTP (PAC).

## Distribuzione (Windows)

Per creare l'installer .exe, segui questa procedura nella **VM Windows**:

1.  **Preparazione Ambiente**:
    -   Installa Python 3.11+ e Git.
    -   Installa **Inno Setup Compiler**.
    -   Clona/Aggiorna il repo: `git pull`

2.  **Build (Creazione .exe)**:
    ```resh
    # Crea venv e installa dipendenze
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    pip install pyinstaller

    # Lancia lo script di build
    python build_windows.py
    ```
    *Questo genererà la cartella `dist/LabInternetControl`.*

3.  **Generazione Installer**:
    -   Apri `installer_config.iss` con Inno Setup.
    -   Premi **Run (F9)**.
    -   Troverai il file `LabInternetControl_Setup_vX.X.X.exe` nella cartella principale.

Le configurazioni e i log degli utenti verranno salvati in `%LOCALAPPDATA%\LabInternetControl`.

Le configurazioni e i log degli utenti verranno salvati in `%LOCALAPPDATA%\LabInternetControl` per garantire la compatibilità con i permessi di sistema.

## Principi di Design
-   **Zero Code Burden**: Il codice deve essere gestito interamente dallo sviluppatore.
-   **No Popups**: L'applicazione non deve mai interrompere l'utente con popup invasivi (eccetto conferme critiche esplicite).
-   **Cross-Platform**: Sviluppo su Linux, Esecuzione su Windows.

## Licenza

**MIT License**
Copyright (c) 2026 **Alfonso Parisini**.

Distribuito gratuitamente per la comunità scolastica. Sentiti libero di usarlo, modificarlo e condividerlo!