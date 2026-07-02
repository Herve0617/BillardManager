from datetime import datetime
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
            "ca_jour": 0.0,
            "ca_mois": 0.0,
            "ca_annee": 0.0,
            "ventilation_modes": {}
        }

        # Sécurité : Si le fichier n'existe pas encore, on retourne les stats à zéro
        if not os.path.exists(cls.FICHIER_PAIEMENTS):
            return stats
        
        # Nous récupérons la date du jour (2026-07-02 pour vos tests actuels)
        maintenant = datetime.now()
        str_jour = maintenant.strftime("%Y-%m-%d")
        str_mois = maintenant.strftime("%Y-%m")
        str_annee = maintenant.strftime("%Y")

        try:
            # Ouverture et lecture du grand livre des paiements JSON
            with open(cls.FICHIER_PAIEMENTS, "r", encoding="utf-8") as f:
                transactions = json.load(f)
                
            # Nous chargeons aussi l'historique des parties pour lier les dates d'encaissement
            with open(os.path.join("data", "parties.json"), "r", encoding="utf-8") as f_p:
                parties = json.load(f_p)
            
            # Compte le nombre total de reçus de caisse émis par le club
            stats["nombre_transactions"] = len(transactions)

            # Parcourt chaque transaction pour cumuler les montants
            for t in transactions:
                net = t.get("montant_net", 0.0)
                # Cumul du chiffre d'affaires net encaissé (après déduction des remises)
                stats["total_recettes_net"] += t.get("montant_net", 0.0)
                # Cumul du manque à gagner / cadeaux offerts aux membres VIP
                stats["total_remises_vip"] += t.get("remise_vip", 0.0)
                
                # Récupération de la date réelle d'exécution via l'ID de partie
                partie = next((p for p in parties if p["id_partie"] == t["id_partie"]), None)
                if partie and partie.get("heure_fin"):
                    date_fin_str = partie["heure_fin"] # Format: "YYYY-MM-DD HH:MM:S"
                    
                    # Accumulation par filtres temporels
                    if date_fin_str.startswith(str_jour):
                        stats["ca_jour"] += net
                    if date_fin_str.startswith(str_mois):
                        stats["ca_mois"] += net
                    if date_fin_str.startswith(str_annee):
                        stats["ca_annee"] += net

                # Ventilation dynamique par mode de paiement (Orange Money, Espèces, etc.)
                mode = t.get("mode_paiement", "Inconnu")
                # Si le mode de paiement n'est pas encore dans le dictionnaire, on l'initialise à 0
                if mode not in stats["ventilation_modes"]:
                    stats["ventilation_modes"][mode] = 0.0
                # On ajoute le montant net de la transaction au mode de paiement correspondant
                stats["ventilation_modes"][mode] += t.get("montant_net", 0.0)

            # Arrondit les résultats financiers à deux décimales pour éviter les bugs d'affichage flottants
            for cle in ["total_recettes_net", "total_remises_vip", "ca_jour", "ca_mois", "ca_annee"]:
                stats[cle] = round(stats[cle], 2)
            
        except (json.JSONDecodeError, FileNotFoundError):
            # En cas de fichier corrompu, retourne le dictionnaire initialisé à zéro
            return stats

        return stats
