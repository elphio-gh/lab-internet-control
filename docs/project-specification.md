# Progetto: Lab Internet Control  
Dashboard docente per controllo Internet ON / OFF / Whitelist tramite Veyon

---

## 1. Scopo del progetto

Realizzare un software **desktop per Windows (Windows 10 e Windows 11)** che consenta al docente di:

- bloccare Internet sui PC degli studenti
- sbloccare Internet
- consentire l’accesso **solo a una whitelist di siti**
- visualizzare **a colpo d’occhio** lo stato di ogni PC del laboratorio
- operare in modo **sicuro, intuitivo e a prova di errore umano**

Il software deve essere **utilizzabile anche da docenti non tecnici** (es. religione, supplenti), senza necessità di formazione specifica.

---

## 2. Contesto reale (vincoli obbligatori)

### 2.1 Infrastruttura
- Rete in **DHCP**
- **Veyon** già installato e funzionante
- Veyon identifica i PC tramite **hostname**
- Presenza di **più laboratori**, ciascuno con il proprio PC cattedra

### 2.2 PC Studenti
- Sistema operativo: **Windows 10 e Windows 11**
- Più account **non amministrativi**, uno per classe (es. `1A`, `1B`, `1C`, …)
- Account studenti:
  - protetti da password
  - **NON amministratori**
- Presente un account **Admin** per manutenzione, non usato dagli studenti

### 2.3 PC Docente
- Sistema operativo: **Windows 10 o Windows 11**
- Presente **solo account Admin**, senza password
- Su ogni PC docente deve girare **una istanza indipendente** del programma
- Ogni laboratorio è gestito in modo autonomo

---

## 3. Principi di progettazione (NON negoziabili)

### 3.1 Fail-safe obbligatorio
**Internet NON deve mai rimanere bloccato per errore.**

Devono essere gestiti correttamente:
- spegnimento improvviso
- riavvio
- blackout
- docente che dimentica di sbloccare Internet

👉 **Comportamento predefinito**:  
> Internet torna automaticamente **ATTIVO** al riavvio del PC studente.

---

### 3.2 Modalità di blocco configurabili

Il sistema deve supportare **due modalità**, selezionabili dalle impostazioni dell’interfaccia docente:

#### Modalità 1 — *Blocco fino al riavvio* (**DEFAULT**)
- Internet viene bloccato immediatamente
- Al primo reboot o nuovo login:
  - Internet viene **automaticamente ripristinato**
- È la modalità consigliata e predefinita

#### Modalità 2 — *Blocco fino a sblocco manuale*
- Internet resta bloccato finché il docente non clicca “Sblocca”
- Pensata per verifiche o esami
- NON è la modalità di default

---

### 3.3 Scope di sicurezza e limiti dichiarati

Questo progetto è uno **strumento di controllo didattico**, non un sistema di sicurezza anti-attaccante.

Sono **fuori dallo scope**:
- prevenzione di hotspot mobili personali
- prevenzione di VPN esterne o tunnel fuori banda
- controllo di applicazioni che ignorano le impostazioni proxy di sistema

Il sistema è progettato per:
- browser standard
- software didattico comune
- contesti scolastici senza AD/GPO e senza privilegi amministrativi sugli studenti

Per un enforcement di rete più forte è necessario un controllo a livello gateway/firewall, che non rientra negli obiettivi di questo progetto.

---

## 4. Meccanismo tecnico di blocco (client-side)

### 4.1 Requisiti
- Nessun utilizzo di firewall di sistema
- Nessun UAC
- Nessun privilegio admin sugli account studenti
- Tutto deve avvenire a livello **HKCU (profilo utente)**

### 4.2 Tecnica adottata
Blocco Internet tramite **proxy locale non funzionante**:

```

127.0.0.1:6666

```

Modifica delle chiavi:
```

HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings

```

Questa tecnica:
- funziona su Windows 10 e Windows 11
- funziona con utenti non admin
- è immediata e reversibile

---

## 5. Whitelist (requisito obbligatorio)

### 5.1 Funzionalità
- Deve esistere una modalità:
  **“Consenti SOLO i siti in whitelist”**
- Tutto ciò che non è in whitelist deve essere bloccato

### 5.2 Implementazione
- Uso di **PAC file (Proxy Auto Configuration)**
- Regola logica:
  - domini whitelist → `DIRECT`
  - tutto il resto → `PROXY 127.0.0.1:6666`

### 5.3 Gestione whitelist
- La whitelist **DEVE essere modificabile dall’interfaccia grafica**
- Il docente deve poter:
  - aggiungere un dominio
  - rimuoverlo
  - modificarlo
- Nessuna modifica manuale di file o codice

### 5.4 Server PAC
- Il programma docente deve includere:
  - un **mini server HTTP interno**
  - che espone `proxy.pac`
- Il PC docente:
  - **NON** fa da proxy di navigazione
  - serve solo il file PAC
- Deve essere considerato il comportamento offline (cache del PAC)
- Opzionalmente supportare PAC locale (`file://`) per whitelist stabili

---

## 6. Comportamento al riavvio (fail-safe)

### 6.1 Modalità “fino a riavvio”
Quando Internet viene bloccato:
- viene creata una chiave:
```

HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce

```
- la chiave è creata **nel profilo dell’utente studente loggato**
- al prossimo login:
  - Internet viene automaticamente sbloccato
  - le chiavi di blocco vengono rimosse

