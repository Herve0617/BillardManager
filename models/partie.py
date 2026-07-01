from datetime import datetime
from models.client import Client
from models.table_billard import TableBillard

class Partie:
    def __init__(self, id_partie: int, client: Client, table: TableBillard):
        self.id_partie = id_partie
        self.client = client
        self.table = table
        self.heure_debut = datetime.now()
        self.heure_fin = None
        self.table.est_occupee = True

    def cloturer(self) -> float:
        """Termine la partie et libère la table."""
        self.heure_fin = datetime.now()
        self.table.est_occupee = False
        duree = (self.heure_fin - self.heure_debut).total_seconds() / 3600
        return max(duree, 0.5)  # Facture au moins 30 minutes
