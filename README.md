# 🎱 BillardManager v3.0

> Application logicielle modulaire et professionnelle pour la gestion de l'exploitation, du parc de tables et de la facturation en temps réel d'un club de billard.

Ce projet implémente une double approche utilisateur : une **interface console interactive** et une **interface graphique moderne (GUI)**, le tout connecté à un système de stockage persistant.

---

## 📐 Conception Orientée Objet (Critères Pédagogiques)

Le logiciel est structuré selon une architecture modulaire en couches (`models`, `services`, `ui`, `utils`, `data`) respectant strictement les règles de la POO et les contraintes académiques :

1. **`Personne` (Classe de Base)** : Centralise les attributs communs (Nom, Prénom, Téléphone) et intègre un moteur de validation des formats par expressions régulières (Regex).
2. **`Client` (Héritage)** : Hérite de `Personne`. Gère les spécificités des membres, le calcul automatique des droits aux remises et l'éligibilité au statut VIP.
3. **`Employe` (Héritage)** : Hérite de `Personne`. Modélise le personnel de caisse en service pour garantir la traçabilité complète de chaque transaction financière.
4. **`TableBillard` (Encapsulation)** : Encapsule l’état de disponibilité, le numéro de table et indexe la tarification horaire fixe sur l'énumération stricte `TypeBillard` (Américain, Snooker, Français).
5. **`Partie` & `Paiement` (Association & Composition)** : Orchestrent le cœur de métier du club. Gèrent l'affectation dynamique d'une table à un joueur, le chronométrage précis des sessions et la sérialisation des reçus comptables.

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
├── models/                    # Modèles de données métiers et structures
│   ├── enums.py               # Énumérations strictes (Types, Modes, Statuts)
│   ├── personne.py
│   ├── client.py
│   ├── employe.py
│   ├── table_billard.py
│   ├── partie.py
│   └── paiement.py
│
├── services/                  # Logique métier et couches d'accès aux données
│   ├── client_service.py      # Inscriptions sécurisées et génération d'ID
│   ├── table_service.py       # Contrôle d'unicité du parc de tables
│   ├── partie_service.py      # Suivi des chronos et filtrage des tables libres
│   ├── paiement_service.py    # Calculs financiers et édition des reçus
│   ├── statistique_service.py # Bilans comptables et agrégation des revenus
│   └── sauvegarde_service.py  # Persistance et sérialisation JSON
│
├── ui/                        # Couche de présentation (User Interface)
│   ├── menu.py                # Arborescence des menus textuels (Console)
│   ├── saisie.py              # Blindage des entrées claviers contre les crashs
│   └── affichage.py           # Interface graphique moderne (Tkinter)
│
├── utils/                     # Modules utilitaires transversaux
│   ├── constantes.py          # Configuration financière et temporelle
│   └── validators.py          # Validateurs Regex (Téléphones, Emails)
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
- Python 3.10 ou version supérieure installée sur votre machine.

### Lancement en mode Développement
Ouvrez votre terminal à la racine du dossier du projet et exécutez :
```bash
python main.py
```

### Options au Démarrage
Le point d'entrée unique `main.py` vous invite à choisir votre environnement de travail :
- **Choix 1 (Interface Console)** : Permet de tester la rigueur de l'arborescence des menus textuels, les scénarios de démonstration chronométrés et la robustesse des entrées blindées.
- **Choix 2 (Interface Graphique - GUI)** : Ouvre une application moderne à thème sombre dotée d'onglets pour piloter visuellement le club (Suivi des tables, Formulaire d'inscription des clients, Tableau de bord financier à chaud).

---

## 🛠️ Génération de l'Exécutable Autonome (Setup/Build)

Pour distribuer cette application sous la forme d'un logiciel indépendant installable (sans nécessiter l'installation de Python sur la machine cible), nous utilisons `PyInstaller`.

1. Installez le compilateur :
```bash
pip install -r requirements.txt
```

2. Compilez le projet en un fichier unique avec masquage de la console d'arrière-plan :
```bash
pyinstaller --noconsole --onefile --name="BillardManager" main.py
```

3. L'exécutable autonome compilé est généré et disponible instantanément dans le dossier **`dist/BillardManager.exe`**.
