#visualisation
from fonctions import (
    lire_donnees_chauffage,
    lire_donnees_ecs,
    lire_donnees_chaudiere,
    filtrer_par_date,
    lissage)

from config import (
    DB_FILE,
    COLONNES_TEMP_CHAUDIERE,
    COLONNES_PUISSANCE_CHAUDIERE,
    COLONNES_ECS,
    COLONNES_CHAUFFAGE_TEMPERATURE
    )
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import timedelta

def afficher_statistiques(df):
    print(df.describe(include='all'))

def tracer_evolution(df, colonnes):
    df.set_index("timestamp")[colonnes].plot(figsize=(12, 6))
    plt.title("Évolution des données")
    plt.xlabel("Date")
    plt.ylabel("Valeurs")
    plt.grid()
    plt.tight_layout()
    plt.show()


def visualiser_chaudiere(db_path, start=None, end=None, afficher_infos=True, ax=None):
    """
    Visualise les données principales de la chaudière sur une période donnée.
    """
    if start and not end:
        end = start + timedelta(days=1)

    df_chaudiere = lire_donnees_chaudiere(db_path, start, end)
    if df_chaudiere.empty:
        print("⚠️ Aucune donnée chaudière trouvée.")
        return df_chaudiere

    duree = (df_chaudiere['timestamp'].max() - df_chaudiere['timestamp'].min()).days

    if duree > 3:
        print(f"📉 Durée = {duree} jours → lissage automatique par heure")
        df_chaudiere = lissage(df_chaudiere, COLONNES_TEMP_CHAUDIERE+ COLONNES_PUISSANCE_CHAUDIERE, periode='1H')

    if afficher_infos:
        print(f"✅ {len(df_chaudiere)} lignes chaudière chargées")
        print(f"Période : de {df_chaudiere['timestamp'].min()} à {df_chaudiere['timestamp'].max()}")

    if ax is not None:
        plot_chaudiere(df_chaudiere, COLONNES_TEMP_CHAUDIERE, COLONNES_PUISSANCE_CHAUDIERE, ax)
    else:
        # Comportement par défaut : afficher en popup
        plot_chaudiere(df_chaudiere, COLONNES_TEMP_CHAUDIERE, COLONNES_PUISSANCE_CHAUDIERE, plt.gca())
        plt.show()
    return df_chaudiere

def plot_chaudiere(df_chaudiere, COLONNES_TEMP_CHAUDIERE, COLONNES_PUISSANCE_CHAUDIERE, ax1):
    

    # Températures chaudières et fumées
    for col in COLONNES_TEMP_CHAUDIERE:
        if col in df_chaudiere.columns:
            ax1.plot(df_chaudiere['timestamp'], df_chaudiere[col], label=col)
    ax1.set_ylabel("Température (°C)")
    ax1.set_xlabel("Date")
    ax1.grid(True)
    ax1.legend(loc='upper left')

    # Deuxième axe pour la puissance
    ax2 = ax1.twinx()
    for col in COLONNES_PUISSANCE_CHAUDIERE:
        if col in df_chaudiere.columns:
            ax2.plot(df_chaudiere['timestamp'], df_chaudiere[col], linestyle='--', alpha=0.7, label=col)
    ax2.set_ylabel("Puissance (%)")
    ax2.legend(loc='upper right')

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %Hh'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
    ax1.figure.tight_layout()
    

def visualiser_chauffage(db_path, start=None, end=None, afficher_infos=True, ax=None):
    """
    Charge les données de chauffage 1 sur une période donnée et affiche le graphique.
    
    Returns:
        DataFrame pandas avec les données chargées
    """
    if start and not end:
        end = start + timedelta(days=1)

    df_chauffage1 = lire_donnees_chauffage(db_path, start, end)

    if df_chauffage1.empty:
        print("⚠️ Aucune donnée trouvée dans cette période.")
        return df_chauffage1
    duree = (df_chauffage1['timestamp'].max() - df_chauffage1['timestamp'].min()).days
    
    colonnes = [
        'chauffage1_depart_reel',
        'chauffage1_depart_consigne',
        'chauffage1_retour_reel',
        'chauffage1_retour_consigne'
    ]

    if duree > 3:
        print(f"📉 Durée = {duree} jours → lissage automatique par heure")
        
    df_chauffage1 = lissage(df_chauffage1, colonnes, periode='1H')

    if afficher_infos:
        print(f"✅ {len(df_chauffage1)} lignes chargées")
        print(f"Période : de {df_chauffage1['timestamp'].min()} à {df_chauffage1['timestamp'].max()}")
        for col in colonnes:
            if col in df_chauffage1.columns:
                print(f"{col} : min={df_chauffage1[col].min():.1f}°C / max={df_chauffage1[col].max():.1f}°C")

    if ax is not None:
        plot_chauffage1(df_chauffage1, ax)
    else:
        # Comportement par défaut : afficher en popup
        plot_chauffage1(df_chauffage1, plt.gca())
        plt.show()
    return df_chauffage1

