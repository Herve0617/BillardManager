import re

class Validators:
    @staticmethod
    def valider_telephone(telephone: str) -> bool:
        """Valide un numéro de téléphone (8 chiffres pour le Burkina Faso par exemple)."""
        pattern = r"^\d{8}$"
        return bool(re.match(pattern, telephone))

    @staticmethod
    def valider_email(email: str) -> bool:
        """Valide une adresse email standard."""
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))
