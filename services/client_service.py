# Importation des types de données nécessaires
from typing import List, Optional
# Importation de notre modèle de données Client
from models.client import Client
# Importation du service d'accès aux fichiers de données JSON
from services.sauvegarde_service import SauvegardeService

class ClientService:
    @staticmethod
    def verifier_telephone_existe(telephone: str, liste_clients: List[Client]) -> bool:
        """Parcourt la mémoire pour vérifier si ce numéro de téléphone est déjà attribué."""
        for client in liste_clients:
            if client.telephone == telephone:
                return True  # Doublon détecté, le numéro existe déjà
        return False  # Le numéro est totalement disponible

    @classmethod
    def inscrire_nouveau_client(cls, nom: str, prenom: str, telephone: str, est_vip: bool) -> Optional[Client]:
        """Gère le processus complet d'inscription sécurisée d'un client."""
        # 1. Charge tous les clients actuellement enregistrés sur le disque dur
        clients = SauvegardeService.charger_clients()

        # 2. Sécurité : Empêche l'inscription si le téléphone est déjà utilisé
        if cls.verifier_telephone_existe(telephone, clients):
            print(f"\n❌ Erreur : Un client avec le téléphone {telephone} est déjà inscrit !")
            return None  # Annulation immédiate de l'opération

        # 3. Génération automatique et transparente de l'identifiant unique (ex: CLT0002)
        id_automatique = SauvegardeService.generer_prochain_id_client()

        # 4. Instanciation du nouvel objet métier Client avec les informations validées
        nouveau_client = Client(id_automatique, nom, prenom, telephone, est_vip)

        # 5. Ajout du client à la liste globale du club
        clients.append(nouveau_client)

        # 6. Écriture immédiate dans le fichier data/clients.json pour la persistance
        SauvegardeService.sauvegarder_clients(clients)
        print(f"\n🟢 Succès : {prenom} {nom} a été inscrit avec l'ID {id_automatique} !")
        return nouveau_client

    @staticmethod
    def rechercher_client_par_id(id_recherche: str) -> Optional[Client]:
        """Cherche un client spécifique dans la base de données à partir de son identifiant."""
        # Charge la liste fraîche des clients depuis le fichier JSON
        clients = SauvegardeService.charger_clients()
        
        # Parcourt chaque objet client de la base
        for client in clients:
            # SÉCURITÉ : On transforme l'id en str() au cas où c'est un ancien entier (int)
            id_stocke_str = str(client.id_personne)
            
            # Compare les deux identifiants en majuscules pour éviter les erreurs de casse (clt0001 vs CLT0001)
            if id_stocke_str.upper() == id_recherche.upper():
                return client  # Retourne l'objet client correspondant trouvé
                
        return None  # Aucun client ne possède cet ID

