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

        # Création des 6 panneaux applicatifs majeurs
        self.onglet_tables = ttk.Frame(self.notebook)
        self.onglet_parties = ttk.Frame(self.notebook)
        self.onglet_clients = ttk.Frame(self.notebook)
        self.onglet_reservations = ttk.Frame(self.notebook)
        self.onglet_stats = ttk.Frame(self.notebook)
        self.onglet_historique = ttk.Frame(self.notebook) # Nouveau cadre
         
        # Injection des onglets dans le conteneur principal
        self.notebook.add(self.onglet_tables, text=" 🎱 Tables de Billard ")
        self.notebook.add(self.onglet_parties, text=" 🕹️ Sessions de Jeu ")
        self.notebook.add(self.onglet_clients, text=" 👥 Gestion des Clients ")
        self.notebook.add(self.onglet_reservations, text=" 📅 Réservations ")
        self.notebook.add(self.onglet_stats, text=" 📊 Tableau de Bord ")
        self.notebook.add(self.onglet_historique, text=" 📜 Journal de Bord ")

        # Construction des interfaces graphiques respectives
        self.construire_onglet_tables()
        self.construire_onglet_parties()
        self.construire_onglet_clients()
        self.construire_onglet_reservations()
        self.construire_onglet_stats()
        self.construire_onglet_historique()

    def creer_barre_statut(self):
        """Affiche la barre supérieure avec option de permutation de l'employé en service."""
        barre = tk.Frame(self.root, bg="#2d2d2d", height=45)
        barre.pack(fill="x", side="top")
        
        # Bouton Quitter
        btn_quitter = tk.Button(barre, text="🚪 Quitter", bg="#a33b3b", fg="#ffffff", font=("Helvetica", 9, "bold"), 
                                borderwidth=0, padx=10, command=self.root.quit)
        btn_quitter.pack(side="left", padx=15, pady=8)

        # Label d'en-tête pour le sélecteur
        lbl_select = tk.Label(barre, text="👤 Agent en service :", bg="#2d2d2d", fg="#ffffff", font=("Helvetica", 10, "bold"))
        lbl_select.pack(side="left", padx=(300, 5))

        # Chargement de la liste des employés depuis le JSON pour la permutation
        self.liste_employes_obj = SauvegardeService.charger_employes()
        # Formate le texte d'affichage pour la liste déroulante (ex: "EMP0001 - Zoungrana Pierre")
        options_employes = [f"{e['id_personne']} - {e['nom']} {e['prenom']}" for e in self.liste_employes_obj]

        # Création de la Combobox de permutation
        self.combo_employes = ttk.Combobox(barre, values=options_employes, state="readonly", width=30, font=("Helvetica", 10))
        if options_employes:
            self.combo_employes.current(0)  # Sélectionne le premier par défaut
        self.combo_employes.pack(side="left", padx=5)

        # Écouteur d'événement : à chaque changement d'employé, on appelle la méthode de permutation
        self.combo_employes.bind("<<ComboboxSelected>>", self.action_permuter_employe)

        # Initialisation de la variable globale de session avec le premier employé de la liste
        self.employe_connecte = {
            "id": self.liste_employes_obj[0]["id_personne"],
            "nom": f"{self.liste_employes_obj[0]['nom']} {self.liste_employes_obj[0]['prenom']}"
        }


    def action_permuter_employe(self, event):
        """Détecte le choix de l'utilisateur et change instantanément l'employé actif en session."""
        index_selectionne = self.combo_employes.current()
        emp_choisi = self.liste_employes_obj[index_selectionne]
        
        # Permutation de la variable d'authentification
        self.employe_connecte["id"] = emp_choisi["id_personne"]
        self.employe_connecte["nom"] = f"{emp_choisi['nom']} {emp_choisi['prenom']}"
        
        # Message de confirmation éphémère
        messagebox.showinfo(
            "Permutation de Session", 
            f"🔄 Changement d'équipe effectué !\nLa session est désormais gérée par : {self.employe_connecte['nom']}."
        )


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
    # FONCTIONNALITÉ : INTERFACE SESSIONS DE JEU (RECHERCHE SMART)
    # ==========================================
    def construire_onglet_parties(self):
        """Construit le panneau de commande avec détection automatique du client par téléphone."""
        cadre_form = tk.LabelFrame(self.onglet_parties, text=" 🟢 Lancer une Session de Jeu ", bg="#1e1e1e", fg="#ffffff", padx=15, pady=15, font=("Helvetica", 11, "bold"))
        cadre_form.pack(fill="x", padx=20, pady=10)

        # Remplacement de l'ID par le Téléphone pour la recherche
        ttk.Label(cadre_form, text="Tél Client (8 chiff.) :").grid(row=0, column=0, padx=5, sticky="w")
        self.entry_recherche_tel = ttk.Entry(cadre_form, width=15, font=("Helvetica", 10))
        self.entry_recherche_tel.grid(row=0, column=1, padx=5)
        
        # SÉCURITÉ & ERGONOMIE : On écoute chaque touche tapée par le réceptionniste
        self.entry_recherche_tel.bind("<KeyRelease>", self.verification_dynamique_client)

        ttk.Label(cadre_form, text="Type Billard :").grid(row=0, column=2, padx=5, sticky="w")
        self.combo_type = ttk.Combobox(cadre_form, values=[t.value for t in TypeBillard], state="readonly", width=15)
        self.combo_type.current(0)
        self.combo_type.grid(row=0, column=3, padx=5)

        # Label dynamique de confirmation d'identité (S'affiche en vert quand le client est trouvé)
        self.lbl_info_client_detecte = tk.Label(cadre_form, text="⚠️ En attente d'un numéro valide...", bg="#1e1e1e", fg="#ffaa00", font=("Helvetica", 10, "italic"))
        self.lbl_info_client_detecte.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

        # Bouton d'action (Désactivé par défaut, s'activera uniquement si le client existe)
        self.btn_lancer = ttk.Button(cadre_form, text="🚀 Ouvrir la Table", state="disabled", command=self.action_ouvrir_table)
        self.btn_lancer.grid(row=0, column=4, padx=20)
        
        # Variable cachée pour mémoriser l'ID du client trouvé lors de la frappe
        self.id_client_selectionne_cache = None

        # --- SECTION DES SESSIONS EN COURS (Identique) ---
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


    def verification_dynamique_client(self, event):
        """Vérifie à chaque frappe de touche si le téléphone correspond à un client inscrit."""
        tel_saisi = self.entry_recherche_tel.get().strip()
        
        # On ne cherche en base que si l'utilisateur a fini de taper les 8 chiffres du Burkina
        if len(tel_saisi) == 8:
            client = ClientService.rechercher_client_par_telephone(tel_saisi)
            
            if client:
                # Client trouvé ! On affiche son identité et on stocke son ID en cache
                vip_txt = "⭐ VIP (Remise 20%)" if client.est_vip else "Standard"
                self.lbl_info_client_detecte.config(
                    text=f"🟢 Client : {client.prenom} {client.nom} ({client.id_personne}) - {vip_txt}", 
                    fg="#88ff88"
                )
                self.id_client_selectionne_cache = client.id_personne
                self.btn_lancer.config(state="normal") # Débloque le bouton d'ouverture !
            else:
                # Le numéro a 8 chiffres mais n'existe pas dans le JSON
                self.lbl_info_client_detecte.config(text="❌ Aucun client enregistré avec ce numéro.", fg="#ff5555")
                self.id_client_selectionne_cache = None
                self.btn_lancer.config(state="disabled")
        else:
            # Saisie en cours (moins de 8 chiffres)
            self.lbl_info_client_detecte.config(text="⚠️ En attente d'un numéro valide (8 chiffres)...", fg="#ffaa00")
            self.id_client_selectionne_cache = None
            self.btn_lancer.config(state="disabled")


    def actualiser_parties_actives(self):
        for row in self.tree_parties.get_children():
            self.tree_parties.delete(row)
        parties = PartieService.obtenir_parties_actives()
        for p in parties:
            self.tree_parties.insert("", "end", values=(p["id_partie"], p["id_client"], f"Table N°{p['numero_table']}", p["heure_debut"]))

    def action_ouvrir_table(self):
    # On récupère directement l'ID valide stocké par notre écouteur dynamique
        id_c = self.id_client_selectionne_cache
        type_str = self.combo_type.get()
        
        # Le client est garanti d'exister grâce au filtrage de saisie
        client = ClientService.rechercher_client_par_id(id_c)
        type_enum = TypeBillard(type_str)
        tables_libres = PartieService.obtenir_tables_libres_par_type(type_enum)
        
        if not tables_libres:
            messagebox.showwarning("Club Saturé", f"Toutes les tables '{type_str}' sont occupées.")
            return

        table_attribuee = tables_libres[0]
        PartieService.démarrer_partie(client, table_attribuee)
        
        messagebox.showinfo("Chrono Lancé", f"Table N°{table_attribuee.numero} affectée à {client.prenom} {client.nom}.")
        
        # Nettoyage et réinitialisation de l'onglet
        self.entry_recherche_tel.delete(0, tk.END)
        self.lbl_info_client_detecte.config(text="⚠️ En attente d'un numéro valide...", fg="#ffaa00")
        self.btn_lancer.config(state="disabled")
        self.id_client_selectionne_cache = None
        
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
        """Génère le module de planification avec options Annuler et Honorer."""
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
        self.entry_r_date.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.entry_r_date.grid(row=0, column=5, padx=5, pady=5)

        btn_add_res = ttk.Button(cadre_r, text="Réserver", command=self.action_creer_reservation)
        btn_add_res.grid(row=0, column=6, padx=15, pady=5)

        # Tableau des réservations
        cols_r = ("id", "client", "table", "date", "statut")
        self.tree_reservations = ttk.Treeview(self.onglet_reservations, columns=cols_r, show="headings", height=10)
        self.tree_reservations.heading("id", text="Code Résa")
        self.tree_reservations.heading("client", text="Identifiant Client")
        self.tree_reservations.heading("table", text="Table N°")
        self.tree_reservations.heading("date", text="Date & Horaire Prévus")
        self.tree_reservations.heading("statut", text="Statut")
        self.tree_reservations.pack(expand=True, fill="both", padx=20, pady=10)

        # PANNEAU D'OUTILS INTERACTIFS DE SÉCURITÉ
        zone_r_outils = tk.Frame(self.onglet_reservations, bg="#1e1e1e")
        zone_r_outils.pack(fill="x", padx=20, pady=5)

        btn_honorer = ttk.Button(zone_r_outils, text="🎮 Le client est là (Honorer)", command=self.action_honorer_reservation)
        btn_honorer.pack(side="left", padx=5)

        btn_annuler_res = tk.Button(zone_r_outils, text="❌ Annuler la Réservation", bg="#a33b3b", fg="#ffffff", 
                                    font=("Helvetica", 10, "bold"), borderwidth=0, padx=10, pady=5, command=self.action_annuler_reservation)
        btn_annuler_res.pack(side="right", padx=5)

        self.actualiser_reservations()

    def action_honorer_reservation(self):
        """Prend la réservation sélectionnée et démarre instantanément la partie."""
        selection = self.tree_reservations.selection()
        if not selection:
            messagebox.showwarning("Sélection Requise", "Veuillez sélectionner une réservation à honorer.")
            return

        # Extraction des valeurs de la ligne
        valeurs = self.tree_reservations.item(selection, "values")
        id_res = valeurs[0]
        statut_actuel = valeurs[4]

        # Alerte préventive visuelle
        if statut_actuel != "Confirmée":
            messagebox.showwarning("Action Impossible", f"❌ Impossible d'honorer la réservation {id_res}.\nSon statut actuel est déjà : {statut_actuel}")
            return

        if ReservationService.honorer_reservation(id_res):
            messagebox.showinfo("Partie Lancée", f"La réservation {id_res} a été honorée !\nLa table est lancée chronométrée.")
            self.actualiser_reservations()
            self.actualiser_tables()
            self.actualiser_parties_actives()
        else:
            messagebox.showerror("Erreur", "Impossible d'honorer la réservation. Vérifiez la disponibilité de la table.")

    def action_annuler_reservation(self):
        """Bascule le statut de la réservation sélectionnée à Annulée."""
        selection = self.tree_reservations.selection()
        if not selection:
            messagebox.showwarning("Sélection Requise", "Veuillez sélectionner une réservation à annuler.")
            return

        valeurs = self.tree_reservations.item(selection, "values")
        id_res = valeurs[0]
        statut_actuel = valeurs[4]

        # Alerte préventive visuelle
        if statut_actuel != "Confirmée":
            messagebox.showwarning("Action Impossible", f"❌ Impossible d'annuler la réservation {id_res}.\nElle possède déjà le statut : {statut_actuel}")
            return

        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment annuler la réservation {id_res} ?"):
            ReservationService.changer_statut_reservation(id_res, "Annulée")
            messagebox.showinfo("Annulée", f"La réservation {id_res} a été annulée.")
            self.actualiser_reservations()


    def action_creer_reservation(self):
        id_c = self.entry_r_client.get().strip()
        num_t_str = self.entry_r_table.get().strip()
        date_str = self.entry_r_date.get().strip()

        if not id_c or not num_t_str or not date_str:
            messagebox.showerror("Champs Vides", "Veuillez remplir toutes les informations de planification.")
            return

        if not ClientService.rechercher_client_par_id(id_c):
            messagebox.showerror("Client Introuvable", f"L'identifiant '{id_c}' n'existe pas.")
            return

        try:
            num_t = int(num_t_str)
        except ValueError:
            messagebox.showerror("Saisie Incorrecte", "Le numéro de table doit être un entier.")
            return

        # MODIFICATION : Analyse du booléen renvoyé par le service métier blindé
        if ReservationService.creer_reservation(id_c, num_t, date_str):
            messagebox.showinfo("Confirmée", "🟢 Succès ! La réservation a été enregistrée.")
            self.entry_r_client.delete(0, tk.END)
            self.entry_r_table.delete(0, tk.END)
            self.actualiser_reservations()
        else:
            # Message d'erreur explicite en cas de conflit détecté par les règles
            messagebox.showerror(
                "Conflit de Planning", 
                f"❌ Échec de la réservation !\nLa table N°{num_t} est soit actuellement occupée, soit déjà réservée par un autre client."
            )


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

    # ==========================================
    # FONCTIONNALITÉ : HISTORIQUE DES PARTIES
    # ==========================================
    def construire_onglet_historique(self):
        """Génère l'interface de consultation du journal des transactions."""
        lbl_titre = ttk.Label(self.onglet_historique, text="Journal historique des parties clôturées", font=("Helvetica", 14, "bold"))
        lbl_titre.pack(pady=10)

        cols_h = ("id_p", "client", "table", "debut", "fin")
        self.tree_historique = ttk.Treeview(self.onglet_historique, columns=cols_h, show="headings", height=15)
        self.tree_historique.heading("id_p", text="N° Session")
        self.tree_historique.heading("client", text="ID Client")
        self.tree_historique.heading("table", text="Table")
        self.tree_historique.heading("debut", text="Heure Début")
        self.tree_historique.heading("fin", text="Heure Clôture")
        self.tree_historique.pack(expand=True, fill="both", padx=20, pady=10)

        btn_refresh_h = ttk.Button(self.onglet_historique, text="🔄 Actualiser le Journal", command=self.actualiser_historique)
        btn_refresh_h.pack(pady=10)
        self.actualiser_historique()

    def actualiser_historique(self):
        """Recharge les anciennes parties depuis le fichier JSON."""
        for row in self.tree_historique.get_children():
            self.tree_historique.delete(row)
        
        historique = PartieService.obtenir_historique_complet()
        for h in historique:
            self.tree_historique.insert("", "end", values=(h["id_partie"], h["id_client"], f"Table N°{h['numero_table']}", h["heure_debut"], h["heure_fin"]))