### 6.2 Modalità “manuale”
- NON viene creata alcuna chiave RunOnce
- il ripristino avviene solo tramite comando docente

---

## 7. Invisibilità lato studente (UX fondamentale)

Quando il docente esegue un’azione:
- ❌ nessuna finestra CMD o PowerShell visibile
- ❌ nessun prompt tecnico
- ✅ solo un messaggio chiaro a schermo

### Messaggi previsti:
- “Internet è stato BLOCCATO dall’insegnante”
- “Internet è stato SBLOCCATO dall’insegnante”
- “Navigazione consentita solo su siti autorizzati”

I messaggi devono:
- essere grafici (popup Windows)
- comparire solo all’utente loggato
- non richiedere interazione tecnica

---

## 8. Telemetria e stato PC (LED)

### 8.1 Problema
Non è affidabile leggere il registro di Windows da remoto senza privilegi amministrativi.

### 8.2 Soluzione
Ogni PC studente, quando applica un’azione:
- invia un messaggio **UDP** al PC docente

Formato:
```

HOSTNAME|ON
HOSTNAME|OFF
HOSTNAME|WL

```

La telemetria è **solo informativa** e non costituisce un canale di comando.

### 8.3 Uso
La dashboard docente:
- ascolta su una porta UDP configurabile
- aggiorna i LED in tempo reale
- se non riceve aggiornamenti, mostra stato “sconosciuto” o “in attesa di conferma”

---

## 9. Interfaccia utente (PRIORITÀ ASSOLUTA)

### 9.1 Obiettivo UX
Un docente deve poter usare il software:
- **senza formazione**
- **senza leggere manuali**
- **senza paura di sbagliare**

### 9.2 Interfaccia richiesta
- Finestra unica
- Lista PC del laboratorio:
  - nome PC
  - LED colorato
- Tre pulsanti grandi e chiari:
  - 🔴 Blocca Internet
  - 🟢 Sblocca Internet
  - 🟡 Whitelist
- Se nessun PC è selezionato → azione su **tutta la classe**

### 9.3 Gestione whitelist
- Sezione “Siti consentiti”
- Lista modificabile:
  - Aggiungi dominio
  - Rimuovi dominio
- Le modifiche devono avere effetto immediato

### 9.4 Impostazioni (poche e chiare)
- Modalità di blocco:
  - (●) fino al riavvio **[DEFAULT]**
  - (○) fino a sblocco manuale
- (opzionale) timeout automatico di sblocco

---

## 10. Integrazione con Veyon

### 10.1 Backend A (baseline)
- Workflow Veyon “Invia ed esegui”
- Trasferimento script ai PC studenti ed esecuzione remota

### 10.2 Backend B (preferito)
- Uso di `veyon-cli` o WebAPI (se disponibili)
- Avvio di script o comandi senza trasferimento file
- Riduzione delle notifiche lato client

### 10.3 Command Abstraction Layer
Il progetto deve includere un livello di astrazione dei comandi, ad esempio:

```

send_action(hosts, action, mode, teacher_host, pac_url)

```

In questo modo eventuali cambi di backend non richiederanno modifiche al resto del codice.

---

## 11. Autenticazione e controllo accesso

- L’accesso alla dashboard docente deve essere protetto
- Deve essere richiesto un **PIN o password locale** all’avvio
- Le credenziali non devono essere condivise in rete
- La sicurezza dei comandi remoti è demandata a Veyon

---

## 12. Logging e tracciabilità (GDPR-friendly)

Il sistema deve mantenere un **log minimale** delle azioni del docente.

Il log include:
- data e ora
- laboratorio
- azione (Blocca / Sblocca / Whitelist)
- elenco PC target
- esito per PC (ok / timeout / non raggiungibile)

Il log NON include:
- siti visitati
- contenuti
- dati personali degli studenti

Il log deve:
- essere locale al PC docente
- avere retention configurabile
- essere esportabile (CSV)

---

## 13. Packaging

- Applicazione desktop Windows
- Preferibile: **Python + PyInstaller → `.exe`**
- Nessuna installazione complessa
- Configurazione locale (file JSON o YAML)

---

## 14. Internazionalizzazione (i18n)

- Applicazione multilingua
- Stringhe UI separate dal codice
- Supporto iniziale:
  - Inglese
  - Italiano
  - Tedesco
  - Francese
  - Spagnolo
- Aggiunta di nuove lingue senza modifiche al codice

---

## 15. Gestione errori e modalità di fallimento

- Timeout per host non raggiungibile
- Numero limitato di tentativi (retry)
- Stato “non raggiungibile” per PC problematici
- UI sempre responsiva
- Pulsante “Riprova su non riusciti”
- Se la telemetria non arriva: stato “applicato, in attesa di conferma”

---

## 16. Criteri di successo

Il progetto è riuscito se:
- Internet non rimane mai bloccato per errore
- Un docente non tecnico lo usa senza spiegazioni
- Funziona in modo identico su Windows 10 e Windows 11
- La whitelist è gestibile dall’interfaccia
- Nessun UAC, nessun prompt tecnico
- Nessun panico da “oddio ho rotto Internet alla classe”

---

## 17. Obiettivo finale

Non uno script “furbo”, ma:

> **uno strumento scolastico affidabile, prevedibile e umano**.

---
