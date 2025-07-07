import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QButtonGroup, QDateEdit
)
from PyQt5.QtCore import QDate

# Ajout du dossier racine au path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.fonctions import lire_jours_actifs_sqlite, extraire_dates_disponibles_sqlite
from src.config import DB_FILE
from src.database import creer_vue_jours_actifs, creer_base
from src.class_interface import CalendarChauffage, PopupGraphique, WorkerThread


def lancer_interface():
    # === INITIALISATION APPLICATION ===
    creer_vue_jours_actifs()
    app = QApplication([])
    fenetre = QWidget()
    fenetre.setWindowTitle("Interface Chaudière")
    fenetre.popups_ouverts = []
    layout = QVBoxLayout()

    # === FONCTIONS INTERNES ===
    def charger_et_colorier_chauffage():
        try:
            jours_actifs = lire_jours_actifs_sqlite()
            for cal in (cal_unique, cal_debut, cal_fin):
                cal.jours_actifs = jours_actifs
                cal.formater_jours_actifs()
        except Exception as e:
            print("❌ Erreur lors du chargement des jours actifs :", e)

    def start_update_db():
        label_status.setText("⏳ Mise à jour en cours...")
        btn_update_db.setEnabled(False)
        fenetre.thread = WorkerThread()

        def on_finished(success, message):
            label_status.setText(message)
            btn_update_db.setEnabled(True)
            charger_et_colorier_chauffage()

        fenetre.thread.finished.connect(on_finished)
        fenetre.thread.start()

    def changer_mode():
        widget_date_unique.setVisible(bouton_jour.isChecked())
        intervalle_layout_widget.setVisible(bouton_intervalle.isChecked())

    def on_valider():
        if bouton_jour.isChecked():
            date_debut = widget_date_unique.date().toPyDate()
            date_fin = date_debut
        else:
            date_debut = widget_date_debut.date().toPyDate()
            date_fin = widget_date_fin.date().toPyDate()

        if bouton_chaudiere.isChecked():
            choix_graph = "Chaudière"
        elif bouton_chauffage.isChecked():
            choix_graph = "Chauffage"
        else:
            choix_graph = "ECS"

        popup = PopupGraphique(choix_graph, date_debut, date_fin)
        fenetre.popups_ouverts.append(popup)
        popup.show()

    def fermer_toutes_popups():
        for popup in fenetre.popups_ouverts:
            popup.close()
        fenetre.popups_ouverts.clear()

    # === STATUT & BOUTON MISE À JOUR ===
    label_status = QLabel("✅ Prêt")
    layout.addWidget(label_status)

    btn_update_db = QPushButton("Mettre à jour la base")
    layout.addWidget(btn_update_db)
    btn_update_db.clicked.connect(start_update_db)

    # === RÉCUPÉRATION DES DATES DISPONIBLES ===
    dates_dispo = extraire_dates_disponibles_sqlite()
    if not dates_dispo:
        layout.addWidget(QLabel("❌ Aucune date disponible dans les fichiers CSV."))
        fenetre.setLayout(layout)
        fenetre.show()
        app.exec_()
        return

    min_date = QDate(dates_dispo[0].year, dates_dispo[0].month, dates_dispo[0].day)
    max_date = QDate(dates_dispo[-1].year, dates_dispo[-1].month, dates_dispo[-1].day)

    # === LÉGENDE JOURS CHAUFFAGE ===
    legende_layout = QHBoxLayout()
    couleur = QLabel()
    couleur.setFixedSize(20, 20)
    couleur.setStyleSheet("background-color: orange; border: 1px solid black;")
    legende_layout.addWidget(couleur)
    legende_layout.addWidget(QLabel("= jours avec chauffage actif"))
    layout.addLayout(legende_layout)

    # === MODE DE DATE : JOUR OU INTERVALLE ===
    layout.addWidget(QLabel("Sélection du mode de date :"))
    bouton_jour = QRadioButton("Date unique")
    bouton_intervalle = QRadioButton("Intervalle de dates")
    bouton_jour.setChecked(True)

    layout_mode = QHBoxLayout()
    layout_mode.addWidget(bouton_jour)
    layout_mode.addWidget(bouton_intervalle)
    layout.addLayout(layout_mode)

    # === CALENDRIERS PERSONNALISÉS ===
    cal_unique = CalendarChauffage(set())
    cal_debut = CalendarChauffage(set())
    cal_fin = CalendarChauffage(set())

    # === SÉLECTION DATE UNIQUE ===
    widget_date_unique = QDateEdit()
    widget_date_unique.setCalendarPopup(True)
    widget_date_unique.setCalendarWidget(cal_unique)
    widget_date_unique.setDate(min_date)
    widget_date_unique.setMinimumDate(min_date)
    widget_date_unique.setMaximumDate(max_date)
    layout.addWidget(widget_date_unique)

    # === SÉLECTION INTERVALLE ===
    intervalle_layout = QHBoxLayout()
    widget_date_debut = QDateEdit()
    widget_date_fin = QDateEdit()

    widget_date_debut.setCalendarPopup(True)
    widget_date_debut.setCalendarWidget(cal_debut)
    widget_date_debut.setDate(min_date)

    widget_date_fin.setCalendarPopup(True)
    widget_date_fin.setCalendarWidget(cal_fin)
    widget_date_fin.setDate(max_date)

    intervalle_layout.addWidget(QLabel("De :"))
    intervalle_layout.addWidget(widget_date_debut)
    intervalle_layout.addWidget(QLabel("à"))
    intervalle_layout.addWidget(widget_date_fin)

    intervalle_layout_widget = QWidget()
    intervalle_layout_widget.setLayout(intervalle_layout)
    intervalle_layout_widget.setVisible(False)
    layout.addWidget(intervalle_layout_widget)

    bouton_jour.toggled.connect(changer_mode)
    bouton_intervalle.toggled.connect(changer_mode)

    # === CHOIX DU GRAPHIQUE ===
    layout.addWidget(QLabel("Choix du graphique à afficher :"))
    bouton_chaudiere = QRadioButton("Chaudière")
    bouton_chauffage = QRadioButton("Chauffage")
    bouton_ecs = QRadioButton("ECS")
    bouton_chaudiere.setChecked(True)

    layout_graphique = QHBoxLayout()
    layout_graphique.addWidget(bouton_chaudiere)
    layout_graphique.addWidget(bouton_chauffage)
    layout_graphique.addWidget(bouton_ecs)
    layout.addLayout(layout_graphique)

    groupe_graphique = QButtonGroup()
    groupe_graphique.addButton(bouton_chaudiere)
    groupe_graphique.addButton(bouton_chauffage)
    groupe_graphique.addButton(bouton_ecs)

    # === BOUTON VALIDER ===
    bouton_valider = QPushButton("Valider")
    bouton_valider.clicked.connect(on_valider)
    layout.addWidget(bouton_valider)

    # === BOUTON FERMER LES FENÊTRES ===
    bouton_fermer_tout = QPushButton("Fermer toutes les fenêtres")
    bouton_fermer_tout.clicked.connect(fermer_toutes_popups)
    layout.addWidget(bouton_fermer_tout)

    # === FINALISATION ===
    fenetre.setLayout(layout)
    fenetre.resize(600, 500)
    fenetre.show()
    QApplication.processEvents()
    charger_et_colorier_chauffage()
    app.exec_()


if __name__ == "__main__":
    lancer_interface()
