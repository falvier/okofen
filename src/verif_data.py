import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))

import sqlite3
import pandas as pd
from src.config import DATA_DIR, COLONNES_CHAUFFAGE_COMPLET, DB_FILE
from src.fonctions import etat_chauffage_par_date_sqlite


def test_etat_chauffage():
    print("📊 Test de la fonction 'etat_chauffage_par_date_sqlite()'")
    print(f"📁 Base de données utilisée : {DB_FILE}")

    etats = etat_chauffage_par_date_sqlite()

    if not etats:
        print("⚠️ Aucun jour trouvé ou erreur de lecture.")
        return

    actifs = sum(1 for actif in etats.values() if actif)
    inactifs = sum(1 for actif in etats.values() if not actif)

    print(f"✅ Jours trouvés : {len(etats)}")
    print(f"🔥 Jours avec chauffage actif : {actifs}")
    print(f"❄️ Jours sans activité de chauffage : {inactifs}")
    print("")

    # Affiche les 10 premiers résultats
    for jour in sorted(etats)[:10]:
        print(f"{jour} : {'✅ Actif' if etats[jour] else '❌ Inactif'}")

