from models.personne import Personne
from utils.constantes import TAUX_REMISE_VIP

class Client(Personne):
    def __init__(self, id_personne: str, nom: str, prenom: str, telephone: str, est_vip: bool = False):
        super().__init__(id_personne, nom, prenom, telephone)
        self.est_vip = est_vip

    def calculer_remise(self, montant_brut: float) -> float:
        return montant_brut * TAUX_REMISE_VIP if self.est_vip else 0.0
