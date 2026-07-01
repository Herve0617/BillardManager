import sys
from datetime import datetime
from ui.saisie import Saisie
from models.enums import TypeBillard, ModePaiement
from services.table_service import TableService
from services.partie_service import PartieService
from services.client_service import ClientService
from services.sauvegarde_service import SauvegardeService
from services.paiement_service import PaiementService
from services.statistique_service import StatistiqueService
from utils.constantes import DEVISE

class Menu:
    # On simule l'employé connecté par défaut sur la console
    EMPLOYE_CONNECTE = "EMP0001"

    @classmethod
    def afficher_menu_principal(cls):
        """Menu racine du logiciel."""
        while True:
            # Remplacement de Affichage par des prints propres et autonomes
            print("\n" + "="*50)
            print(" MENU PRINCIPAL - BILLARD MANAGER ".center(50, "="))
            print("="*50)
            print("1. 👥 Gérer les Clients")
            print("2. 🎱 Gérer les Tables de Billard")
            print("3. 🕹️ Sessions de Jeu (Lancer / Clôturer)")
            print("4. 📊 Tableau de Bord & Statistiques")
            print("5. 🚪 Quitter l'application")

            choix = Saisie.saisir_entier("\nVotre choix (1-5) : ")
            if choix == 1:
                cls.sous_menu_clients()
            elif choix == 2:
                cls.sous_menu_tables()
            elif choix == 3:
                cls.sous_menu_parties()
            elif choix == 4:
                cls.afficher_statistiques_club()
            elif choix == 5:
                print("\n👋 Au revoir !")
                sys.exit()

    @classmethod
    def afficher_statistiques_club(cls):
        """Affiche un bilan comptable complet et propre sur la console pour le gérant."""
        print("\n" + "="*50)
        print(" TABLEAU DE BORD FINANCIER ".center(50, "="))
        print("="*50)
        
        rapport = StatistiqueService.generer_rapport_financier()

        print(f"📈 Nombre total de transactions : {rapport['nombre_transactions']}")
        print(f"💰 Chiffre d'Affaires Net Global : {rapport['total_recettes_net']} {DEVISE}")
        print(f"🎁 Total des remises accordées : {rapport['total_remises_vip']} {DEVISE}")
        
        print("\n💳 Ventilation des recettes par mode d'encaissement :")
        print("-" * 45)
        
        if not rapport["ventilation_modes"]:
            print("  ➡️ Aucune recette enregistrée pour le moment.")
        else:
            for mode, montant in rapport["ventilation_modes"].items():
                print(f"  • {mode:<20} : {round(montant, 2):>10} {DEVISE}")
        print("-" * 45)
        
        input("\nAppuyez sur [Entrée] pour retourner au menu principal...")

    @classmethod
    def sous_menu_parties(cls):
        """Gère l'aiguillage entre l'ouverture d'une table et l'encaissement d'une facture."""
        while True:
            print("\n--- GESTION DES SESSIONS DE JEU ---")
            print("1. 🟢 Ouvrir une table (Lancer une partie)")
            print("2. 🔴 Clôturer une table (Calculer la facture & Libérer)")
            print("3. ↩️ Retour au menu principal")

            choix = Saisie.saisir_entier("\nVotre choix (1-3) : ")
            if choix == 1:
                cls.lancer_session_jeu()
            elif choix == 2:
                cls.cloturer_session_jeu()
            elif choix == 3:
                break

    @classmethod
    def lancer_session_jeu(cls):
        """Assigne une table vide à un joueur identifié."""
        print("\n--- OUVERTURE D'UNE TABLE ---")
        id_recherche = Saisie.saisir_texte("Entrez l'ID du client (ex: CLT0001) : ")
        client = ClientService.rechercher_client_par_id(id_recherche)
        if not client:
            print("❌ Aucun client trouvé avec cet ID.")
            return

        type_b = Saisie.choisir_enum(TypeBillard, "Type de billard souhaité")
        tables_libres = PartieService.obtenir_tables_libres_par_type(type_b)

        if not tables_libres:
            print(f"❌ Plus de tables disponibles pour le type '{type_b.value}'.")
            return

        print(f"\nTables libres pour [{type_b.value}] :")
        for t in tables_libres:
            print(f" -> Table N°{t.numero}")

        while True:
            num_choisi = Saisie.saisir_entier("\nAttribuer la table N° : ")
            table_choisie = next((t for t in tables_libres if t.numero == num_choisi), None)
            if table_choisie:
                break
            print("❌ Numéro incorrect ou table indisponible.")

        PartieService.démarrer_partie(client, table_choisie)
        print(f"\n🎯 Chronomètre lancé ! Table N°{table_choisie.numero} occupée par {client.prenom}.")

    @classmethod
    def cloturer_session_jeu(cls):
        """Arrête le chrono d'une table, effectue les calculs et génère le ticket de caisse."""
        print("\n--- CLÔTURE DE TABLE & FACTURATION ---")
        parties_actives = PartieService.obtenir_parties_actives()

        if not parties_actives:
            print("\n📭 Aucune table n'est occupée actuellement dans le club.")
            return

        print("\nSessions en cours d'exécution :")
        for p in parties_actives:
            print(f" -> Partie N°{p['id_partie']} | Client: {p['id_client']} | Table N°{p['numero_table']} | Début: {p['heure_debut']}")

        while True:
            id_p_choisi = Saisie.saisir_entier("\nEntrez le numéro de la partie à clôturer : ")
            partie_cible = next((p for p in parties_actives if p["id_partie"] == id_p_choisi), None)
            if partie_cible:
                break
            print("❌ Numéro de partie introuvable.")

        heure_debut_obj = datetime.strptime(partie_cible["heure_debut"], "%Y-%m-%d %H:%M:%S")
        heure_fin_obj = datetime.now()
        duree_secondes = (heure_fin_obj - heure_debut_obj).total_seconds()
        duree_reelle_heures = duree_secondes / 3600

        if duree_secondes < 60:
            print("\n💡 [Mode Démo] La partie vient à peine de commencer (moins d'une minute).")
            duree_heures = Saisie.saisir_flottant("Combien d'heures de jeu voulez-vous simuler ? (ex: 2.5) : ")
        else:
            duree_heures = duree_reelle_heures

        client = ClientService.rechercher_client_par_id(partie_cible["id_client"])
        toutes_tables = SauvegardeService.charger_tables()
        table = next((t for t in toutes_tables if t.numero == partie_cible["numero_table"]), None)

        mode_p = Saisie.choisir_enum(ModePaiement, "Mode de règlement")

        facture = PaiementService.generer_facture(
            id_partie=partie_cible["id_partie"],
            tarif_horaire=table.tarif_horaire,
            duree_heures=duree_heures,
            est_vip=client.est_vip,
            mode=mode_p,
            id_employe=cls.EMPLOYE_CONNECTE
        )

        PartieService.cloturer_partie_en_base(partie_cible["id_partie"], heure_fin_obj.strftime("%Y-%m-%d %H:%M:%S"))

        # --- AJOUT DES LIGNES MANQUANTES : Impression propre du ticket ---
        print("\n" + "="*40)
        print(f"🧾 REÇU DE CAISSE N°{facture['id_paiement']}".center(40))
        print("="*40)
        print(f"Client        : {client.prenom} {client.nom} ({'VIP' if client.est_vip else 'Standard'})")
        print(f"Table libérée : N°{table.numero} ({table.type_billard.value})")
        print(f"Temps de jeu  : {facture['duree_heures']} heure(s)")
        print(f"Prix Brut     : {facture['montant_brut']} {DEVISE}")
        print(f"Remise accordée: {facture['remise_vip']} {DEVISE}")
        print("-" * 40)
        print(f" NET À PAYER  : {facture['montant_net']} {DEVISE}")
        print(f"Règlement via : {facture['mode_paiement']}")
        print(f"Encaissé par  : {facture['id_employe']}")
        print("="*40)
        print("✨ Table de nouveau disponible ! ✨\n")

    @classmethod
    def sous_menu_clients(cls):
        """Sous-menu de consultation et d'ajout de clients."""
        while True:
            print("\n--- GESTION DES CLIENTS ---")
            print("1. 📜 Afficher la liste de tous les clients")
            print("2. ➕ Inscrire un nouveau client")
            print("3. ↩️ Retour")
            
            choix = Saisie.saisir_entier("\nVotre choix (1-3) : ")
            if choix == 1:
                clients = SauvegardeService.charger_clients()
                print("\n--- LISTE DES CLIENTS INSCRITS ---")
                if not clients:
                    print("📭 Aucun client enregistré.")
                for c in clients:
                    statut = "VIP" if c.est_vip else "Standard"
                    print(f"ID: {c.id_personne} | Nom: {c.nom} {c.prenom} | Tél: {c.telephone} | [{statut}]")
            elif choix == 2:
                nom = Saisie.saisir_texte("Nom : ")
                prenom = Saisie.saisir_texte("Prénom : ")
                tel = Saisie.saisir_telephone("Téléphone : ")
                vip = input("VIP ? (o/n) : ").lower().strip() == 'o'
                ClientService.inscrire_nouveau_client(nom, prenom, tel, vip)
            elif choix == 3:
                break

    @classmethod
    def sous_menu_tables(cls):
        """Sous-menu d'administration du parc informatique."""
        while True:
            print("\n--- GESTION DES TABLES ---")
            print("1. 📜 Afficher l'état en direct des tables")
            print("2. ➕ Enregistrer une nouvelle table")
            print("3. ↩️ Retour")

            choix = Saisie.saisir_entier("\nVotre choix (1-3) : ")
            if choix == 1:
                tables = SauvegardeService.charger_tables()
                print("\n--- ÉTAT DES TABLES DU CLUB ---")
                if not tables:
                    print("📭 Aucune table configurée.")
                for t in tables:
                    dispo = "🔴 OCCUPÉE" if t.est_occupee else "🟢 DISPONIBLE"
