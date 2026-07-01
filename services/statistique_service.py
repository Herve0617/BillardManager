import json
import os
from utils.constantes import DEVISE

class StatistiqueService:
    # Chemin absolu vers le fichier d'enregistrement des reçus financiers
    FICHIER_PAIEMENTS = os.path.join("data", "paiements.json")

    @classmethod
    def generer_rapport_financier(cls) -> dict:
        """Analyse le fichier comptable pour extraire les indicateurs clés de performance."""
        # Initialisation d'un dictionnaire de statistiques par défaut (si le fichier est vide)
        stats = {
            "total_recettes_net": 0.0,
            "total_remises_vip": 0.0,
            "nombre_transactions": 0,
            "ventilation_modes": {}
        }

        # Sécurité : Si le fichier n'existe pas encore, on retourne les stats à zéro
        if not os.path.exists(cls.FICHIER_PAIEMENTS):
            return stats

        try:
            # Ouverture et lecture du grand livre des paiements JSON
            with open(cls.FICHIER_PAIEMENTS, "r", encoding="utf-8") as f:
                transactions = json.load(f)
            
            # Compte le nombre total de reçus de caisse émis par le club
            stats["nombre_transactions"] = len(transactions)

            # Parcourt chaque transaction pour cumuler les montants
            for t in transactions:
                # Cumul du chiffre d'affaires net encaissé (après déduction des remises)
                stats["total_recettes_net"] += t.get("montant_net", 0.0)
                # Cumul du manque à gagner / cadeaux offerts aux membres VIP
                stats["total_remises_vip"] += t.get("remise_vip", 0.0)

                # Ventilation dynamique par mode de paiement (Orange Money, Espèces, etc.)
                mode = t.get("mode_paiement", "Inconnu")
                # Si le mode de paiement n'est pas encore dans le dictionnaire, on l'initialise à 0
                if mode not in stats["ventilation_modes"]:
                    stats["ventilation_modes"][mode] = 0.0
                # On ajoute le montant net de la transaction au mode de paiement correspondant
                stats["ventilation_modes"][mode] += t.get("montant_net", 0.0)

            # Arrondit les résultats financiers à deux décimales pour éviter les bugs d'affichage flottants
            stats["total_recettes_net"] = round(stats["total_recettes_net"], 2)
            stats["total_remises_vip"] = round(stats["total_remises_vip"], 2)
            
        except (json.JSONDecodeError, FileNotFoundError):
            # En cas de fichier corrompu, retourne le dictionnaire initialisé à zéro
            return stats

        return stats
