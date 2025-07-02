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
    QCalendarWidget
    )
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QTextCharFormat, QColor
from src.fonctions import (
    lire_jours_actifs_sqlite,
    extraire_dates_disponibles_sqlite)
from src.config import DB_FILE
from src.database import creer_vue_jours_actifs
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from src.visualisation import (
    visualiser_chaudiere,
    visualiser_chauffage,
    visualiser_ecs)



class CalendarChauffage(QCalendarWidget):
    def __init__(self, jours_actifs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jours_actifs = jours_actifs
        self.formater_jours_actifs()

    def formater_jours_actifs(self):
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("orange"))  # Tu peux choisir une autre couleur
        for jour in self.jours_actifs:
            qdate = QDate(jour.year, jour.month, jour.day)
            self.setDateTextFormat(qdate, fmt)

class GrapheWidget(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        super().__init__(fig)
        self.setParent(parent)
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

        self.ax.legend()
        self.draw()



def lancer_interface():
    creer_vue_jours_actifs()
    app = QApplication([])
    fenetre = QWidget()
    fenetre.setWindowTitle("Interface Chaudière")

    layout = QVBoxLayout()

    graphe_widget = GrapheWidget()
    layout.addWidget(graphe_widget)
    print(type(graphe_widget))



    # Récupérer les dates disponibles
    dates_dispo = extraire_dates_disponibles_sqlite()
    if not dates_dispo:
        layout.addWidget(QLabel("❌ Aucune date disponible dans les fichiers CSV."))
        fenetre.setLayout(layout)
        fenetre.show()
        app.exec_()
        return

    min_date = QDate(dates_dispo[0].year, dates_dispo[0].month, dates_dispo[0].day)
    max_date = QDate(dates_dispo[-1].year, dates_dispo[-1].month, dates_dispo[-1].day)

    # Légende pour les jours en orange
    legende_layout = QHBoxLayout()
    couleur = QLabel()
    couleur.setFixedSize(20, 20)
    couleur.setStyleSheet("background-color: orange; border: 1px solid black;")
    texte_legende = QLabel("= jours avec chauffage actif")
    legende_layout.addWidget(couleur)
    legende_layout.addWidget(texte_legende)
    layout.addLayout(legende_layout)

    # Sélection du mode
    layout.addWidget(QLabel("Sélection du mode de date :"))

    bouton_jour = QRadioButton("Date unique")
    bouton_intervalle = QRadioButton("Intervalle de dates")
    bouton_jour.setChecked(True)

    layout_mode = QHBoxLayout()
    layout_mode.addWidget(bouton_jour)
    layout_mode.addWidget(bouton_intervalle)
    layout.addLayout(layout_mode)

   # Widget pour date unique avec surlignage des jours de chauffage
    # Création des 3 calendriers séparés
    cal_unique = CalendarChauffage(set())
    cal_debut = CalendarChauffage(set())
    cal_fin = CalendarChauffage(set())

    def charger_et_colorier_chauffage():
        try:
            jours_actifs = lire_jours_actifs_sqlite()

            #print(f"🔥 {len(jours_actifs)} jours actifs trouvés :", sorted(list(jours_actifs))[:5], "...")

            for cal in (cal_unique, cal_debut, cal_fin):
                cal.jours_actifs = jours_actifs
                cal.formater_jours_actifs()
        except Exception as e:
            print("❌ Erreur lors du chargement des jours actifs :", e)

    widget_date_unique = QDateEdit()
    widget_date_unique.setCalendarPopup(True)
    

    widget_date_unique.setDate(min_date)
    widget_date_unique.setMinimumDate(min_date)
    widget_date_unique.setMaximumDate(max_date)
    layout.addWidget(widget_date_unique)


    # Widget pour intervalle
    intervalle_layout = QHBoxLayout()
    widget_date_debut = QDateEdit()
    widget_date_fin = QDateEdit()

    widget_date_unique.setCalendarWidget(cal_unique)

    widget_date_debut.setCalendarPopup(True)
    widget_date_debut.setCalendarWidget(cal_debut)

    widget_date_fin.setCalendarPopup(True)
    widget_date_fin.setCalendarWidget(cal_fin)


    widget_date_debut.setDate(min_date)
    widget_date_fin.setDate(max_date)

    intervalle_layout.addWidget(QLabel("De :"))
    intervalle_layout.addWidget(widget_date_debut)
    intervalle_layout.addWidget(QLabel("à"))
    intervalle_layout.addWidget(widget_date_fin)
    intervalle_layout_widget = QWidget()
    intervalle_layout_widget.setLayout(intervalle_layout)
    intervalle_layout_widget.setVisible(False)  # Masqué par défaut
    layout.addWidget(intervalle_layout_widget)

    

    # Réaction au changement de bouton
    def changer_mode():
        widget_date_unique.setVisible(bouton_jour.isChecked())
        intervalle_layout_widget.setVisible(bouton_intervalle.isChecked())

    bouton_jour.toggled.connect(changer_mode)
    bouton_intervalle.toggled.connect(changer_mode)

    # Choix du graphique
    layout.addWidget(QLabel("Choix du graphique à afficher :"))

    bouton_chaudiere = QRadioButton("Chaudière")
    bouton_chauffage = QRadioButton("Chauffage")
    bouton_ecs = QRadioButton("ECS")

    # On choisit un par défaut, par exemple "Chaudière"
    bouton_chaudiere.setChecked(True)

    layout_graphique = QHBoxLayout()
    layout_graphique.addWidget(bouton_chaudiere)
    layout_graphique.addWidget(bouton_chauffage)
    layout_graphique.addWidget(bouton_ecs)
    layout.addLayout(layout_graphique)

    # Groupe exclusif (utile pour vérifier quel bouton est coché)
    groupe_graphique = QButtonGroup()
    groupe_graphique.addButton(bouton_chaudiere)
    groupe_graphique.addButton(bouton_chauffage)
    groupe_graphique.addButton(bouton_ecs)



    # Bouton valider
    bouton_valider = QPushButton("Valider")
    layout.addWidget(bouton_valider)

    # Action de validation
    def on_valider():
        if bouton_jour.isChecked():
            date = widget_date_unique.date().toPyDate()
            date_debut = date
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

        print(f"📊 Graphique choisi : {choix_graph}")

        graphe_widget.tracer_graphique(choix_graph, date_debut, date_fin)

    bouton_valider.clicked.connect(on_valider)

    # Finalisation
    fenetre.setLayout(layout)
    fenetre.resize(600, 500)
    fenetre.show()
    QApplication.processEvents()  # Permet d’afficher l’interface tout de suite
    charger_et_colorier_chauffage()  # Lance le surlignage des jours chauffage

    app.exec_()


# Pour tester l'interface en lançant ce fichier seul
if __name__ == "__main__":
    lancer_interface()