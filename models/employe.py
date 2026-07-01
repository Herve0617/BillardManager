from models.personne import Personne

class Employe(Personne):
    def __init__(self, id_personne: int, nom: str, prenom: str, telephone: str, poste: str):
        super().__init__(id_personne, nom, prenom, telephone)
        self.poste = poste
