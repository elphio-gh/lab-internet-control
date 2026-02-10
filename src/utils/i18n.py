from src.utils.logger import log
from src.utils.config import config

class I18n:
    """
    Gestisce l'internazionalizzazione dell'applicazione.
    """
    
    LANGUAGES = {
        "it": "🇮🇹 Italiano",
        "en": "🇬🇧 English",
        "de": "🇩🇪 Deutsch",
        "fr": "🇫🇷 Français",
        "es": "🇪🇸 Español"
    }

    TRANSLATIONS = {
        "it": {
            "APP_TITLE": "Lab Internet Control - Dashboard Docente",
            "BLOCK": "BLOCCA INTERNET",
            "UNBLOCK": "SBLOCCA INTERNET",
            "WL_ON": "CONSENTI WHITELIST",
            "WL_OFF": "DISATTIVA WHITELIST",
            "SETTINGS": "Impostazioni",
            "LAB_STATUS": "Stato Laboratorio",
            "MSG_BLOCK": "Comando BLOCCO inviato a {} PC.",
            "MSG_UNBLOCK": "Comando SBLOCCO inviato a {} PC.",
            "MSG_WHITELIST": "Comando WHITELIST inviato a {} PC.",
            "TAB_GENERAL": "Generali",
            "TAB_WHITELIST": "Whitelist",
            "LBL_LANG": "Lingua (Riavvio richiesto)",
            "LBL_MODE": "Modalità di Blocco",
            "MODE_RESTART": "Fino al riavvio (Consigliato)",
            "MODE_MANUAL": "Manuale (Sblocco Manuale)",
            "BTN_EDIT_WL": "✏️ Modifica",
            "BTN_ADD": "Aggiungi",
            "BTN_REMOVE": "Rimuovi Selezionato",
            "BTN_SAVE": "Salva",
            "ERR_NO_SEL": "Nessun elemento selezionato.",
            "SAVED": "Impostazioni salvate.",
        },
        "en": {
            "APP_TITLE": "Lab Internet Control - Teacher Dashboard",
            "BLOCK": "BLOCK INTERNET",
            "UNBLOCK": "UNBLOCK INTERNET",
            "WL_ON": "ALLOW WHITELIST",
            "WL_OFF": "DISABLE WHITELIST",
            "SETTINGS": "Settings",
            "LAB_STATUS": "Lab Status",
            "MSG_BLOCK": "BLOCK command sent to {} PCs.",
            "MSG_UNBLOCK": "UNBLOCK command sent to {} PCs.",
            "MSG_WHITELIST": "WHITELIST command sent to {} PCs.",
            "TAB_GENERAL": "General",
            "TAB_WHITELIST": "Whitelist",
            "LBL_LANG": "Language (Restart required)",
            "LBL_MODE": "Blocking Mode",
            "MODE_RESTART": "Until Restart (Recommended)",
            "MODE_MANUAL": "Manual (Manual Unblock)",
            "BTN_EDIT_WL": "✏️ Edit",
            "BTN_ADD": "Add",
            "BTN_REMOVE": "Remove Selected",
            "BTN_SAVE": "Save",
            "ERR_NO_SEL": "No item selected.",
            "SAVED": "Settings saved.",
        },
        "de": {
            "APP_TITLE": "Lab Internet Control - Lehrer Dashboard",
            "BLOCK": "INTERNET SPERREN",
            "UNBLOCK": "INTERNET FREIGEBEN",
            "WL_ON": "WHITELIST ERLAUBEN",
            "WL_OFF": "WHITELIST DEAKTIVIEREN",
            "SETTINGS": "Einstellungen",
            "LAB_STATUS": "Laborstatus",
            "MSG_BLOCK": "SPERREN Befehl gesendet an {} PCs.",
            "MSG_UNBLOCK": "FREIGEBEN Befehl gesendet an {} PCs.",
            "MSG_WHITELIST": "WHITELIST Befehl gesendet an {} PCs.",
            "TAB_GENERAL": "Allgemein",
            "TAB_WHITELIST": "Whitelist",
            "LBL_LANG": "Sprache (Neustart erforderlich)",
            "LBL_MODE": "Sperrmodus",
            "MODE_RESTART": "Bis Neustart (Empfohlen)",
            "MODE_MANUAL": "Manuell (Manuelle Freigabe)",
            "BTN_EDIT_WL": "✏️ Bearbeiten",
            "BTN_ADD": "Hinzufügen",
            "BTN_REMOVE": "Ausgewählte entfernen",
            "BTN_SAVE": "Speichern",
            "ERR_NO_SEL": "Kein Element ausgewählt.",
            "SAVED": "Einstellungen gespeichert.",
        },
        "fr": {
            "APP_TITLE": "Lab Internet Control - Tableau de Bord Enseignant",
            "BLOCK": "BLOQUER INTERNET",
            "UNBLOCK": "DÉBLOQUER INTERNET",
            "WL_ON": "AUTORISER WHITELIST",
            "WL_OFF": "DÉSACTIVER WHITELIST",
            "SETTINGS": "Paramètres",
            "LAB_STATUS": "État du Laboratoire",
            "MSG_BLOCK": "Commande BLOQUER envoyée à {} PC.",
            "MSG_UNBLOCK": "Commande DÉBLOQUER envoyée à {} PC.",
            "MSG_WHITELIST": "Commande WHITELIST envoyée à {} PC.",
            "TAB_GENERAL": "Général",
            "TAB_WHITELIST": "Liste Blanche",
            "LBL_LANG": "Langue (Redémarrage requis)",
            "LBL_MODE": "Mode de Blocage",
            "MODE_RESTART": "Jusqu'au redémarrage (Recommandé)",
            "MODE_MANUAL": "Manuel (Déblocage Manuel)",
            "BTN_EDIT_WL": "✏️ Modifier",
            "BTN_ADD": "Ajouter",
            "BTN_REMOVE": "Supprimer la sélection",
            "BTN_SAVE": "Enregistrer",
            "ERR_NO_SEL": "Aucun élément sélectionné.",
            "SAVED": "Paramètres enregistrés.",
        },
        "es": {
            "APP_TITLE": "Lab Internet Control - Panel del Docente",
            "BLOCK": "BLOQUEAR INTERNET",
            "UNBLOCK": "DESBLOQUEAR INTERNET",
            "WL_ON": "PERMITIR WHITELIST",
            "WL_OFF": "DESACTIVAR WHITELIST",
            "SETTINGS": "Ajustes",
            "LAB_STATUS": "Estado del Laboratorio",
            "MSG_BLOCK": "Comando BLOQUEO enviado a {} PC.",
            "MSG_UNBLOCK": "Comando DESBLOQUEO enviado a {} PC.",
            "MSG_WHITELIST": "Comando WHITELIST enviado a {} PC.",
            "TAB_GENERAL": "General",
            "TAB_WHITELIST": "Lista Blanca",
            "LBL_LANG": "Idioma (Reinicio requerido)",
            "LBL_MODE": "Modo de Bloqueo",
            "MODE_RESTART": "Hasta reiniciar (Recomendado)",
            "MODE_MANUAL": "Manual (Desbloqueo Manual)",
            "BTN_EDIT_WL": "✏️ Editar",
            "BTN_ADD": "Añadir",
            "BTN_REMOVE": "Eliminar selección",
            "BTN_SAVE": "Guardar",
            "ERR_NO_SEL": "Ningún elemento seleccionado.",
            "SAVED": "Ajustes guardados.",
        }
    }

    def __init__(self):
        self.current_lang = config.get("language") or "it"
        if self.current_lang not in self.TRANSLATIONS:
            log.warning(f"Lingua '{self.current_lang}' non supportata. Fallback su 'it'.")
            self.current_lang = "it"

    def t(self, key):
        """Restituisce la traduzione per la chiave data."""
        return self.TRANSLATIONS[self.current_lang].get(key, key)

# Istanza globale
i18n = I18n()
