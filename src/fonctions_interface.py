#fonctions_interface.py

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
from src.class_interface import (
    WorkerThread,
    MainWindow,
    CalendarChauffage,
    GrapheWidget,
    PopupGraphique
)



