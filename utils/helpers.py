from datetime import datetime
from utils.constantes import FORMAT_DATE_HEURE

class Helpers:
    @staticmethod
    def date_vers_chaine(dateobj: datetime) -> str:
        """Convertit un objet datetime en chaîne de caractères pour le stockage JSON."""
        if not dateobj:
            return ""
        return dateobj.strftime(FORMAT_DATE_HEURE)

    @staticmethod
    def chaine_vers_date(chaine: str) -> datetime:
        """Convertit une chaîne de caractères JSON en objet datetime."""
        if not chaine:
            return None
        return datetime.strptime(chaine, FORMAT_DATE_HEURE)
