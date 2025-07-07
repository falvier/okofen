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
from matplotlib.dates import date2num
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
    
    if ax1 is None:
        fig, ax1 = plt.subplots(figsize=(12, 7))
    else:
        fig = ax1.figure

    # Températures chaudières et fumées
    for col in COLONNES_TEMP_CHAUDIERE:
        if col in df_chaudiere.columns:
            ax1.plot(df_chaudiere['timestamp'], df_chaudiere[col], label=col)
    ax1.set_ylabel("Température (°C)")
    ax1.grid(True)
    
    


    # Deuxième axe pour la puissance
    ax2 = ax1.twinx()
    for col in COLONNES_PUISSANCE_CHAUDIERE:
        if col in df_chaudiere.columns:
            ax2.plot(df_chaudiere['timestamp'], df_chaudiere[col], linestyle='--', alpha=0.7, label=col)
    ax2.set_ylabel("Puissance (%)")

    # Création d'un second axe X (en bas), pour afficher les heures
    ax3 = ax1.twiny()

    # Pour les dates : sur ax3, on affiche uniquement le jour et mois, sans heure
    dates_uniques = pd.date_range(
        start=df_chaudiere['timestamp'].dt.normalize().min(),
        end=df_chaudiere['timestamp'].dt.normalize().max(),
        freq='D'
    )
    dates_num = date2num(dates_uniques)

    # Décaler l'axe ax3 vers le bas (en dessous de ax1)
    ax3.spines['bottom'].set_position(('outward', 30))
    ax3.xaxis.set_ticks_position('bottom')
    ax3.xaxis.set_label_position('bottom')
    # Centrer le label de l'axe x (dates)
    ax3.xaxis.set_label_coords(0.5, -0.3)  # 0.5 = centre horizontal, -0.3 = un peu plus bas sous l'axe
    # Eventuellement, forcer les limites pour que les ticks s'étalent bien
    ax3.set_xlim(ax1.get_xlim())


    # Formatter et locator pour heures
    ax1.xaxis.set_major_locator(mdates.HourLocator(byhour=[0,6,12,18]))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))

    # Place les ticks sur ax3 à la position des dates normalisées
    ax3.set_xticks(dates_num)

    # Définit les labels des ticks sous forme 'jour/mois' sans heure
    ax3.set_xticklabels([d.strftime('%d/%m') for d in dates_uniques])

     # Ajuste rotation et padding pour éviter chevauchement
    ax3.xaxis.set_tick_params(rotation=0)
    ax3.tick_params(axis='x', which='major', pad=15)
    ax3.grid(False)

    # Récupérer les handles et labels des deux axes
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()

    # Légende combinée sous le graphique
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2,
               loc='upper center', bbox_to_anchor=(0.5, -0.25),
               ncol=2, fancybox=True, shadow=True)

    for label in ax1.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
    fig.subplots_adjust(bottom=0.25)
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
    
    colonnes = [col for col in COLONNES_CHAUFFAGE_TEMPERATURE if col in df_chauffage1.columns]


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
    colonnes = COLONNES_CHAUFFAGE_TEMPERATURE


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

    df_ecs = lire_donnees_ecs(db_path, start, end)  

    if df_ecs.empty:
        print("⚠️ Aucune donnée ECS trouvée.")
        return df_ecs
    
    if "timestamp" not in df_ecs.columns:
        print("❌ Colonne 'timestamp' absente dans les données ECS.")
        return pd.DataFrame()
    
    
    

    # 🔢 Calcul de la durée pour décider du lissage
    duree = (df_ecs["timestamp"].max() - df_ecs["timestamp"].min()).days

    colonnes = [col for col in COLONNES_ECS if col in df_ecs.columns]


    if duree > 3:
        print(f"📉 Durée = {duree} jours → lissage automatique par heure")
        df_ecs = lissage(df_ecs, colonnes, periode='1H')

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
    colonnes_temp = [col for col in COLONNES_ECS if col in df_ecs.columns and col != 'timestamp']

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


    '''
    # Tracé de la modulation de puissance de la chaudière (sur un 2e axe y)
    if 'modulation_puissance_chaudiere' in df_ecs.columns:
        ax2 = ax1.twinx()
        ax2.plot(df_ecs['timestamp'], df_ecs['modulation_puissance_chaudiere'], color='black', alpha=0.3, label='modulation_puissance_chaudiere')
        ax2.set_ylabel("modulation_puissance_chaudiere (%)")
        ax2.legend(loc='upper right')
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(handles2, labels2, loc='upper right')

    ax1.set_title("Évolution ECS : températures et consigne")
    ax1.figure.tight_layout()
    '''
    


if __name__ == "__main__":
    #df_chauffage1 = lire_donnees_chauffage(DB_FILE, start='2025-01-01', end='2025-01-03')
    #plot_chauffage1(df_chauffage1)
    #df_ecs = lire_donnees_ecs(DB_FILE, start='2025-01-01', end='2025-01-03')
    #plot_ecs(df_ecs)
    df_chaudiere = lire_donnees_chaudiere(DB_FILE, start='2025-01-01', end='2025-01-03')
    plot_chaudiere(df_chaudiere, COLONNES_TEMP_CHAUDIERE, COLONNES_PUISSANCE_CHAUDIERE, ax1=None)

