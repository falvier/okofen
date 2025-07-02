from pathlib import Path

# Dossier racine du projet (on part du fichier config.py dans src/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Dossier des données
DATA_DIR = PROJECT_ROOT / "data"

# Chemin vers la base de données
DB_FILE = DATA_DIR / "chaudiere.sqlite"

# Recherche des CSV
#CSV_GLOB = DATA_DIR.glob("*.csv")


#dictionnaire de traduction de nom de colonnes
RENAME_DICT = {
    'Datum _Zeit': 'timestamp',
    'AT [°C]': 'temp_ext',
    'ATakt [°C]': 'temp_ext_actuelle',
    'PE1_BR1': 'puissance_bruleur',
    'HK1 VL Ist[°C]': 'chauffage1_depart_reel',
    'HK1 VL Soll[°C]': 'chauffage1_depart_consigne',
    'HK1 RT Ist[°C]': 'chauffage1_retour_reel',
    'HK1 RT Soll[°C]': 'chauffage1_retour_consigne',
    'HK1 Pumpe': 'chauffage1_pompe',
    'HK1 Mischer': 'chauffage1_melangeur',
    'HK1 Fernb[°C]': 'chauffage1_telecommande',
    'HK1 Status': 'chauffage1_etat',
    'WW1 EinT Ist[°C]': 'ecs_entree_reelle',
    'WW1 AusT Ist[°C]': 'ecs_sortie_reelle',
    'WW1 Soll[°C]': 'ecs_consigne',
    'WW1 Pumpe': 'ecs_pompe',
    'WW1 Status': 'ecs_etat',
    'PE1 KT[°C]': 'chaudiere_temp_kt',
    'PE1 KT_SOLL[°C]': 'chaudiere_temp_kt_consigne',
    'PE1 UW Freigabe[°C]': 'chaudiere_uw_autorisation',
    'PE1 Modulation[%]': 'modulation_puissance_chaudiere',
    'PE1 FRT Ist[°C]': 'fumee_retour_reelle',
    'PE1 FRT Soll[°C]': 'fumee_retour_consigne',
    'PE1 FRT End[°C]': 'fumee_retour_fin',
    'PE1 Einschublaufzeit[zs]': 'temps_vis_alimentaiont_granules',
    'PE1 Pausenzeit[zs]': 'temps_pause_vis',
    'PE1 Luefterdrehzahl[%]': 'ventilateur_vitesse',
    'PE1 Saugzugdrehzahl[%]': 'extracteur_vitesse',
    'PE1 Unterdruck Ist[EH]': 'depression_reelle',
    'PE1 Unterdruck Soll[EH]': 'depression_consigne',
    'PE1 Fuellstand[kg]': 'reservoir_kg',
    'PE1 Fuellstand ZWB[kg]': 'reservoir_interne_kg',
    'PE1 Status': 'chaudiere_etat',
    'PE1 Motor ES': 'moteur_es',
    'PE1 Motor RA': 'moteur_ra',
    'PE1 Motor RES1': 'moteur_res1',
    'PE1 Motor TURBINE': 'moteur_turbine',
    'PE1 Motor ZUEND': 'moteur_allumage',
    'PE1 Motor UW[%]': 'moteur_uw',
    'PE1 Motor AV': 'moteur_av',
    'PE1 Motor RES2': 'moteur_res2',
    'PE1 Motor MA': 'moteur_ma',
    'PE1 Motor RM': 'moteur_rm',
    'PE1 Motor SM': 'moteur_sm',
    'PE1 Res1 Temp.[°C]': 'temperature_res1',
    'PE1 Res2 Temp.[°C]': 'temperature_res2',
    'PE1 CAP RA': 'capteur_ra',
    'PE1 CAP ZB': 'capteur_zb',
    'PE1 AK': 'capteur_ak',
    'PE1 Saug-Int[min]': 'intervalle_aspiration_min',
    'PE1 DigIn1': 'entree_numerique_1',
    'PE1 DigIn2': 'entree_numerique_2',
    'Fehler1': 'erreur1',
    'Fehler2': 'erreur2',
    'Fehler3': 'erreur3',
    'Unnamed: 56': 'colonne_inconnue_56'
}


# préparation des colonnes des tables
COLONNES_CHAUDIERE = [
    'timestamp',
    'puissance_bruleur',
    'chaudiere_temp_kt',
    'chaudiere_temp_kt_consigne',
    'modulation_puissance_chaudiere',
    'chaudiere_uw_autorisation',
    'fumee_retour_reelle',
    'fumee_retour_consigne',
    'fumee_retour_fin',
    'reservoir_kg',
    'reservoir_interne_kg',
    'chaudiere_etat',
    'moteur_es', 'moteur_ra', 'moteur_res1', 'moteur_res2',
    'moteur_turbine', 'moteur_allumage', 'moteur_uw',
    'moteur_av', 'moteur_ma', 'moteur_rm', 'moteur_sm',
    'capteur_ra', 'capteur_zb', 'capteur_ak',
    'ventilateur_vitesse', 'extracteur_vitesse',
    'depression_reelle', 'depression_consigne',
    'intervalle_aspiration_min',
    'entree_numerique_1', 'entree_numerique_2',
    'erreur1', 'erreur2', 'erreur3'
]

COLONNES_CHAUFFAGE_COMPLET = [
    'timestamp',
    'chauffage1_depart_reel',
    'chauffage1_depart_consigne',
    'chauffage1_retour_reel',
    'chauffage1_retour_consigne',
    'chauffage1_pompe',
    'chauffage1_melangeur',
    'chauffage1_telecommande',
    'chauffage1_etat'
]

COLONNES_ECS = [
    'timestamp',
    'ecs_entree_reelle',
    'ecs_sortie_reelle',
    'ecs_consigne',
    'ecs_pompe',
    'ecs_etat'
]

# Colonnes pour la visualisation chaudière
COLONNES_TEMP_CHAUDIERE = [
    'chaudiere_temp_kt',
    'chaudiere_temp_kt_consigne',
    'fumee_retour_reelle',
    'fumee_retour_consigne'
]

COLONNES_PUISSANCE_CHAUDIERE = [
    'puissance_bruleur',
    'modulation_puissance_chaudiere'
]


COLONNES_CHAUFFAGE_TEMPERATURE = [
    'chauffage1_depart_reel', 
    'chauffage1_depart_consigne', 
    'chauffage1_retour_reel', 
    'chauffage1_retour_consigne'
    ]

