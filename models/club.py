from typing import List
from models.table_billard import TableBillard
from models.client import Client

class Club:
    def __init__(self, nom: str, adresse: str):
        self.nom = nom
        self.adresse = adresse
        self.tables: List[TableBillard] = []
        self.clients: List[Client] = []

    def ajouter_table(self, table: TableBillard):
        self.tables.append(table)

    def inscrire_client(self, client: Client):
        self.clients.append(client)
