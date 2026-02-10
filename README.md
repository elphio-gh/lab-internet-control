# Lab Internet Control

Strumento desktop per docenti per controllare l'accesso a Internet nei laboratori scolastici.

## Panoramica

Questo software permette ai docenti di:
- Bloccare e sbloccare l'accesso a Internet sui PC degli studenti.
- Impostare una "Whitelist" (elenco di siti consentiti).
- Monitorare lo stato dei PC (Internet ON/OFF) tramite una dashboard visiva.

Sviluppato in Python con interfaccia grafica moderna (CustomTkinter).

## Caratteristiche Principali

- **Fail-safe**: Internet viene ripristinato automaticamente al riavvio del PC studente.
- **Interfaccia Semplice**: Pulsanti grandi e chiari (Blocca, Sblocca, Whitelist).
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

## Licenza

**MIT License**
Copyright (c) 2026 **Alfonso Parisini**.

Distribuito gratuitamente per la comunità scolastica. Sentiti libero di usarlo, modificarlo e condividerlo!