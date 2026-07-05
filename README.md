# 🎱 BillardManager v3.0

> Système d'Information Évolué (ERP) pour la gestion opérationnelle, la planification des parcs de tables, la traçabilité du personnel et la facturation automatisée d'un club de billard.

Ce logiciel met en œuvre une double approche applicative : une **interface console interactive** sécurisée et une **interface graphique moderne (GUI)** à thème sombre, connectée à une base de données relationnelle déportée sur fichiers plats JSON.

---

## 📝 Description du Sujet de Projet

### 1. Contexte et Problématique Métier
La gestion quotidienne d'un club de billard repose sur une ressource critique, limitée et périssable : **le temps d'occupation des tables**. Contrairement à un commerce classique de vente d'articles physiques, un club de billard vend une expérience temporelle (la location d'une table à l'heure). 

Dans la réalité, un gestionnaire fait face à plusieurs défis majeurs :
*   **Les erreurs de facturation humaine** : Calculer de tête la durée exacte entre l'arrivée (ex: 14h13) et le départ (ex: 15h42) d'un client, tout en appliquant des tarifs différents par type de billard et des réductions d'abonnements, est source de pertes financières ou de litiges.
*   **Les conflits de planification (Surréservation)** : Permettre à un client de réserver une table alors qu'elle est déjà promise à un autre, ou accorder une session libre à un joueur de passage alors qu'une réservation officielle commence dans 10 minutes.
*   **Le manque de traçabilité** : Savoir quel employé a encaissé quelle somme, suivre l'évolution du Chiffre d'Affaires par Jour, Mois ou Année, et connaître l'historique précis de l'utilisation du parc de tables.

### 2. Traduction des Concepts en Programmation Orientée Objet (POO)
L'exploitation d'un club de billard est un cas d'école parfait pour appliquer les principes de la POO demandés par les consignes :
*   **L'Héritage** : Une classe mère `Personne` centralise l'identité humaine. Les classes filles `Client` et `Employe` en héritent directement. `Client` y ajoute la gestion du statut VIP et de la méthode de réduction, tandis que `Employe` gère la traçabilité des équipes.
*   **L'Encapsulation** : La classe `TableBillard` protège ses données internes (`numero`, `tarif_horaire`, `est_occupee`). Son type est verrouillé par une énumération (`TypeBillard`) pour interdire toute valeur fantaisiste.
*   **L'Association et la Composition** : La classe `Partie` matérialise l'association entre un `Client` et une `Table`. La classe `Paiement` est liée par composition à la `Partie` pour en extraire la durée exacte et sceller le règlement financier.
*   **La Persistance des données (Sérialisation)** : Toutes les entités sont traduites en dictionnaires pour être stockées de manière permanente dans des fichiers plats au format standardisé **JSON** (`data/`).

> 📌 **Note Académique :** Une version rédigée et détaillée de cette description est également disponible dans le dossier des livrables de notre rapport à l'emplacement suivant : **`docs/Rapport/description du sujet de projet.pdf`** (ou .pdf).

---

## 🛠️ Fonctionnalités Avancées du Système (v3.0)

### 👥 1. Gestion & Répertoire des Clients
- Inscription avec génération transparente d'un identifiant unique incrémental (`CLT0001`, `CLT0002`).
- **Blindage Réglementaire (Alerte Graphique)** : Le système intercepte instantanément les saisies et bloque l'inscription via une alerte d'erreur si le numéro de téléphone ne comporte pas exactement 8 chiffres.
- Option de suppression définitive du catalogue client avec réécriture dynamique de la base de données.

### 🕹️ 2. Sessions de Jeu (Recherche Prédictive Smart)
- **Ergonomie Réceptionniste** : Plus besoin de retenir les ID clients. Le système intègre un écouteur d'événements clavier (`KeyRelease`) sur le numéro de téléphone. Dès que les 8 chiffres sont saisis, l'identité du joueur et son statut VIP s'affichent automatiquement en vert à l'écran, et le bouton d'ouverture se débloque.
- Attribution automatisée de la première table disponible selon le style de billard désiré.
- **Règle Anti-Squat Temporelle** : Le système analyse le planning et refuse d'accorder une session de jeu libre sur une table si celle-ci fait l'objet d'une réservation confirmée dans les 30 prochaines minutes.

