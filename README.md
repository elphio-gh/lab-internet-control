# Lab Internet Control

Strumento desktop per docenti per controllare l'accesso a Internet nei laboratori scolastici.

## Panoramica

Questo software permette ai docenti di:
- Bloccare e sbloccare l'accesso a Internet sui PC degli studenti.
- Impostare una "Whitelist" (elenco di siti consentiti).
- Monitorare lo stato dei PC (Internet ON/OFF) tramite una dashboard visiva.

Sviluppato in Python con interfaccia grafica moderna (CustomTkinter). **Versione: v0.2.0**

## Caratteristiche Principali

- **Fail-safe**: Internet viene ripristinato automaticamente al riavvio del PC studente.
- **Interfaccia Semplice & Intuitiva**: Dashboard con indicatori visivi chiari (Verde/Rosso/Giallo) per lo stato di Internet.
- **Whitelist Intelligente**: Modalità "Sito Consentito" con visual feedback immediato e controllo modifiche non salvate.
- **Gestione Veyon & CSV**: 
    - Import/Export configurazione PC.
    - Template CSV scaricabile per facilitare l'importazione.
- **Cross-Platform**: Sviluppato per girare su Windows 10/11.
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

Per distribuire il software nei laboratori, segui la procedura nella VM Windows:
1.  Eseguire `python build_windows.py` per creare la build con PyInstaller.
2.  Utilizzare **Inno Setup** con il file `installer_config.iss` per generare l'installer finale.

Le configurazioni e i log degli utenti verranno salvati in `%LOCALAPPDATA%\LabInternetControl` per garantire la compatibilità con i permessi di sistema.

## Licenza

**MIT License**
Copyright (c) 2026 **Alfonso Parisini**.

Distribuito gratuitamente per la comunità scolastica. Sentiti libero di usarlo, modificarlo e condividerlo!