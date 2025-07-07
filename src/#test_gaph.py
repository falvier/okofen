#test_gaph.py
import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))
import sys
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QCalendarWidget, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QScrollArea, QFrame, QMainWindow, QPushButton, QListWidgetItem, QListWidget,QAbstractItemView, 
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QTextCharFormat, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from src.config import COLONNES_CHAUDIERE
from src.config import DB_FILE
import glob
import os

# ---- Configuration des colonnes utiles ----
colonnes_utiles = COLONNES_CHAUDIERE
colonnes_utiles_sans_ts = [col for col in colonnes_utiles if col != 'timestamp']
colonnes_sql = ', '.join(['timestamp'] + colonnes_utiles_sans_ts)


class CalendarChauffage(QCalendarWidget):
    def __init__(self, jours_actifs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jours_actifs = jours_actifs
        self.formater_jours_actifs()

    def formater_jours_actifs(self):
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("orange"))  
        for jour in self.jours_actifs:
            qdate = QDate(jour.year, jour.month, jour.day)
            self.setDateTextFormat(qdate, fmt)

# ---- Interface principale ----
class GraphWindow(QWidget):
    def __init__(self, db_path = DB_FILE, table_name='chaudiere'):
        super().__init__()
        self.setWindowTitle("Visualisation des performances de la chaudière")

        # Chargement des données
        self.db_path = db_path
        self.table_name = table_name

        # Charger les données depuis SQLite
        self.df = self.load_data_sqlite()

        # Extraire les jours avec chauffage actif
        self.jours_actifs = self.extraire_jours_actifs()

        # Calendrier avec les jours actifs colorés
        self.calendar = CalendarChauffage(self.jours_actifs)
        self.calendar.selectionChanged.connect(self.on_date_selected)  # Connexion signal
        
        # Initialiser graphique
        self.canvas = FigureCanvas(Figure(figsize=(10, 6)))
        self.ax = self.canvas.figure.add_subplot(111)



        self.active_columns = list(colonnes_utiles)[:3]  # pré-sélection de 3 colonnes

        layout = QHBoxLayout()         # layout principal horizontal
        left_panel = QVBoxLayout()     # panneau de gauche vertical

        # Bouton pour actualiser
        bouton_actualiser = QPushButton("Mettre à jour le graphique")
        bouton_actualiser.clicked.connect(self.update_plot)
        left_panel.addWidget(bouton_actualiser)


        # ➕ Calendrier : inséré ici
        left_panel.addWidget(QLabel("Sélectionnez une date :"))
        left_panel.addWidget(self.calendar)

        # Cases à cocher pour les colonnes
        left_panel.addWidget(QLabel("Sélectionnez les courbes à afficher :"))

        checkbox_widget = QWidget()
        checkbox_layout = QVBoxLayout()
        

        self.checkboxes = {}
        for col in colonnes_utiles:
            checkbox = QCheckBox(col)
            checkbox.setChecked(col in self.active_columns)  # coche uniquement les 3 premières
            checkbox_layout.addWidget(checkbox)
            self.checkboxes[col] = checkbox

        checkbox_widget.setLayout(checkbox_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(checkbox_widget)
        left_panel.addWidget(scroll)

        # Ajout à la fenêtre principale
        layout.addLayout(left_panel)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def on_date_selected(self):
        self.update_plot_for_date(self.calendar.selectedDate())

    def update_plot_for_date(self, qdate):
        # Récupérer la date sélectionnée sous forme de datetime.date
            selected_date = qdate.toPyDate()

         # Filtrer les données du jour sélectionné
            df_filtered = self.df[self.df['timestamp'].dt.date == selected_date]

        # Rééchantillonner (moyenne toutes les 15 min)
            if not df_filtered.empty:
                df_filtered = df_filtered.set_index('timestamp').resample('15T').mean().reset_index()

        # Nettoyer l'axe avant de tracer
            self.ax.clear()
        

        # Tracer les courbes sélectionnées
            has_data = False
            for col, checkbox in self.checkboxes.items():
                if checkbox.isChecked() and col in df_filtered.columns:
                    self.ax.plot(df_filtered['timestamp'], df_filtered[col], label=col)
                    has_data = True

            if has_data:
                self.ax.set_title(f"Données du {selected_date}")
                self.ax.legend()
            else:
                self.ax.set_title(f"Aucune donnée à afficher pour le {selected_date}")

            self.canvas.draw()


       
    

    def extraire_jours_actifs(self):
            # Exemple simple : jours où 'modulation_puissance_chaudiere' > 0
            jours = set()
            for dt, puissance in zip(self.df['timestamp'], self.df['modulation_puissance_chaudiere']):
                if puissance > 0:
                    jours.add(dt.date())  # on garde uniquement la date (sans l'heure)
            return sorted(jours)

    def load_data_sqlite(self):
        conn = sqlite3.connect(self.db_path)
        # On s'assure que 'timestamp' n'est pas dupliqué
        colonnes_a_selectionner = list(colonnes_utiles)
        if "timestamp" not in colonnes_a_selectionner:
            colonnes_a_selectionner.insert(0, "timestamp")

        colonnes_str = ", ".join(colonnes_a_selectionner)
        query = f"SELECT {colonnes_str} FROM {self.table_name}"
        df = pd.read_sql_query(query, conn)
        print("Colonnes récupérées :", df.columns.tolist())  # Pour vérifier
        conn.close()

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        return df

    
    
    def update_plot(self):
    # Récupérer les colonnes cochées
        selected_columns = [col for col, checkbox in self.checkboxes.items() if checkbox.isChecked()]

        self.ax.clear()  # Nettoyer l'axe pour rafraîchir le graphique

        if not selected_columns:
            self.ax.set_title("Aucune colonne sélectionnée")
        else:
            for col in selected_columns:
                self.ax.plot(self.df['timestamp'], self.df[col], label=col)

            self.ax.set_title("Courbes sélectionnées")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Valeur")
            self.ax.legend()

        self.canvas.draw()



# ---- Lancement de l'application ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    sys.exit(app.exec_())
