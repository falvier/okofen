import sys
from pathlib import Path
# 🔧 Ajouter le dossier parent de 'src/' au chemin des modules
sys.path.append(str(Path(__file__).resolve().parents[1]))


import pandas as pd
import glob
from src.config import (
    DB_FILE,
    DATA_DIR,
    COLONNES_CHAUDIERE,
    COLONNES_CHAUFFAGE_COMPLET,
    COLONNES_ECS
    )
from src.fonctions import lire_table
from src.database import creer_base
from src.visualisation import visualiser_ecs





if __name__ == "__main__":
    # 1. Construire ou mettre à jour la base
    creer_base()

    # 2. Lire la table chaudière
    df_chaudiere = lire_table("chaudiere")

    # 3. Aperçu des données
    print(df_chaudiere[COLONNES_CHAUDIERE].head(5))
