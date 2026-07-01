from models.partie import Partie
from models.enums import ModePaiement

class Paiement:
    def __init__(self, id_paiement: int, partie: Partie, mode: ModePaiement, duree_simulee: float = 1.5):
        self.id_paiement = id_paiement
        self.partie = partie
        self.mode = mode
        self.duree_simulee = duree_simulee
        self.montant_final = self.calculer_total()

    def calculer_total(self) -> float:
        montant_brut = self.duree_simulee * self.partie.table.tarif_horaire
        remise = self.partie.client.calculer_remise(montant_brut)
        return montant_brut - remise
