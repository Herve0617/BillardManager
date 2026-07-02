import json
import os
from datetime import datetime
from typing import List
from models.enums import StatutReservation
from services.sauvegarde_service import SauvegardeService

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
            "statut": StatutReservation.CONFIRMEE.value
        }
        
        reservations.append(nouvelle_res)
        with open(cls.FICHIER_RESERVATIONS, "w", encoding="utf-8") as f:
            json.dump(reservations, f, indent=4)
        return True

    @classmethod
    def charger_toutes_reservations(cls) -> List[dict]:
        cls.initialiser_fichier()
        try:
            with open(cls.FICHIER_RESERVATIONS, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
