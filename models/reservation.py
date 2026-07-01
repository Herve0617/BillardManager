from datetime import datetime
from models.client import Client
from models.table_billard import TableBillard
from models.enums import StatutReservation

class Reservation:
    def __init__(self, id_res: int, client: Client, table: TableBillard, date_heure: datetime):
        self.id_res = id_res
        self.client = client
        self.table = table
        self.date_heure = date_heure
        self.statut = StatutReservation.CONFIRMEE
