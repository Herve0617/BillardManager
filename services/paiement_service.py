import json
import os
from typing import List
from models.enums import ModePaiement
from utils.constantes import TAUX_REMISE_VIP

class PaiementService:
    FICHIER_PAIEMENTS = os.path.join("data", "paiements.json")

    @classmethod
    def initialiser_fichier_paiements(cls):
        """S'assure que le fichier d'enregistrement des recettes financières existe."""
        if not os.path.exists(cls.FICHIER_PAIEMENTS):
            with open(cls.FICHIER_PAIEMENTS, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    @classmethod
    def generer_facture(cls, id_partie: int, tarif_horaire: float, duree_heures: float, est_vip: bool, mode: ModePaiement, id_employe: str) -> dict:
        """Calcule la facture et enregistre l'ID de l'employé en service."""
        cls.initialiser_fichier_paiements()

        montant_brut = round(duree_heures * tarif_horaire, 2)
        remise = round(montant_brut * TAUX_REMISE_VIP, 2) if est_vip else 0.0
        net_a_payer = montant_brut - remise

        with open(cls.FICHIER_PAIEMENTS, "r", encoding="utf-8") as f:
            transactions = json.load(f)
        id_recu = len(transactions) + 1

        recu_dict = {
            "id_paiement": id_recu,
            "id_partie": id_partie,
            "duree_heures": round(duree_heures, 2),
            "montant_brut": montant_brut,
            "remise_vip": remise,
            "montant_net": net_a_payer,
            "mode_paiement": mode.value,
            "id_employe": id_employe  # Ajout de la traçabilité employé
        }

        transactions.append(recu_dict)
        with open(cls.FICHIER_PAIEMENTS, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=4)

        return recu_dict

