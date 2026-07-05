import json
import os
from datetime import datetime
from typing import List
from models.enums import StatutReservation
from services.sauvegarde_service import SauvegardeService
from services.partie_service import PartieService
from services.client_service import ClientService

class ReservationService:
    FICHIER_RESERVATIONS = os.path.join("data", "reservations.json")

    @classmethod
    def initialiser_fichier(cls):
        if not os.path.exists(cls.FICHIER_RESERVATIONS):
            with open(cls.FICHIER_RESERVATIONS, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    @classmethod
    def creer_reservation(cls, id_client: str, numero_table: int, date_heure_str: str) -> bool:
        cls.initialiser_fichier()
        with open(cls.FICHIER_RESERVATIONS, "r", encoding="utf-8") as f:
            reservations = json.load(f)
        
        id_res = f"RES{len(reservations) + 1:04d}"
        
        nouvelle_res = {
            "id_res": id_res,
            "id_client": id_client,
            "numero_table": numero_table,
            "date_heure": date_heure_str,
            "statut": "Confirmée"
        }
        
        reservations.append(nouvelle_res)
        with open(cls.FICHIER_RESERVATIONS, "w", encoding="utf-8") as f:
            json.dump(reservations, f, indent=4)
        return True

    @classmethod
    def changer_statut_reservation(cls, id_res: str, nouveau_statut: str) -> bool:
        """Modifie le statut d'une réservation, UNIQUEMENT si elle est encore 'Confirmée'."""
        cls.initialiser_fichier()
        with open(cls.FICHIER_RESERVATIONS, "r", encoding="utf-8") as f:
            reservations = json.load(f)

        trouve = False
        for r in reservations:
            if r["id_res"].upper() == id_res.upper():
                # BLINDAGE DE SÉCURITÉ : On interdit d'annuler une réservation déjà Honorée ou Annulée
                if r["statut"] != "Confirmée":
                    return False  # Opération refusée, le statut est verrouillé
                
                r["statut"] = nouveau_statut
                trouve = True
                break

        if trouve:
            with open(cls.FICHIER_RESERVATIONS, "w", encoding="utf-8") as f:
                json.dump(reservations, f, indent=4)
        return trouve

    @classmethod
    def honorer_reservation(cls, id_res: str) -> bool:
        """Transforme une réservation en partie active, UNIQUEMENT si elle est 'Confirmée'."""
        cls.initialiser_fichier()
        with open(cls.FICHIER_RESERVATIONS, "r", encoding="utf-8") as f:
            reservations = json.load(f)

        res_cible = next((r for r in reservations if r["id_res"].upper() == id_res.upper()), None)
        
        # BLINDAGE DE SÉCURITÉ : On vérifie qu'elle existe ET qu'elle est bien 'Confirmée'
        if not res_cible or res_cible["statut"] != "Confirmée":
            return False

        # Récupération des objets métiers
        client = ClientService.rechercher_client_par_id(res_cible["id_client"])
        toutes_tables = SauvegardeService.charger_tables()
        table = next((t for t in toutes_tables if t.numero == res_cible["numero_table"]), None)

        if not client or not table:
            return False

        if table.est_occupee:
            return False  # Sécurité si la table est physiquement prise entre temps

        # Lancement automatique du chronomètre de jeu
        PartieService.démarrer_partie(client, table)

        # Verrouillage du statut final
        res_cible["statut"] = "Honorée"
        
        with open(cls.FICHIER_RESERVATIONS, "w", encoding="utf-8") as f:
            json.dump(reservations, f, indent=4)
        return True


    @classmethod
    def charger_toutes_reservations(cls) -> List[dict]:
        cls.initialiser_fichier()
        # 1. Lance le nettoyage automatique des retards avant de lire les données
        cls.verifier_et_nettoyer_retards()
        
        # 2. Lit et retourne le fichier mis à jour
        try:
            with open(cls.FICHIER_RESERVATIONS, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []


    @classmethod
    def verifier_et_nettoyer_retards(cls):
        """Annule automatiquement les réservations dont les clients ont plus de 30 min de retard."""
        cls.initialiser_fichier()
        with open(cls.FICHIER_RESERVATIONS, "r", encoding="utf-8") as f:
            reservations = json.load(f)

        maintenant = datetime.now()
        modifie = False

        for r in reservations:
            if r["statut"] == "Confirmée":
                try:
                    heure_prevue = datetime.strptime(r["date_heure"], "%Y-%m-%d %H:%M:%S")
                    retard_minutes = (maintenant - heure_prevue).total_seconds() / 60
                    
                    # Si l'heure est dépassée de plus de 30 minutes
                    if retard_minutes > 30:
                        r["statut"] = "Annulée (Retard)"
                        modifie = True
                except ValueError:
                    continue

        # Si au moins un statut a changé, on réécrit le fichier JSON à chaud
        if modifie:
            with open(cls.FICHIER_RESERVATIONS, "w", encoding="utf-8") as f:
                json.dump(reservations, f, indent=4)
