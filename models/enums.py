from enum import Enum

class TypeBillard(Enum):
    AMERICAIN = "Américain"
    SNOOKER = "Snooker"
    FRANCAIS = "Français"

class StatutReservation(Enum):
    CONFIRMEE = "Confirmée"
    ANNULEE = "Annulée"
    TERMINEE = "Terminée"

class ModePaiement(Enum):
    ESPECES = "Espèces"
    ORANGE_MONEY = "Orange Money"
    MOOV_MONEY = "Moov Money"
    CARTE_BANCAIRE = "Carte Bancaire"