def plot_chauffage1(df_chauffage1, ax1):
    """
    Affiche les courbes principales de température et de consigne du chauffage1.
    """
    colonnes = [
        'chauffage1_depart_reel',
        'chauffage1_depart_consigne',
        'chauffage1_retour_reel',
        'chauffage1_retour_consigne'
    ]
    for col in colonnes:
        if col in df_chauffage1.columns:
            ax1.plot(df_chauffage1['timestamp'], df_chauffage1[col], label=col)
    ax1.set_title("Températures départ / retour - Chauffage 1")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Température (°C)")
    ax1.grid(True)
    ax1.legend()
    ax1.figure.tight_layout()


def visualiser_ecs(db_path, start=None, end=None, afficher_infos=True, ax=None):
    """
    Charge les données ECS sur une période donnée, lisse si nécessaire, et affiche le graphique.
    
    Returns:
        DataFrame pandas avec les données chargées
    """
    if start and not end:
        end = start + timedelta(days=1)

    df_ecs = lire_donnees_ecs(db_path)  # ⛔ start/end traités après

    if df_ecs.empty:
        print("⚠️ Aucune donnée ECS trouvée.")
        return df_ecs

    if "timestamp" not in df_ecs.columns:
        print("❌ Colonne 'timestamp' absente dans les données ECS.")
        return pd.DataFrame()

    # ⏳ Filtrage par date
    if start or end:
        df_ecs = filtrer_par_date(
            df_ecs,
            start or df_ecs["timestamp"].min(),
            end or df_ecs["timestamp"].max()
        )

    

    # 🔢 Calcul de la durée pour décider du lissage
    duree = (df_ecs["timestamp"].max() - df_ecs["timestamp"].min()).days

    colonnes = [
        'ecs_entree_reelle',
        'ecs_consigne',
        'ecs_sortie_reelle'
    ]

    #if duree > 3:
    #    print(f"📉 Durée = {duree} jours → lissage automatique par heure")
    #    df_ecs = lissage(df_ecs, colonnes, periode='1H')

    if afficher_infos:
        print(f"✅ {len(df_ecs)} lignes ECS chargées")
        print(f"Période : de {df_ecs['timestamp'].min()} à {df_ecs['timestamp'].max()}")
        for col in colonnes:
            if col in df_ecs.columns:
                print(f"{col} : min={df_ecs[col].min():.1f}°C / max={df_ecs[col].max():.1f}°C")
            else:
                print(f"⚠️ Colonne {col} absente dans les données ECS")

    # 📈 Affichage
    if ax is not None:
        plot_ecs(df_ecs, ax)
    else:
        fig, ax_local = plt.subplots()
        plot_ecs(df_ecs, ax_local)
        fig.tight_layout()
        ax.figure.tight_layout()


    return df_ecs

def plot_ecs(df_ecs, ax1):
    """
    Affiche l'évolution des températures et de la pompe ECS.
    """
    df_ecs = df_ecs.sort_values("timestamp")
    colonnes_temp = ['ecs_entree_reelle', 'ecs_sortie_reelle', 'ecs_consigne']
    colonnes_temp = [col for col in colonnes_temp if col in df_ecs.columns]


    # Tracé des températures sur ax1
    for col in colonnes_temp:
        ax1.plot(df_ecs['timestamp'], df_ecs[col], label=col)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Température (°C)")
    ax1.grid(True)
    ax1.legend(loc='upper left')

    # ✅ Ajout des heures sur l'axe X
    ax1.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %Hh'))
    for label in ax1.xaxis.get_majorticklabels():
        label.set_rotation(45)
        label.set_ha('right')



    # Tracé de la pompe ECS (sur un 2e axe y)
    if 'ecs_pompe' in df_ecs.columns:
        ax2 = ax1.twinx()
        ax2.plot(df_ecs['timestamp'], df_ecs['ecs_pompe'], color='black', alpha=0.3, label='ecs_pompe')
        ax2.set_ylabel("État Pompe ECS")
        ax2.legend(loc='upper right')

    ax1.set_title("Évolution ECS : températures et pompe")
    ax1.figure.tight_layout()

    


if __name__ == "__main__":
    #df_chauffage1 = lire_donnees_chauffage(DB_FILE, start='2025-01-01', end='2025-01-03')
    #plot_chauffage1(df_chauffage1)
    #df_ecs = lire_donnees_ecs(DB_FILE, start='2025-01-01', end='2025-01-03')
    #plot_ecs(df_ecs)
    df_chaudiere = lire_donnees_chaudiere(DB_FILE, start='2025-01-01', end='2025-01-03')
    plot_chaudiere(df_chaudiere, COLONNES_TEMP_CHAUDIERE, COLONNES_PUISSANCE_CHAUDIERE, ax1=None)

