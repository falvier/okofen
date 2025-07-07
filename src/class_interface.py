#fonction_interface.py


import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QDateEdit,
    QCalendarWidget,
    QDialog
    )
from PyQt5.QtCore import (QDate,
                          QThread,
                          pyqtSignal
)
from PyQt5.QtGui import QTextCharFormat, QColor
from src.fonctions import (
    lire_jours_actifs_sqlite,
    extraire_dates_disponibles_sqlite)
from src.config import DB_FILE
from src.database import creer_vue_jours_actifs, creer_base
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from src.visualisation import (
    visualiser_chaudiere,
    visualiser_chauffage,
    visualiser_ecs)
import subprocess

class WorkerThread(QThread):
    # Signal envoyé à la fin du traitement : succès booléen et message texte
    finished = pyqtSignal(bool, str)

    def run(self):
        try:
            # Lance la création ou mise à jour de la base
            creer_base()
            self.finished.emit(True, "Base mise à jour avec succès")
        except Exception as e:
            self.finished.emit(False, f"Erreur : {e}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal
        self.layout = QVBoxLayout()

        # Bouton pour mettre à jour la base de données
        self.btn_update_db = QPushButton("Mettre à jour la base")
        self.btn_update_db.clicked.connect(self.start_update_db)

        # Label pour afficher le statut de la mise à jour
        self.label_status = QLabel("Prêt")

        # Ajout des widgets au layout
        self.layout.addWidget(self.btn_update_db)
        self.layout.addWidget(self.label_status)
        self.setLayout(self.layout)

        # Initialisation du thread à None
        self.thread = None

    def start_update_db(self):
        # Désactive le bouton pour éviter les clics multiples
        self.btn_update_db.setEnabled(False)
        self.label_status.setText("Mise à jour en cours...")

        # Création et démarrage du thread Worker
        self.thread = WorkerThread()
        self.thread.finished.connect(self.on_update_finished)
        self.thread.start()

    def on_update_finished(self, success, message):
        # Affiche le message de fin de mise à jour
        self.label_status.setText(message)
        # Réactive le bouton
        self.btn_update_db.setEnabled(True)
        # Nettoie la référence du thread
        self.thread = None

        # Si la mise à jour a réussi, tu peux aussi recharger les données ici
        if success:
            # Par exemple, relancer un chargement ou un affichage
            # self.charge_donnees_et_met_a_jour_affichage()
            pass

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

class GrapheWidget(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(12, 7), dpi=100)
        super().__init__(fig)
        self.setParent(parent)
        self.setMinimumSize(1200, 700)
        self.ax = fig.add_subplot(111)
        fig.tight_layout()

    def tracer_graphique(self, type_graphique, date_debut, date_fin=None):
        self.ax.clear()

        if type_graphique == "Chaudière":
            visualiser_chaudiere(DB_FILE, date_debut, date_fin, ax=self.ax)
        elif type_graphique == "Chauffage":
            visualiser_chauffage(DB_FILE, date_debut, date_fin, ax=self.ax)
        elif type_graphique == "ECS":
            visualiser_ecs(DB_FILE, date_debut, date_fin, ax=self.ax)

class PopupGraphique(QDialog):
    def __init__(self, type_graphique, date_debut, date_fin=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Graphique : {type_graphique}")
        self.resize(700, 500)

        layout = QVBoxLayout()
        self.graphe = GrapheWidget(self)
        layout.addWidget(self.graphe)
        self.setLayout(layout)

        # Trace le graphique demandé
        self.graphe.tracer_graphique(type_graphique, date_debut, date_fin)
