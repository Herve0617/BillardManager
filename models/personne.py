from utils.validators import Validators

class Personne:
    def __init__(self, id_personne: int, nom: str, prenom: str, telephone: str):
        if not Validators.valider_telephone(telephone):
            raise ValueError("Numéro de téléphone invalide. Il doit contenir 8 chiffres.")
        
        self.id_personne = id_personne
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone
