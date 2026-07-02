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
from services.reservation_service import ReservationService
from models.enums import TypeBillard, ModePaiement
from utils.constantes import DEVISE
from utils.validators import Validators

class BillardManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎱 Billard Manager v3.0 - Karpala Club")
        self.root.geometry("1100x750")
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

        # Création des 5 panneaux applicatifs majeurs
        self.onglet_tables = ttk.Frame(self.notebook)
        self.onglet_parties = ttk.Frame(self.notebook)
        self.onglet_clients = ttk.Frame(self.notebook)
        self.onglet_reservations = ttk.Frame(self.notebook)
        self.onglet_stats = ttk.Frame(self.notebook)
        
        # Injection des onglets dans le conteneur principal
        self.notebook.add(self.onglet_tables, text=" 🎱 Tables de Billard ")
        self.notebook.add(self.onglet_parties, text=" 🕹️ Sessions de Jeu ")
        self.notebook.add(self.onglet_clients, text=" 👥 Gestion des Clients ")
        self.notebook.add(self.onglet_reservations, text=" 📅 Réservations ")
        self.notebook.add(self.onglet_stats, text=" 📊 Tableau de Bord ")

        # Construction des interfaces graphiques respectives
        self.construire_onglet_tables()
        self.construire_onglet_parties()
        self.construire_onglet_clients()
        self.construire_onglet_reservations()
        self.construire_onglet_stats()

    def creer_barre_statut(self):
        """Affiche l'en-tête de traçabilité de l'employé et le bouton de fermeture."""
        barre = tk.Frame(self.root, bg="#2d2d2d", height=45)
        barre.pack(fill="x", side="top")
        
        btn_quitter = tk.Button(barre, text="🚪 Quitter", bg="#a33b3b", fg="#ffffff", font=("Helvetica", 9, "bold"), 
                                borderwidth=0, padx=10, command=self.root.quit)
        btn_quitter.pack(side="left", padx=15, pady=8)

        lbl = tk.Label(barre, text=f"👤 En service : {self.employe_connecte['nom']} ({self.employe_connecte['id']})", 
                       bg="#2d2d2d", fg="#88ff88", font=("Helvetica", 10, "bold"))
        lbl.pack(side="right", padx=15, pady=10)

    # ==========================================
    # FONCTIONNALITÉ : GESTION DES TABLES
    # ==========================================
    def construire_onglet_tables(self):
        lbl_titre = ttk.Label(self.onglet_tables, text="Suivi en direct du parc de tables", font=("Helvetica", 14, "bold"))
        lbl_titre.pack(pady=10)

        # Formulaire d'ajout
        cadre_ajout = tk.LabelFrame(self.onglet_tables, text=" ➕ Enregistrer une nouvelle table ", bg="#1e1e1e", fg="#ffffff", padx=10, pady=10)
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

        # Outils de gestion en bas du tableau
        zone_outils = tk.Frame(self.onglet_tables, bg="#1e1e1e")
        zone_outils.pack(fill="x", padx=20, pady=5)

        btn_refresh = ttk.Button(zone_outils, text="🔄 Actualiser la vue", command=self.actualiser_tables)
        btn_refresh.pack(side="left", padx=5)

        btn_delete_table = tk.Button(zone_outils, text="🗑️ Supprimer la Table sélectionnée", bg="#a33b3b", fg="#ffffff", 
                                     font=("Helvetica", 10, "bold"), borderwidth=0, padx=10, pady=5, command=self.action_supprimer_table)
        btn_delete_table.pack(side="right", padx=5)

        self.actualiser_tables()

    def action_ajouter_table(self):
        try:
            num = int(self.entry_num_table.get().strip())
        except ValueError:
            messagebox.showerror("Saisie Incorrecte", "Le numéro de table doit être un entier numérique.")
            return

        type_enum = TypeBillard(self.combo_new_table_type.get())
        
        if TableService.ajouter_nouvelle_table(num, type_enum):
            messagebox.showinfo("Succès", f"La table N°{num} a été ajoutée à la base.")
            self.entry_num_table.delete(0, tk.END)
            self.actualiser_tables()
        else:
            messagebox.showerror("Doublon", f"Le numéro de table {num} est déjà utilisé.")

    def action_supprimer_table(self):
        selection = self.tree_tables.selection()
        if not selection:
            messagebox.showwarning("Sélection Requise", "Veuillez sélectionner une table dans la liste pour la supprimer.")
            return
        
        valeurs = self.tree_tables.item(selection, "values")
        num_table = int(valeurs[0])

        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer la table N°{num_table} du parc ?"):
            TableService.supprimer_table(num_table)
            messagebox.showinfo("Supprimée", f"La table N°{num_table} a été retirée.")
            self.actualiser_tables()

    def actualiser_tables(self):
        for row in self.tree_tables.get_children():
            self.tree_tables.delete(row)
        tables = SauvegardeService.charger_tables()
        for t in tables:
            dispo = "🔴 OCCUPÉE" if t.est_occupee else "🟢 DISPONIBLE"
            self.tree_tables.insert("", "end", values=(t.numero, t.type_billard.value, f"{t.tarif_horaire} {DEVISE}/h", dispo))

    # ==========================================
    # FONCTIONNALITÉ : INTERFACE SESSIONS DE JEU
    # ==========================================
    def construire_onglet_parties(self):
        """Construit le panneau de commande d'ouverture et fermeture de table."""
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

        table_attribuee = tables_libres[0]
        PartieService.démarrer_partie(client, table_attribuee)
        
        messagebox.showinfo("Chrono Lancé", f"Table N°{table_attribuee.numero} affectée à {client.prenom} {client.nom}.")
        self.entry_id_client.delete(0, tk.END)
        self.actualiser_tables()
        self.actualiser_parties_actives()

    def action_cloturer_table(self):
        selection = self.tree_parties.selection()
        if not selection:
            messagebox.showwarning("Sélection Requise", "Veuillez sélectionner une session active.")
            return

        valeurs_ligne = self.tree_parties.item(selection, "values")
        id_partie = int(valeurs_ligne[0])
        id_client = valeurs_ligne[1]
        num_table = int(valeurs_ligne[2].replace("Table N°", ""))

        client = ClientService.rechercher_client_par_id(id_client)
        toutes_tables = SauvegardeService.charger_tables()
        table = next((t for t in toutes_tables if t.numero == num_table), None)
        mode_paiement_enum = ModePaiement(self.combo_mode.get())

        parties_actives = PartieService.obtenir_parties_actives()
        partie_dict = next((p for p in parties_actives if p["id_partie"] == id_partie), None)
        
        heure_debut_obj = datetime.strptime(partie_dict["heure_debut"], "%Y-%m-%d %H:%M:%S")
        heure_fin_obj = datetime.now()
        duree_heures = (heure_fin_obj - heure_debut_obj).total_seconds() / 3600

        if duree_heures < 0.02:
            duree_heures = 1.5  # Forfait mode démo automatique

        facture = PaiementService.generer_facture(
            id_partie=id_partie,
            tarif_horaire=table.tarif_horaire,
            duree_heures=duree_heures,
            est_vip=client.est_vip,
            mode=mode_paiement_enum,
            id_employe=self.employe_connecte["id"]
        )

        PartieService.cloturer_partie_en_base(id_partie, heure_fin_obj.strftime("%Y-%m-%d %H:%M:%S"))

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
        
        messagebox.showinfo("💵 ENCAISSEMENT EFFECTUÉ", ticket_texte)
        self.actualiser_tables()
        self.actualiser_parties_actives()
        self.actualiser_stats()

    # ==========================================
    # FONCTIONNALITÉ : GESTION DES CLIENTS
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

        self.vip_var = tk.BooleanVar()
        self.chk_vip = tk.Checkbutton(cadre_c, text="Membre VIP", variable=self.vip_var, bg="#1e1e1e", fg="#ffffff", selectcolor="#2d2d2d")
        self.chk_vip.grid(row=0, column=6, padx=10, pady=5)

        btn_add_client = ttk.Button(cadre_c, text="Inscrire", command=self.action_inscrire_client)
        btn_add_client.grid(row=0, column=7, padx=10, pady=5)

        # Grille de visualisation du répertoire client
        cols_c = ("id", "nom", "prenom", "tel", "statut")
        self.tree_clients = ttk.Treeview(self.onglet_clients, columns=cols_c, show="headings", height=12)
        self.tree_clients.heading("id", text="ID Client")
        self.tree_clients.heading("nom", text="Nom de Famille")
        self.tree_clients.heading("prenom", text="Prénom")
        self.tree_clients.heading("tel", text="N° Téléphone")
        self.tree_clients.heading("statut", text="Type Adhésion")
        self.tree_clients.pack(expand=True, fill="both", padx=20, pady=10)

        # Zone d'outils de suppression en bas du tableau
        zone_c_outils = tk.Frame(self.onglet_clients, bg="#1e1e1e")
        zone_c_outils.pack(fill="x", padx=20, pady=5)

        btn_del_client = tk.Button(zone_c_outils, text="🗑️ Supprimer le Client sélectionné", bg="#a33b3b", fg="#ffffff", 
                                   font=("Helvetica", 10, "bold"), borderwidth=0, padx=10, pady=5, command=self.action_supprimer_client)
        btn_del_client.pack(side="right")

        self.actualiser_clients()

    def action_inscrire_client(self):
        """Valide la conformité du téléphone et enregistre le client."""
        nom = self.entry_c_nom.get().strip()
        prenom = self.entry_c_prenom.get().strip()
        tel = self.entry_c_tel.get().strip()
        vip = self.vip_var.get()

        if not nom or not prenom or not tel:
            messagebox.showerror("Champs Vides", "Veuillez remplir toutes les informations personnelles.")
            return

        # SÉCURITÉ GRAPHIQUE AJOUTÉE : Contrôle immédiat de la conformité réglementaire (8 chiffres)
        if not Validators.valider_telephone(tel):
            messagebox.showerror(
                "Format Téléphone Invalide", 
                "❌ Échec de l'inscription !\nLe numéro de téléphone doit comporter exactement 8 chiffres."
            )
            return

        if ClientService.inscrire_nouveau_client(nom, prenom, tel, vip):
            messagebox.showinfo("Inscrit", f"Client ajouté au répertoire avec succès !")
            self.entry_c_nom.delete(0, tk.END)
            self.entry_c_prenom.delete(0, tk.END)
            self.entry_c_tel.delete(0, tk.END)
            self.vip_var.set(False)
            self.actualiser_clients()
        else:
            messagebox.showerror("Doublon", "Ce numéro de téléphone est déjà attribué à un autre client.")

    def action_supprimer_client(self):
        selection = self.tree_clients.selection()
        if not selection:
            messagebox.showwarning("Sélection Requise", "Veuillez sélectionner un client dans la liste pour le supprimer.")
            return
        
        valeurs = self.tree_clients.item(selection, "values")
        id_client = valeurs

        if messagebox.askyesno("Confirmation", f"Voulez-vous supprimer définitivement le client {id_client} ?"):
            ClientService.supprimer_client(id_client)
            messagebox.showinfo("Supprimé", f"Le client {id_client} a été retiré de la base.")
            self.actualiser_clients()

    def actualiser_clients(self):
        for row in self.tree_clients.get_children():
            self.tree_clients.delete(row)
        clients = SauvegardeService.charger_clients()
        for c in clients:
            statut = "⭐ Membre VIP" if c.est_vip else "Standard"
            self.tree_clients.insert("", "end", values=(c.id_personne, c.nom, c.prenom, c.telephone, statut))

    # ==========================================
    # FONCTIONNALITÉ : TABLE DES RÉSERVATIONS
    # ==========================================
    def construire_onglet_reservations(self):
        """Génère le module de planification des réservations."""
        lbl_titre = ttk.Label(self.onglet_reservations, text="Planification des Tables", font=("Helvetica", 14, "bold"))
        lbl_titre.pack(pady=10)

        # Formulaire de réservation
        cadre_r = tk.LabelFrame(self.onglet_reservations, text=" ➕ Enregistrer une Réservation ", bg="#1e1e1e", fg="#ffffff", padx=10, pady=10)
        cadre_r.pack(fill="x", padx=20, pady=5)

        ttk.Label(cadre_r, text="ID Client :").grid(row=0, column=0, padx=5, pady=5)
        self.entry_r_client = ttk.Entry(cadre_r, width=12)
        self.entry_r_client.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(cadre_r, text="N° Table :").grid(row=0, column=2, padx=5, pady=5)
        self.entry_r_table = ttk.Entry(cadre_r, width=6)
        self.entry_r_table.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(cadre_r, text="Date/Heure :").grid(row=0, column=4, padx=5, pady=5)
        self.entry_r_date = ttk.Entry(cadre_r, width=18)
        # Pré-remplissage avec un format exemple
        self.entry_r_date.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.entry_r_date.grid(row=0, column=5, padx=5, pady=5)

        btn_add_res = ttk.Button(cadre_r, text="Réserver", command=self.action_creer_reservation)
        btn_add_res.grid(row=0, column=6, padx=15, pady=5)

        # Tableau des réservations
        cols_r = ("id", "client", "table", "date", "statut")
        self.tree_reservations = ttk.Treeview(self.onglet_reservations, columns=cols_r, show="headings", height=12)
        self.tree_reservations.heading("id", text="Code Résa")
        self.tree_reservations.heading("client", text="Identifiant Client")
        self.tree_reservations.heading("table", text="Table N°")
        self.tree_reservations.heading("date", text="Date & Horaire Prévus")
        self.tree_reservations.heading("statut", text="Statut")
        self.tree_reservations.pack(expand=True, fill="both", padx=20, pady=10)

        self.actualiser_reservations()

    def action_creer_reservation(self):
        id_c = self.entry_r_client.get().strip()
        num_t_str = self.entry_r_table.get().strip()
        date_str = self.entry_r_date.get().strip()

        if not id_c or not num_t_str or not date_str:
            messagebox.showerror("Champs Vides", "Veuillez remplir toutes les informations de planification.")
            return

        # Validation existence client
        if not ClientService.rechercher_client_par_id(id_c):
            messagebox.showerror("Client Introuvable", f"L'identifiant '{id_c}' n'existe pas.")
            return

        try:
            num_t = int(num_t_str)
        except ValueError:
            messagebox.showerror("Saisie Incorrecte", "Le numéro de table doit être un entier.")
            return

        # Enregistrement via le service
        ReservationService.creer_reservation(id_c, num_t, date_str)
        messagebox.showinfo("Confirmée", "La réservation a été enregistrée avec succès.")
        
        self.entry_r_client.delete(0, tk.END)
        self.entry_r_table.delete(0, tk.END)
        self.actualiser_reservations()

    def actualiser_reservations(self):
        for row in self.tree_reservations.get_children():
            self.tree_reservations.delete(row)
        res_list = ReservationService.charger_toutes_reservations()
        for r in res_list:
            self.tree_reservations.insert("", "end", values=(r["id_res"], r["id_client"], f"Table N°{r['numero_table']}", r["date_heure"], r["statut"]))

    # ==========================================
    # FONCTIONNALITÉ : TABLEAU DE BORD TEMPOREL
    # ==========================================
    def construire_onglet_stats(self):
        """Génère l'onglet comptable pour le suivi périodique des performances."""
        lbl_titre = ttk.Label(self.onglet_stats, text="Indicateurs Financiers Globaux du Club", font=("Helvetica", 14, "bold"))
        lbl_titre.pack(pady=15)

        # Cartes d'indicateurs comptables
        self.cadre_indicateurs = tk.Frame(self.onglet_stats, bg="#1e1e1e")
        self.cadre_indicateurs.pack(fill="x", padx=40, pady=10)

        self.lbl_tx = ttk.Label(self.cadre_indicateurs, text="📈 Nombre total de transactions : 0", font=("Helvetica", 11, "bold"))
        self.lbl_tx.pack(anchor="w", pady=5)

        self.lbl_ca = ttk.Label(self.cadre_indicateurs, text="💰 Chiffre d'Affaires Net Global : 0 FCFA", font=("Helvetica", 11, "bold"))
        self.lbl_ca.pack(anchor="w", pady=5)

        self.lbl_remise = ttk.Label(self.cadre_indicateurs, text="🎁 Total des avantages VIP : 0 FCFA", font=("Helvetica", 11, "bold"))
        self.lbl_remise.pack(anchor="w", pady=5)

        # Séparateur visuel pour la ventilation temporelle
        lbl_sep = ttk.Label(self.onglet_stats, text="📊 Ventilation Temporelle du Chiffre d'Affaires", font=("Helvetica", 12, "bold"))
        lbl_sep.pack(pady=15, anchor="w", padx=40)

        self.cadre_temporel = tk.Frame(self.onglet_stats, bg="#1e1e1e")
        self.cadre_temporel.pack(fill="x", padx=40, pady=5)

        self.lbl_ca_jour = ttk.Label(self.cadre_temporel, text="▶️ Chiffre d'Affaires du Jour : 0 FCFA", font=("Helvetica", 11))
        self.lbl_ca_jour.pack(anchor="w", pady=4)

        self.lbl_ca_mois = ttk.Label(self.cadre_temporel, text="▶️ Chiffre d'Affaires du Mois : 0 FCFA", font=("Helvetica", 11))
        self.lbl_ca_mois.pack(anchor="w", pady=4)

        self.lbl_ca_annee = ttk.Label(self.cadre_temporel, text="▶️ Chiffre d'Affaires de l'Année : 0 FCFA", font=("Helvetica", 11))
        self.lbl_ca_annee.pack(anchor="w", pady=4)

        btn_refresh_stats = ttk.Button(self.onglet_stats, text="🔄 Actualiser la Comptabilité", command=self.actualiser_stats)
        btn_refresh_stats.pack(pady=20)
        
        self.actualiser_stats()

    def actualiser_stats(self):
        """Calcule à chaud et met à jour l'affichage des valeurs financières."""
        rapport = StatistiqueService.generer_rapport_financier()
        
        self.lbl_tx.config(text=f"📈 Nombre total de transactions traitées : {rapport['nombre_transactions']}")
        self.lbl_ca.config(text=f"💰 Chiffre d'Affaires Net Encaissé : {rapport['total_recettes_net']} {DEVISE}")
        self.lbl_remise.config(text=f"🎁 Total des avantages accordés aux VIP : {rapport['total_remises_vip']} {DEVISE}")
        
        # Injection des valeurs de CA ventilées
        self.lbl_ca_jour.config(text=f"▶️ Chiffre d'Affaires du Jour : {rapport['ca_jour']} {DEVISE}")
        self.lbl_ca_mois.config(text=f"▶️ Chiffre d'Affaires du Mois : {rapport['ca_mois']} {DEVISE}")
        self.lbl_ca_annee.config(text=f"▶️ Chiffre d'Affaires de l'Année : {rapport['ca_annee']} {DEVISE}")