### 📅 3. Cycle de Vie des Réservations
- Enregistrement des réservations par ID Client, numéro de table et date/heure.
- **Contrôles Anti-Surréservation** : Le système refuse d'enregistrer une réservation si la table demandée est déjà réservée dans le planning ou si elle est physiquement occupée par un joueur.
- Passerelle automatisée : Option « Honorer » qui bascule instantanément la réservation au statut `Honorée`, libère le planning et lance le chronomètre de jeu sans ressaisie.
- **Maintenance Automatique des Retards** : À chaque ouverture ou rechargement, un algorithme d'arrière-plan calcule le décalage horaire. Si un client a plus de 30 minutes de retard sur sa réservation, le système la bascule automatiquement au statut `Annulée (Retard)` et libère la table pour le club.

### 📊 4. Tableau de Bord Comptable Temporel & Traçabilité
- **Permutation des Employés (Changement d'équipe)** : La barre supérieure de l'application permet de permuter le réceptionniste actif. Chaque reçu de caisse est marqué par l'identité de l'agent pour assurer un audit transparent.
- **Ventilation Calendaire** : Analyse en temps réel des transactions pour afficher distinctement le Chiffre d'Affaires du **Jour**, du **Mois**, et de l'**Année** en cours.
- Journal historique de bord (`parties.json`) listant l'intégralité des sessions clôturées.

---

## 📁 Architecture du Projet

```text
BillardManager/
│
├── main.py                    # Point d'entrée unique de l'application
├── requirements.txt           # Dépendances logicielles
├── .gitignore                 # Filtres d'exclusion Git
├── README.md                  # Documentation principale
│
├── docs/                      # Documentation et Rapports Académiques
│   ├── UML/                   # Fichiers PlantUML (.puml)
│   ├── Rapport/               # Dossier du rapport écrit complet ( description_sujet.txt )
│   └── Images/                # Diagrammes exportés (.png)
│
├── models/                    # Modèles de données métiers et structures
│   ├── enums.py
│   ├── personne.py
│   ├── client.py
│   ├── employe.py
│   ├── table_billard.py
│   ├── partie.py
│   └── paiement.py
│
├── services/                  # Logique métier et couches d'accès aux données
│   ├── client_service.py
│   ├── table_service.py
│   ├── partie_service.py
│   ├── paiement_service.py
│   ├── statistique_service.py
│   └── sauvegarde_service.py
│
├── ui/                        # Couche de présentation (User Interface)
│   ├── menu.py                # Arborescence des menus textuels (Console)
│   ├── saisie.py              # Blindage des entrées claviers contre les crashs
│   └── affichage.py           # Interface graphique moderne (Tkinter)
│
├── utils/                     # Modules utilitaires transversaux
│   ├── constantes.py
│   └── validators.py
│
└── data/                      # Persistance de données (Fichiers plats JSON)
    ├── clients.json
    ├── tables.json
    ├── parties.json
    └── paiements.json
```

---

## 🚀 Guide d'Installation et d'Exécution

### Prérequis
- Python 3.10 ou version supérieure installée.

### Lancement standard (Mode Développement)
Placez-vous à la racine du projet dans votre terminal et exécutez :
```bash
python main.py
```
Le point d'entrée unique vous invite à choisir votre environnement de travail :
- **Choix 1** : Lancement de l'interface **Console (Textuelle)**.
- **Choix 2** : Lancement de l'interface **Graphique Moderne (Tkinter Sombre)**.

### 📦 Compilation du Setup Autonome (Livrable Client)
Pour distribuer l'application sous forme de logiciel installable indépendant (exécutable sans Python), utilisez `PyInstaller` :
```bash
pip install -r requirements.txt
pyinstaller --noconsole --onefile --name="BillardManager" main.py
```
L'exécutable autonome est généré instantanément dans le dossier **`dist/BillardManager.exe`**.


## 📁 Spécifications des Diagrammes de Conception (`docs/UML/`)

L'ensemble des fichiers de modélisation industrielle est disponible au format universel `PlantUML` dans le répertoire dédié :
- `cas_utilisation.puml` : Modélisation des privilèges et cas d'utilisation (Réceptionniste vs Gérant).
- `diagramme_classes.puml` : Cartographie structurelle complète des classes, multiplicités et dépendances POO.
- `diagramme_sequence.puml` : Cinématique de la recherche prédictive par saisie de téléphone à 8 chiffres.