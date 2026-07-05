# 🎱 BillardManager v3.0

> Système d'Information Évolué (ERP) pour la gestion opérationnelle, la planification des parcs de tables, la traçabilité du personnel et la facturation automatisée d'un club de billard.

Ce logiciel met en œuvre une double approche applicative : une **interface console interactive** sécurisée et une **interface graphique moderne (GUI)** à thème sombre, connectée à une base de données relationnelle déportée sur fichiers plats JSON.

---

## 📐 Architecture Orientée Objet & Règles Métiers (POO)

Le logiciel est découpé en packages hermétiques (`models`, `services`, `ui`, `utils`, `data`) et s'articule autour de 6 structures de classes fondamentales :

1. **`Personne` (Classe Abstraite de Base)** : Centralise l'identité civile (Nom, Prénom, Téléphone) et embarque un moteur de filtrage par Expressions Régulières (Regex).
2. **`Client` (Héritage de Personne)** : Intègre le statut d'éligibilité financière (Membres VIP) ouvrant droit à une réduction permanente de 20% sur les sessions de jeu.
3. **`Employe` (Héritage de Personne)** : Modélise les agents de caisse et réceptionnistes en service afin de garantir l'auditabilité et la traçabilité de chaque encaissement.
4. **`TableBillard` (Encapsulation)** : Encapsule les index de tarification fixe et l'état physique du matériel, indexés sur l'énumération stricte `TypeBillard` (Américain, Snooker, Français).
5. **`Reservation` (Planification Temporelle)** : Gère le cycle de vie complet des réservations (`Confirmée`, `Annulée`, `Honorée`) et interdit toute modification régressive des statuts validés.
6. **`Partie` & `Paiement` (Associations & Agrégations)** : Orchestrent le cœur métier (calcul des durées réelles, génération des reçus fiscaux et ventilation comptable périodique).

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
- Passerelle automatisée : Option « Honorer » qui bascule instantanément la réservation au statut `Honorée`, libère le planning et lance le chronomètre de jeu sans ressaisie.
- **Maintenance Automatique des Retards** : À chaque ouverture ou rechargement, un algorithme d'arrière-plan calcule le décalage horaire. Si un client a plus de 30 minutes de retard sur sa réservation, le système la bascule automatiquement au statut `Annulée (Retard)` et libère la table pour le club.

### 📊 4. Tableau de Bord Comptable Temporel
- Calcul à chaud du chiffre d'affaires global et du volume de remises offertes.
- **Ventilation Calendaire** : Analyse en temps réel des transactions pour afficher distinctement le Chiffre d'Affaires du **Jour**, du **Mois**, et de l'**Année** en cours.
- Journal historique de bord (`parties.json`) listant l'intégralité des sessions clôturées pour l'audit.

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

---

## 📁 Spécifications des Diagrammes de Conception (`docs/UML/`)

L'ensemble des fichiers de modélisation industrielle est disponible au format universel `PlantUML` dans le répertoire dédié :
- `cas_utilisation.puml` : Modélisation des privilèges et cas d'utilisation (Réceptionniste vs Gérant).
- `diagramme_classes.puml` : Cartographie structurelle complète des classes, multiplicités et dépendances POO.
- `diagramme_sequence.puml` : Cinématique de la recherche prédictive par saisie de téléphone à 8 chiffres.
