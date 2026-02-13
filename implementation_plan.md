# Improving Whitelist Description

## User Review Required
- Please review the proposed text for the whitelist explanation below.

## Proposed Changes

### src/utils/i18n.py
#### [MODIFY] Update `LBL_WL_DESC`
Before: `Inserisci i domini consentiti (uno per riga)`
After: `Domini consentiti`

### src/ui/settings.py
#### [MODIFY] Update instruction label
Replace the current short instruction with a detailed, non-technical explanation:

```python
label_text = (
    "Inserisci un dominio per riga.\n"
    "Esempio:\n"
    "• 'google.com' autorizza TUTTI i sottodomini (Drive, Classroom, ecc.)\n"
    "• 'classroom.google.com' autorizza SOLO Classroom (non tutto Google)."
)
```

## Verification Plan

### Manual Verification
- Run the application (`run_lab.bat`).
- Navigate to Settings -> Whitelist.
- Verify the new text is displayed clearly and without redundancy.
