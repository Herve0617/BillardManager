import json
import os
from datetime import datetime
from typing import List

from models import Client, TableBillard, TypeBillard
from utils import Helpers

class SauvegardeService:
    FICHIER_CLIENTS = os.path.join("data", "clients.json")
    FICHIER_TABLES = os.path.join("data", "tables.json")

    @classmethod
    def initialiser_dossier_data(cls):
        """S'assure que le dossier 'data' et les fichiers JSON existent."""
        if not os.path.exists("data"):
            os.makedirs("data")
        for fichier in [cls.FICHIER_CLIENTS, cls.FICHIER_TABLES]:
            if not os.path.exists(fichier) or os.path.getsize(fichier) == 0:
                with open(fichier, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)

    # --- NOUVELLE MÉTHODE DE GÉNÉRATION AUTOMATIQUE D'ID ---
    @classmethod
    def generer_prochain_id_client(cls) -> str:
        """Calcule le nombre de clients en base pour générer un ID unique (ex: CLT0001)."""
        cls.initialiser_dossier_data()
        try:
            with open(cls.FICHIER_CLIENTS, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                # Le prochain numéro est égal à la taille de la liste actuelle + 1
                prochain_numero = len(donnees) + 1
                # :04d permet de forcer l'affichage sur 4 chiffres avec des zéros (ex: 1 -> 0001)
                return f"CLT{prochain_numero:04d}"
        except (json.JSONDecodeError, FileNotFoundError):
            return "CLT0001"

    # --- SECTION CLIENTS (Mise à jour pour accepter les ID en chaînes de caractères) ---
    @classmethod
    def sauvegarder_clients(cls, liste_clients: List[Client]):
        cls.initialiser_dossier_data()
        donnees = []
        for client in liste_clients:
            donnees.append({
                "id_personne": client.id_personne,  # Stocke la chaîne "CLT0001"
                "nom": client.nom,
                "prenom": client.prenom,
                "telephone": client.telephone,
                "est_vip": client.est_vip
            })
        with open(cls.FICHIER_CLIENTS, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)

    @classmethod
    def charger_clients(cls) -> List[Client]:
        cls.initialiser_dossier_data()
        liste_clients = []
        try:
            with open(cls.FICHIER_CLIENTS, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                for item in donnees:
                    client = Client(
                        id_personne=item["id_personne"],  # Récupère la chaîne "CLT0001"
                        nom=item["nom"],
                        prenom=item["prenom"],
                        telephone=item["telephone"],
                        est_vip=item["est_vip"]
                    )
                    liste_clients.append(client)
        except json.JSONDecodeError:
            return []
        return liste_clients

    # --- SECTION TABLES ---
    @classmethod
    def sauvegarder_tables(cls, liste_tables: List[TableBillard]):
        cls.initialiser_dossier_data()
        donnees = []
        for table in liste_tables:
            donnees.append({
                "numero": table.numero,
                "type_billard": table.type_billard.value,
                "tarif_horaire": table.tarif_horaire,
                "est_occupee": table.est_occupee
            })
        with open(cls.FICHIER_TABLES, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)

    @classmethod
    def charger_tables(cls) -> List[TableBillard]:
        cls.initialiser_dossier_data()
        liste_tables = []
        try:
            with open(cls.FICHIER_TABLES, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                for item in donnees:
                    type_enum = TypeBillard(item["type_billard"])
                    table = TableBillard(
                        numero=item["numero"],
                        type_billard=type_enum,
                        tarif_horaire=item["tarif_horaire"]
                    )
                    table.est_occupee = item["est_occupee"]
                    liste_tables.append(table)
        except json.JSONDecodeError:
            return []
        return liste_tables

    #----SECTION EMPLOYES---------
    
    @classmethod
    def charger_employes(cls) -> List[dict]:
        """Charge la liste des employés disponibles dans le club."""
        fichier_emp = os.path.join("data", "employes.json")
        if not os.path.exists(fichier_emp):
            # Initialisation automatique avec deux employés types du Burkina
            employes_defaut = [
                {"id_personne": "EMP0001", "nom": "Zoungrana", "prenom": "Pierre", "telephone": "70203040", "poste": "Réceptionniste"},
                {"id_personne": "EMP0002", "nom": "Sawadogo", "prenom": "Ali", "telephone": "76112233", "poste": "Gérant"}
            ]
            with open(fichier_emp, "w", encoding="utf-8") as f:
                json.dump(employes_defaut, f, indent=4, ensure_ascii=False)
        try:
            with open(fichier_emp, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

