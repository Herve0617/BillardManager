from typing import List
from models import TableBillard, TypeBillard
from services.sauvegarde_service import SauvegardeService
from utils.constantes import TARIFS_BILLARD

class TableService:
    @staticmethod
    def verifier_numero_existe(numero: int, liste_tables: List[TableBillard]) -> bool:
        """Parcourt la liste en mémoire pour voir si le numéro de table est déjà pris."""
        for table in liste_tables:
            if table.numero == numero:
                return True  # Le numéro existe déjà, doublon détecté
        return False  # Le numéro est totalement libre

    @classmethod
    def ajouter_nouvelle_table(cls, numero: int, type_billard: TypeBillard) -> bool:
        """Gère la création sécurisée d'une table avec tarification automatique."""
        # 1. Charge les tables actuellement enregistrées sur le disque dur
        tables = SauvegardeService.charger_tables()

        # 2. Vérifie si le numéro demandé n'est pas déjà attribué
        if cls.verifier_numero_existe(numero, tables):
            print(f"\n❌ Erreur : La table N°{numero} existe déjà dans le club !")
            return False  # Annulation de l'opération

        # 3. Récupère automatiquement le tarif fixe lié au type de billard choisi
        tarif_automatique = TARIFS_BILLARD[type_billard.value]

        # 4. Instancie le nouvel objet métier TableBillard
        nouvelle_table = TableBillard(numero, type_billard, tarif_automatique)

        # 5. Ajoute la nouvelle table à la liste existante
        tables.append(nouvelle_table)

        # 6. Sauvegarde la liste mise à jour dans le fichier JSON
        SauvegardeService.sauvegarder_tables(tables)
        print(f"\n🟢 Succès : La table N°{numero} ({type_billard.value}) a été ajoutée.")
        return True
