import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Importations des contrôleurs et modèles métiers
from services.sauvegarde_service import SauvegardeService
from services.table_service import TableService
from services.client_service import ClientService
from services.partie_service import PartieService
from services.paiement_service import PaiementService
from services.statistique_service import StatistiqueService
from models.enums import TypeBillard, ModePaiement
from utils.constantes import DEVISE

class BillardManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎱 Billard Manager v3.0 - Karpala Club")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e1e")

        # Session de l'employé connecté par défaut
        self.employe_connecte = {"id": "EMP0001", "nom": "Zoungrana Pierre"}

        # Style graphique unifié (Thème sombre)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TPanedwindow", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Helvetica", 11))
        self.style.configure("TButton", background="#2b5c8f", foreground="#ffffff", borderwidth=0, font=("Helvetica", 10, "bold"))
        self.style.map("TButton", background=[("active", "#1f446b")])
        self.style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#2d2d2d", foreground="#ffffff", font=("Helvetica", 10, "bold"), padding=8)
        self.style.map("TNotebook.Tab", background=[("selected", "#2b5c8f")], foreground=[("selected", "#ffffff")])

        # Barre supérieure (Profil employé connecté)
        self.creer_barre_statut()

        # Menu à onglets étendu pour couvrir TOUTES les fonctionnalités
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Création des 4 panneaux applicatifs majeurs
        self.onglet_tables = ttk.Frame(self.notebook)
        self.onglet_parties = ttk.Frame(self.notebook)
        self.onglet_clients = ttk.Frame(self.notebook)
        self.onglet_stats = ttk.Frame(self.notebook)
        
        # Injection des onglets dans le conteneur principal
        self.notebook.add(self.onglet_tables, text=" 🎱 Tables de Billard ")
        self.notebook.add(self.onglet_parties, text=" 🕹️ Sessions de Jeu ")
        self.notebook.add(self.onglet_clients, text=" 👥 Gestion des Clients ")
        self.notebook.add(self.onglet_stats, text=" 📊 Tableau de Bord ")

        # Construction des interfaces graphiques respectives
        self.construire_onglet_tables()
        self.construire_onglet_parties()
        self.construire_onglet_clients()
        self.construire_onglet_stats()

    def creer_barre_statut(self):
        """Affiche l'en-tête de traçabilité de l'employé et le bouton de fermeture."""
        barre = tk.Frame(self.root, bg="#2d2d2d", height=45)
        barre.pack(fill="x", side="top")
        
        # Bouton Quitter (Fonctionnalité 5)
        btn_quitter = tk.Button(barre, text="🚪 Quitter", bg="#a33b3b", fg="#ffffff", font=("Helvetica", 9, "bold"), 
                                borderwidth=0, padx=10, command=self.root.quit)
        btn_quitter.pack(side="left", padx=15, pady=8)

        lbl = tk.Label(barre, text=f"👤 En service : {self.employe_connecte['nom']} ({self.employe_connecte['id']})", 
                       bg="#2d2d2d", fg="#88ff88", font=("Helvetica", 10, "bold"))
        lbl.pack(side="right", padx=15, pady=10)

    # ==========================================
    # FUNCTIONALITÉ 2 : GESTION DES TABLES
    # ==========================================
    def construire_onglet_tables(self):
        lbl_titre = ttk.Label(self.onglet_tables, text="Suivi en direct du parc de tables", font=("Helvetica", 14, "bold"))
        lbl_titre.pack(pady=10)

        # Formulaire d'ajout rapide de table au parc informatique
        cadre_ajout = tk.LabelFrame(self.onglet_tables, text=" ➕ Acheter / Enregistrer une nouvelle table ", bg="#1e1e1e", fg="#ffffff", padx=10, pady=10)
        cadre_ajout.pack(fill="x", padx=20, pady=5)

        ttk.Label(cadre_ajout, text="N° Table :").grid(row=0, column=0, padx=5)
        self.entry_num_table = ttk.Entry(cadre_ajout, width=8)
        self.entry_num_table.grid(row=0, column=1, padx=5)

        ttk.Label(cadre_ajout, text="Type :").grid(row=0, column=2, padx=5)
        self.combo_new_table_type = ttk.Combobox(cadre_ajout, values=[t.value for t in TypeBillard], state="readonly", width=12)
        self.combo_new_table_type.current(0)
        self.combo_new_table_type.grid(row=0, column=3, padx=5)

        btn_add_table = ttk.Button(cadre_ajout, text="Ajouter au Club", command=self.action_ajouter_table)
        btn_add_table.grid(row=0, column=4, padx=15)

        # Tableau d'affichage du parc
        colonnes = ("numero", "type", "tarif", "statut")
        self.tree_tables = ttk.Treeview(self.onglet_tables, columns=colonnes, show="headings", height=12)
        self.tree_tables.heading("numero", text="N° Table")
        self.tree_tables.heading("type", text="Type de Billard")
        self.tree_tables.heading("tarif", text="Tarif Horaire")
        self.tree_tables.heading("statut", text="État Disponibilité")
        self.tree_tables.pack(expand=True, fill="both", padx=20, pady=10)

        btn_refresh = ttk.Button(self.onglet_tables, text="🔄 Actualiser la vue", command=self.actualiser_tables)
        btn_refresh.pack(pady=5)
        self.actualiser_tables()

    def action_ajouter_table(self):
        """Prend en compte l'ajout d'une nouvelle table avec détection de doublon."""
        try:
            num = int(self.entry_num_table.get().strip())
        except ValueError:
            messagebox.showerror("Saisie Incorrecte", "Le numéro de table doit être un entier numérique.")
            return

        type_enum = TypeBillard(self.combo_new_table_type.get())
        
        # Exécution via le TableService qui gère les règles métiers
        if TableService.ajouter_nouvelle_table(num, type_enum):
            messagebox.showinfo("Succès", f"La table N°{num} a été ajoutée à la base.")
            self.entry_num_table.delete(0, tk.END)
            self.actualiser_tables()
        else:
            messagebox.showerror("Doublon", f"Le numéro de table {num} est déjà utilisé.")

    def actualiser_tables(self):
        for row in self.tree_tables.get_children():
            self.tree_tables.delete(row)
        tables = SauvegardeService.charger_tables()
        for t in tables:
            dispo = "🔴 OCCUPÉE" if t.est_occupee else "🟢 DISPONIBLE"
            self.tree_tables.insert("", "end", values=(t.numero, t.type_billard.value, f"{t.tarif_horaire} {DEVISE}/h", dispo))

    # ==========================================
    # FONCTIONNALITÉ 3 : INTERFACE SESSIONS DE JEU
    # ==========================================
    def construire_onglet_parties(self):
        cadre_form = tk.LabelFrame(self.onglet_parties, text=" 🟢 Lancer une Session de Jeu ", bg="#1e1e1e", fg="#ffffff", padx=15, pady=15, font=("Helvetica", 11, "bold"))
        cadre_form.pack(fill="x", padx=20, pady=10)

        ttk.Label(cadre_form, text="ID Client :").grid(row=0, column=0, padx=5, sticky="w")
        self.entry_id_client = ttk.Entry(cadre_form, width=15)
        self.entry_id_client.grid(row=0, column=1, padx=5)

        ttk.Label(cadre_form, text="Type Billard :").grid(row=0, column=2, padx=5, sticky="w")
        self.combo_type = ttk.Combobox(cadre_form, values=[t.value for t in TypeBillard], state="readonly", width=15)
        self.combo_type.current(0)
        self.combo_type.grid(row=0, column=3, padx=5)

        btn_lancer = ttk.Button(cadre_form, text="🚀 Ouvrir la Table", command=self.action_ouvrir_table)
        btn_lancer.grid(row=0, column=4, padx=20)

        cadre_cloture = tk.LabelFrame(self.onglet_parties, text=" 🔴 Sessions de Jeu en Cours ", bg="#1e1e1e", fg="#ffffff", padx=15, pady=15, font=("Helvetica", 11, "bold"))
        cadre_cloture.pack(expand=True, fill="both", padx=20, pady=10)

        cols_parties = ("id_partie", "id_client", "num_table", "heure_debut")
        self.tree_parties = ttk.Treeview(cadre_cloture, columns=cols_parties, show="headings", height=8)
        self.tree_parties.heading("id_partie", text="N° Session")
        self.tree_parties.heading("id_client", text="Identifiant Client")
        self.tree_parties.heading("num_table", text="Table Affectée")
        self.tree_parties.heading("heure_debut", text="Heure de Début")
        self.tree_parties.pack(expand=True, fill="both", pady=10)

        zone_outils = tk.Frame(cadre_cloture, bg="#1e1e1e")
        zone_outils.pack(fill="x", pady=5)

        ttk.Label(zone_outils, text="Règlement :").pack(side="left", padx=5)
        self.combo_mode = ttk.Combobox(zone_outils, values=[m.value for m in ModePaiement], state="readonly", width=18)
        self.combo_mode.current(0)
        self.combo_mode.pack(side="left", padx=5)

        btn_cloturer = ttk.Button(zone_outils, text="🧾 Encaisser & Libérer", command=self.action_cloturer_table)
        btn_cloturer.pack(side="right", padx=5)

        self.actualiser_parties_actives()

    def actualiser_parties_actives(self):
        for row in self.tree_parties.get_children():
            self.tree_parties.delete(row)
        parties = PartieService.obtenir_parties_actives()
        for p in parties:
            self.tree_parties.insert("", "end", values=(p["id_partie"], p["id_client"], f"Table N°{p['numero_table']}", p["heure_debut"]))

    def action_ouvrir_table(self):
        id_c = self.entry_id_client.get().strip()
        type_str = self.combo_type.get()
        
        client = ClientService.rechercher_client_par_id(id_c)
        if not client:
            messagebox.showerror("Client Introuvable", f"L'identifiant '{id_c}' n'existe pas.")
            return

        type_enum = TypeBillard(type_str)
        tables_libres = PartieService.obtenir_tables_libres_par_type(type_enum)

        if not tables_libres:
            messagebox.showwarning("Club Saturé", f"Toutes les tables '{type_str}' sont occupées.")
            return

        # 2. Attribution de la première table disponible et lancement
        table_attribuee = tables_libres[0]
        PartieService.démarrer_partie(client, table_attribuee)
        
        messagebox.showinfo(
            "Chrono Lancé", 
            f"Table N°{table_attribuee.numero} affectée à {client.prenom} {client.nom}."
        )
        
        # 3. Réinitialisation des composants visuels d'ouverture
        self.entry_id_client.delete(0, tk.END)
        self.actualiser_tables()
        self.actualiser_parties_actives()

    def action_cloturer_table(self):
        """Calcule la facture d'une table occupée et la libère en base."""
        selection = self.tree_parties.selection()
        if not selection:
            messagebox.showwarning("Sélection Requise", "Veuillez sélectionner une session active.")
            return

        # Extraction des valeurs cibles depuis la ligne du tableau graphique
        valeurs_ligne = self.tree_parties.item(selection, "values")
        id_partie = int(valeurs_ligne[0])
        id_client = valeurs_ligne[1]
        num_table = int(valeurs_ligne[2].replace("Table N°", ""))

        # Récupération des instances d'objets métiers correspondantes
        client = ClientService.rechercher_client_par_id(id_client)
        toutes_tables = SauvegardeService.charger_tables()
        table = next((t for t in toutes_tables if t.numero == num_table), None)
        mode_paiement_enum = ModePaiement(self.combo_mode.get())

        # Analyse temporelle de la session de jeu
        parties_actives = PartieService.obtenir_parties_actives()
        partie_dict = next((p for p in parties_actives if p["id_partie"] == id_partie), None)
        
        heure_debut_obj = datetime.strptime(partie_dict["heure_debut"], "%Y-%m-%d %H:%M:%S")
        heure_fin_obj = datetime.now()
        duree_heures = (heure_fin_obj - heure_debut_obj).total_seconds() / 3600

        # Ajustement automatique pour les besoins de la démonstration pédagogique
        if duree_heures < 0.02:
            duree_heures = 1.5  

        # Enregistrement comptable de la transaction
        facture = PaiementService.generer_facture(
            id_partie=id_partie,
            tarif_horaire=table.tarif_horaire,
            duree_heures=duree_heures,
            est_vip=client.est_vip,
            mode=mode_paiement_enum,
            id_employe=self.employe_connecte["id"]
        )

        # Fermeture de la session informatique et libération de la table physique
        PartieService.cloturer_partie_en_base(id_partie, heure_fin_obj.strftime("%Y-%m-%d %H:%M:%S"))

        # Structuration de la mise en page textuelle du reçu de caisse
        ticket_texte = (
            f"========================================\n"
            f"             RECEPISSE DE PAIEMENT      \n"
            f"========================================\n"
            f" Ticket N° : RECU_00{facture['id_paiement']}\n"
            f" Caissier  : {self.employe_connecte['nom']}\n"
            f" Client    : {client.prenom} {client.nom} ({'VIP' if client.est_vip else 'Standard'})\n"
            f" Table     : N°{table.numero} ({table.type_billard.value})\n"
            f" Durée     : {facture['duree_heures']} heure(s)\n"
            f"----------------------------------------\n"
            f" Montant Brut : {facture['montant_brut']} {DEVISE}\n"
            f" Remise VIP   : -{facture['remise_vip']} {DEVISE}\n"
            f" NET A PAYER  : {facture['montant_net']} {DEVISE}\n"
            f"----------------------------------------\n"
            f" Mode de Règlement : {facture['mode_paiement']}\n"
            f"========================================\n"
        )
        
        # Affichage du ticket à l'écran et rafraîchissement global à chaud
        messagebox.showinfo("💵 ENCAISSEMENT EFFECTUÉ", ticket_texte)
        self.actualiser_tables()
        self.actualiser_parties_actives()
        self.actualiser_stats()

    # ==========================================
    # FONCTIONNALITÉ 1 : GESTION DES CLIENTS
    # ==========================================
    def construire_onglet_clients(self):
        """Génère le panneau d'inscription et le répertoire graphique des clients."""
        lbl_titre = ttk.Label(self.onglet_clients, text="Formulaire d'Inscription et Répertoire", font=("Helvetica", 14, "bold"))
        lbl_titre.pack(pady=10)

        # Formulaire d'inscription (Labels et zones de saisies textuelles)
        cadre_c = tk.LabelFrame(self.onglet_clients, text=" ➕ Inscrire un Nouveau Client ", bg="#1e1e1e", fg="#ffffff", padx=10, pady=10)
        cadre_c.pack(fill="x", padx=20, pady=5)

        ttk.Label(cadre_c, text="Nom :").grid(row=0, column=0, padx=5, pady=5)
        self.entry_c_nom = ttk.Entry(cadre_c, width=15)
        self.entry_c_nom.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(cadre_c, text="Prénom :").grid(row=0, column=2, padx=5, pady=5)
        self.entry_c_prenom = ttk.Entry(cadre_c, width=15)
        self.entry_c_prenom.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(cadre_c, text="Téléphone :").grid(row=0, column=4, padx=5, pady=5)
        self.entry_c_tel = ttk.Entry(cadre_c, width=12)
        self.entry_c_tel.grid(row=0, column=5, padx=5, pady=5)

        # Case à cocher booléenne pour le statut d'éligibilité aux remises VIP
        self.vip_var = tk.BooleanVar()
        self.chk_vip = tk.Checkbutton(cadre_c, text="Membre VIP", variable=self.vip_var, bg="#1e1e1e", fg="#ffffff", selectcolor="#2d2d2d")
        self.chk_vip.grid(row=0, column=6, padx=10, pady=5)

        btn_add_client = ttk.Button(cadre_c, text="Inscrire", command=self.action_inscrire_client)
        btn_add_client.grid(row=0, column=7, padx=10, pady=5)

        # Grille de visualisation (Treeview) du répertoire client
        cols_c = ("id", "nom", "prenom", "tel", "statut")
        self.tree_clients = ttk.Treeview(self.onglet_clients, columns=cols_c, show="headings", height=12)
        self.tree_clients.heading("id", text="ID")
        self.tree_clients.heading("nom", text="Nom de Famille")
        self.tree_clients.heading("prenom", text="Prénom")
        self.tree_clients.heading("tel", text="N° Téléphone")
        self.tree_clients.heading("statut", text="Type Adhésion")
        self.tree_clients.pack(expand=True, fill="both", padx=20, pady=10)

        self.actualiser_clients()

    def action_inscrire_client(self):
        """Valide et enregistre un nouveau client dans le fichier JSON."""
        nom = self.entry_c_nom.get().strip()
        prenom = self.entry_c_prenom.get().strip()
        tel = self.entry_c_tel.get().strip()
        vip = self.vip_var.get()

        # Contrôle de sécurité contre les entrées vides
        if not nom or not prenom or not tel:
            messagebox.showerror("Champs Vides", "Veuillez remplir toutes les informations personnelles.")
            return

        # Appel du service d'inscription
        if ClientService.inscrire_nouveau_client(nom, prenom, tel, vip):
            messagebox.showinfo("Inscrit", f"Client ajouté au répertoire avec succès !")
            # Vider les champs du formulaire après la validation
            self.entry_c_nom.delete(0, tk.END)
            self.entry_c_prenom.delete(0, tk.END)
            self.entry_c_tel.delete(0, tk.END)
            self.vip_var.set(False)
            self.actualiser_clients()
        else:
            messagebox.showerror("Doublon", "Ce numéro de téléphone est déjà attribué.")

    def actualiser_clients(self):
        """Recharge et affiche la liste des clients à jour."""
        for row in self.tree_clients.get_children():
            self.tree_clients.delete(row)
        clients = SauvegardeService.charger_clients()
        for c in clients:
            statut = "⭐ Membre VIP" if c.est_vip else "Standard"
            self.tree_clients.insert("", "end", values=(c.id_personne, c.nom, c.prenom, c.telephone, statut))

    # ==========================================
    # FONCTIONNALITÉ 4 : TABLEAU DE BORD & STATS
    # ==========================================
    def construire_onglet_stats(self):
        """Génère l'onglet comptable pour le suivi des performances financières."""
        lbl_titre = ttk.Label(self.onglet_stats, text="Indicateurs Financiers Globaux du Club", font=("Helvetica", 14, "bold"))
        lbl_titre.pack(pady=15)

        # Cartes d'indicateurs comptables
        self.cadre_indicateurs = tk.Frame(self.onglet_stats, bg="#1e1e1e")
        self.cadre_indicateurs.pack(fill="x", padx=40, pady=10)

        self.lbl_tx = ttk.Label(self.cadre_indicateurs, text="Transactions : 0", font=("Helvetica", 12, "bold"))
        self.lbl_tx.pack(anchor="w", pady=5)

        self.lbl_ca = ttk.Label(self.cadre_indicateurs, text="Chiffre d'Affaires : 0 FCFA", font=("Helvetica", 12, "bold"))
        self.lbl_ca.pack(anchor="w", pady=5)

        self.lbl_remise = ttk.Label(self.cadre_indicateurs, text="Remises Offertes : 0 FCFA", font=("Helvetica", 12, "bold"))
        self.lbl_remise.pack(anchor="w", pady=5)

        btn_refresh_stats = ttk.Button(self.onglet_stats, text="🔄 Actualiser la Comptabilité", command=self.actualiser_stats)
        btn_refresh_stats.pack(pady=20)
        
        self.actualiser_stats()

    def actualiser_stats(self):
        """Calcule à chaud et met à jour l'affichage des valeurs financières."""
        rapport = StatistiqueService.generer_rapport_financier()
        
        # 2. Mise à jour dynamique des étiquettes (Labels) de l'interface graphique
        
        self.lbl_tx.config(text=f"📈 Nombre total de transactions traitées : {rapport['nombre_transactions']}")
        self.lbl_ca.config(text=f"💰 Chiffre d'Affaires Net Encaissé : {rapport['total_recettes_net']} {DEVISE}")
        self.lbl_remise.config(text=f"🎁 Total des avantages accordés aux VIP : {rapport['total_remises_vip']} {DEVISE}")
