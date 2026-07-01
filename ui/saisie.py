from models.enums import TypeBillard, ModePaiement
from utils.validators import Validators

class Saisie:
    @staticmethod
    def saisir_entier(message: str) -> int:
        """Demande un entier de manière sécurisée."""
        while True:  # Crée une boucle infinie jusqu'à obtenir une saisie correcte
            try:
                # Demande la saisie au clavier et tente de la convertir en entier (int)
                return int(input(message))
            except ValueError:
                # Si la conversion échoue (ex: l'utilisateur écrit 'deux' au lieu de 2)
                print("❌ Saisie invalide. Veuillez entrer un nombre entier.")

    @staticmethod
    def saisir_flottant(message: str) -> float:
        """Demande un nombre décimal de manière sécurisée."""
        while True:  # Boucle tant que la valeur saisie n'est pas un nombre à virgule
            try:
                # Demande la saisie et tente de la convertir en nombre décimal (float)
                return float(input(message))
            except ValueError:
                # Si l'utilisateur saisit du texte non numérique
                print("❌ Saisie invalide. Veuillez entrer un nombre valide.")

    @staticmethod
    def saisir_texte(message: str) -> str:
        """Demande une chaîne de caractères non vide."""
        while True:
            # .strip() supprime automatiquement les espaces inutiles au début et à la fin
            valeur = input(message).strip()
            if valeur:  # Si la chaîne n'est pas vide après le strip, on la valide
                return valeur
            # Si l'utilisateur a juste appuyé sur Entrée sans rien écrire
            print("❌ Ce champ ne peut pas être vide.")

    @staticmethod
    def saisir_telephone(message: str) -> str:
        """Force la saisie d'un numéro de téléphone à 8 chiffres."""
        while True:
            # Récupère le numéro tapé par l'utilisateur
            tel = input(message).strip()
            # Utilise notre validateur Regex pour vérifier s'il y a exactement 8 chiffres
            if Validators.valider_telephone(tel):
                return tel  # Si c'est valide, retourne le numéro sous forme de texte
            # Si le numéro contient des lettres ou n'a pas 8 chiffres
            print("❌ Numéro invalide. Il doit comporter exactement 8 chiffres.")

    @staticmethod
    def choisir_enum(enum_classe, message_titre: str):
        """Permet de choisir dynamiquement une option parmi n'importe quel Enum."""
        print(f"\n--- {message_titre} ---")
        # Transforme l'Enum Python en une liste d'éléments manipulables
        options = list(enum_classe)
        # Parcourt la liste pour afficher chaque option indexée à partir de 1
        for i, option in enumerate(options, 1):
            print(f"{i}. {option.value}")
        
        while True:
            # Demande un nombre entier correspondant au choix de l'utilisateur
            choix = Saisie.saisir_entier(f"Votre choix (1-{len(options)}) : ")
            # Vérifie si le nombre tapé est bien compris dans la plage des choix possibles
            if 1 <= choix <= len(options):
                # Retourne l'élément Enum sélectionné (index - 1 car les listes commencent à 0)
                return options[choix - 1]
            # Si le nombre est hors limites (ex: choix 5 alors qu'il n'y a que 3 options)
            print(f"❌ Veuillez choisir un nombre entre 1 et {len(options)}.")
