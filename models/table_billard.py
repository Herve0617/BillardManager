from models.enums import TypeBillard

class TableBillard:
    def __init__(self, numero: int, type_billard: TypeBillard, tarif_horaire: float):
        self.numero = numero
        self.type_billard = type_billard  # Utilisation stricte de l'Enum
        self.tarif_horaire = tarif_horaire
        self.est_occupee = False
