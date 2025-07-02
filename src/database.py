import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))


import pandas as pd
import sqlite3
from src.config import DATA_DIR, DB_FILE, RENAME_DICT, COLONNES_CHAUDIERE, COLONNES_CHAUFFAGE_COMPLET, COLONNES_ECS


def charger_csvs():
    fichiers_csv = list(DATA_DIR.glob("*.csv"))
    if not fichiers_csv:
        raise FileNotFoundError("Aucun fichier CSV trouvé dans le dossier data.")

    dataframes = []
    for fichier in fichiers_csv:
        try:
            df = pd.read_csv(
                fichier,
                sep=';',
                decimal=',',
                parse_dates=[[0, 1]],
                dayfirst=True,
                encoding='ISO-8859-1',
                skipinitialspace=True
            )
            df.columns = df.columns.str.strip()
            df.rename(columns=RENAME_DICT, inplace=True)
            df.dropna(axis=1, how='all', inplace=True)
            dataframes.append(df)
        except Exception as e:
            print(f"Erreur lors du chargement de {fichier.name} :", e)

    return pd.concat(dataframes, ignore_index=True)

def extraire_tables(df):
    return (
        df[COLONNES_CHAUDIERE].copy(),
        df[COLONNES_CHAUFFAGE_COMPLET].copy(),
        df[COLONNES_ECS].copy()
    )

def enregistrer_table(df, nom_table, db_path=DB_FILE):
    try:
        with sqlite3.connect(db_path) as conn:
            df.to_sql(nom_table, conn, if_exists="replace", index=False)
        print(f"✅ Table '{nom_table}' enregistrée dans la base.")
    except Exception as e:
        print(f"❌ Erreur en enregistrant la table '{nom_table}':", e)

def creer_base():
    df_complet = charger_csvs()

    

    df_chaudiere, df_chauffage1, df_ecs = extraire_tables(df_complet)

    enregistrer_table(df_chaudiere, "chaudiere")
    enregistrer_table(df_chauffage1, "chauffage")
    enregistrer_table(df_ecs, "ecs")
    print("🎉 Base de données créée avec succès !")

def creer_vue_jours_actifs(db_path=DB_FILE):
    print("📁 Lecture de la vue dans :", db_path)
    requete = """
    CREATE VIEW IF NOT EXISTS jours_actifs AS
    SELECT 
        DATE(timestamp) AS jour
    FROM chauffage
    WHERE CAST(chauffage1_pompe AS INTEGER) = 100
    GROUP BY jour;
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(requete)
            print("✅ Vue 'jours_actifs' créée ou déjà existante.")
    except Exception as e:
        print("❌ Erreur lors de la création de la vue :", e)

if __name__ == "__main__":
    creer_base()