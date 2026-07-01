import sys
from ui.menu import Menu
from services.sauvegarde_service import SauvegardeService

def main():
    """Point d'entrée principal unique du logiciel BillardManager."""
    # 1. Initialise les fichiers de données JSON requis au démarrage
    SauvegardeService.initialiser_dossier_data()
    
    # SÉCURITÉ COMPILATION : Si l'application est lancée sans console arrière-plan
    if sys.stdin is None or not sys.stdin.isatty():
        # Lance directement l'interface graphique Tkinter moderne sans poser de question
        import tkinter as tk
        from ui.affichage import BillardManagerGUI
        
        root = tk.Tk()
        app = BillardManagerGUI(root)
        root.mainloop()
        return

    # --- MODE DÉVELOPPEMENT / CONSOLE CLASSIQUE ---
    print("==============================================")
    print("📊 INITIALISATION DE BILLARD MANAGER v3.0")
    print("==============================================")
    print("1. 💻 Lancer l'interface Console (Classique)")
    print("2. 🎨 Lancer l'interface Graphique (Moderne)")
    
    while True:
        try:
            choix = int(input("\nChoisissez votre interface (1-2) : "))
            if choix in [1, 2]:
                break
            print("❌ Veuillez choisir 1 ou 2.")
        except ValueError:
            print("❌ Entrée invalide. Saisissez un chiffre.")

    if choix == 1:
        Menu.afficher_menu_principal()
    elif choix == 2:
        import tkinter as tk
        from ui.affichage import BillardManagerGUI
        root = tk.Tk()
        app = BillardManagerGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
