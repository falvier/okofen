import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))

import sqlite3
import pandas as pd
from src.config import (
    DB_FILE,
    COLONNES_CHAUFFAGE_TEMPERATURE,
    COLONNES_PUISSANCE_CHAUDIERE,
    COLONNES_TEMP_CHAUDIERE,
    COLONNES_ECS
    )
from datetime import datetime, time


def lire_table(nom_table, db_path=DB_FILE):
    try:
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql(f"SELECT * FROM {nom_table}", conn, parse_dates=["timestamp"])
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de la table '{nom_table}':", e)
        return pd.DataFrame()

def filtrer_par_date(df, debut, fin):
    mask = (df["timestamp"] >= pd.to_datetime(debut)) & (df["timestamp"] <= pd.to_datetime(fin))
    return df.loc[mask]

def lissage(df, colonnes, periode='1H'):
    df_lisse = df.set_index("timestamp")[colonnes].resample(periode).mean()
    return df_lisse.reset_index()

def extraire_dates_disponibles_sqlite() -> list:
    try:
        with sqlite3.connect(DB_FILE) as conn:
            df = pd.read_sql("SELECT DISTINCT DATE(timestamp) AS jour FROM chauffage ORDER BY jour", conn, parse_dates=["jour"])
            return sorted(df["jour"].dt.date.tolist())
    except Exception as e:
        print(f"❌ Erreur lors de l’extraction des dates :", e)
        return []

def etat_chauffage_par_date_sqlite() -> dict:
    """
    Récupère l'état du chauffage (chauffage1_pompe) par date depuis la base de données.
    Retourne un dict {date: True/False}, True si la pompe a été active (>0) au moins une fois ce jour-là.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = """
    SELECT 
        DATE(timestamp) as jour,
        MAX(CASE 
                WHEN chauffage1_pompe = 100 THEN 1 ELSE 0
            END) as actif
    FROM chauffage
    WHERE chauffage1_pompe != 1 
    GROUP BY jour;
    """

    result = {}
    try:
        for row in cursor.execute(query):
            jour_str, actif = row
            jour = datetime.strptime(jour_str, "%Y-%m-%d").date()
            result[jour] = bool(actif)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de la base : {e}")
    finally:
        conn.close()

    return result

def lire_donnees_chauffage(db_path, start=None, end=None):
    """
    Lit la table 'chauffage' depuis la base SQLite et filtre par dates si précisé.
    """
    df_chauffage1 = lire_table("chauffage", db_path)
    df_chauffage1 = lissage(df_chauffage1, COLONNES_CHAUFFAGE_TEMPERATURE, periode='1H')

    if df_chauffage1.empty:
        return df_chauffage1
    
    if start:
        start = datetime.combine(start, time.min)
    if end:
        end = datetime.combine(end, time.max)

    # Si les deux dates sont identiques, on force la plage sur la journée complète
    if start and end and start.date() == end.date():
        end = datetime.combine(end.date(), time.max)

    # Appliquer le filtre uniquement si au moins une des dates est spécifiée
    if start or end:
        df_chauffage1 = filtrer_par_date(
            df_chauffage1,
            start or df_chauffage1['timestamp'].min(),
            end or df_chauffage1['timestamp'].max()
        )
    return df_chauffage1

def lire_donnees_ecs(db_path, start=None, end=None):
    """
    Lit la table 'ecs' depuis la base SQLite et filtre par dates si précisé.
    """
    df_ecs = lire_table("ecs", db_path)
    
    if df_ecs.empty:
        return df_ecs
    if start:
        start = datetime.combine(start, time.min)
    if end:
        end = datetime.combine(end, time.max)

    # Si les deux dates sont identiques, on force la plage sur la journée complète
    if start and end and start.date() == end.date():
        end = datetime.combine(end.date(), time.max)

    # Appliquer le filtre uniquement si au moins une des dates est spécifiée
    if start or end:
        df_ecs = filtrer_par_date(
            df_ecs,
            start or df_ecs['timestamp'].min(),
            end or df_ecs['timestamp'].max()
        )
    
    colonnes_dispo = [c for c in COLONNES_ECS if c in df_ecs.columns and c != 'timestamp']
    if colonnes_dispo:
        df_ecs = lissage(df_ecs, colonnes_dispo, periode='1H')
    else:
        print("⚠️ Aucune colonne ECS trouvée pour le lissage")
    return df_ecs

def lire_donnees_chaudiere(db_path, start=None, end=None):
    """
    Lit la table 'chaudiere' depuis la base SQLite et filtre par dates si précisé.
    """
    df_chaudiere = lire_table("chaudiere", db_path)
    df_chaudiere = lissage(df_chaudiere, COLONNES_TEMP_CHAUDIERE + COLONNES_PUISSANCE_CHAUDIERE, periode='1H') 
    if df_chaudiere.empty:
        return df_chaudiere
    if start:
        start = datetime.combine(start, time.min)
    if end:
        end = datetime.combine(end, time.max)

    # Si les deux dates sont identiques, on force la plage sur la journée complète
    if start and end and start.date() == end.date():
        end = datetime.combine(end.date(), time.max)

    # Appliquer le filtre uniquement si au moins une des dates est spécifiée
    if start or end:
        df_chaudiere = filtrer_par_date(
            df_chaudiere,
            start or df_chaudiere['timestamp'].min(),
            end or df_chaudiere['timestamp'].max()
        )
    return df_chaudiere

def lire_jours_actifs_sqlite() -> set:
    """
    Lit la vue 'jours_actifs' depuis la base de données SQLite.
    Retourne un ensemble de dates avec chauffage actif.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("SELECT jour FROM jours_actifs", conn, parse_dates=["jour"])
        return set(df["jour"].dt.date)
    except Exception as e:
        print("❌ Erreur lecture de la vue 'jours_actifs' :", e)
        return set()
    finally:
        conn.close()

def jours_chauffage_simple():

    """
    Retourne rapidement les jours avec une activité minimale du chauffage.
    Détecte les jours où 'chauffage1_pompe' est = 100 au moins une fois.
    """
    conn = sqlite3.connect(DB_FILE)
    
    requete = """
    SELECT DATE(timestamp) AS jour
    FROM chauffage
    WHERE chauffage1_pompe = 100
    GROUP BY jour
    ORDER BY jour;
    """
    
    df = pd.read_sql_query(requete, conn)
    conn.close()
    
    df["chauffe"] = True  # 🔸 On ajoute une colonne pour compatibilité avec l’interface
    return df

def main():
    print("=== Test lecture chauffage ===")
    df_chauffage1 = lire_donnees_chauffage(DB_FILE, start='2025-01-01', end='2025-01-03')
    print("Index name chauffage :", df_chauffage1.index.name)
    print("Colonnes chauffage :", df_chauffage1.columns.tolist())
    print(df_chauffage1.head(), "\n")

    print("=== Test lecture ECS ===")
    df_ecs = lire_donnees_ecs(DB_FILE, start='2025-01-01', end='2025-01-03')
    print("Index name ECS :", df_ecs.index.name)
    print("Colonnes ECS :", df_ecs.columns.tolist())
    print(df_ecs.head())

if __name__ == "__main__":
    main()
