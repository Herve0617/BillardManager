import json
import os
from datetime import datetime
from typing import List, Optional
from models import Partie, Client, TableBillard, TypeBillard
from services.sauvegarde_service import SauvegardeService

class PartieService:
    FICHIER_PARTIES = os.path.join("data", "parties.json")

    @classmethod
    def initialiser_fichier_parties(cls):
        """S'assure que le fichier d'historique des parties existe."""
        if not os.path.exists(cls.FICHIER_PARTIES):
            with open(cls.FICHIER_PARTIES, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    @staticmethod
    def obtenir_tables_libres_par_type(type_choisi: TypeBillard) -> List[TableBillard]:
        """Retourne uniquement les tables du type demandé qui ne sont pas occupées."""
        toutes_les_tables = SauvegardeService.charger_tables()
        return [t for t in toutes_les_tables if t.type_billard == type_choisi and not t.est_occupee]

    @classmethod
    def démarrer_partie(cls, client: Client, table: TableBillard):
        """Initialise une nouvelle partie et bascule la table en mode occupé."""
        cls.initialiser_fichier_parties()
        
        # 1. Lit l'historique pour générer un ID de partie unique
        with open(cls.FICHIER_PARTIES, "r", encoding="utf-8") as f:
            historique = json.load(f)
        id_nouvelle_partie = len(historique) + 1

        # 2. Enregistre le lancement de la partie dans l'historique JSON
        nouvelle_partie_dict = {
            "id_partie": id_nouvelle_partie,
            "id_client": client.id_personne,
            "numero_table": table.numero,
            "heure_debut": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "heure_fin": None,
            "cloturee": False
        }
        historique.append(nouvelle_partie_dict)
        with open(cls.FICHIER_PARTIES, "w", encoding="utf-8") as f:
            json.dump(historique, f, indent=4)

        # 3. Met à jour l'état de la table sur le disque
        toutes_tables = SauvegardeService.charger_tables()
        for t in toutes_tables:
            if t.numero == table.numero:
                t.est_occupee = True
        SauvegardeService.sauvegarder_tables(toutes_tables)

    @classmethod
    def obtenir_parties_actives(cls) -> List[dict]:
        """Retourne la liste de toutes les parties qui ne sont pas encore clôturées."""
        cls.initialiser_fichier_parties()
        try:
            with open(cls.FICHIER_PARTIES, "r", encoding="utf-8") as f:
                historique = json.load(f)
            # SÉCURITÉ : On s'assure de ne garder que les dictionnaires où cloturee est strictement False
            return [p for p in historique if p.get("cloturee") is False]
        except (json.JSONDecodeError, FileNotFoundError):
            return []


    @classmethod
    def cloturer_partie_en_base(cls, id_partie: int, heure_fin_str: str) -> float:
        """Marque la partie comme terminée et libère définitivement la table."""
        with open(cls.FICHIER_PARTIES, "r", encoding="utf-8") as f:
            historique = json.load(f)

        numero_table_a_liberer = None
        
        # Met à jour les données de la partie correspondante
        for p in historique:
            if p["id_partie"] == id_partie:
                p["cloturee"] = True
                p["heure_fin"] = heure_fin_str
                numero_table_a_liberer = p["numero_table"]
                break

        # Réécriture de l'historique mis à jour
        with open(cls.FICHIER_PARTIES, "w", encoding="utf-8") as f:
            json.dump(historique, f, indent=4)

        # Libération de la table correspondante dans le fichier des tables
        toutes_tables = SauvegardeService.charger_tables()
        for t in toutes_tables:
            if t.numero == numero_table_a_liberer:
                t.est_occupee = False
        SauvegardeService.sauvegarder_tables(toutes_tables)

    @classmethod
    def obtenir_historique_complet(cls) -> List[dict]:
        """Retourne l'intégralité des sessions de jeu passées (clôturées)."""
        cls.initialiser_fichier_parties()
        try:
            with open(cls.FICHIER_PARTIES, "r", encoding="utf-8") as f:
                historique = json.load(f)
            # On trie pour n'afficher que les parties qui SONT clôturées
            return [p for p in historique if p.get("cloturee") is True]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
