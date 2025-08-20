from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QSize, pyqtProperty
from PyQt5.QtGui import QColor, QPainter, QBrush


class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setChecked(False)
        self.setCursor(Qt.PointingHandCursor)

        # Position initiale du cercle
        self._circle_position = 3

        # Animation du cercle
        self.animation = QPropertyAnimation(self, b"circle_pos", self)
        self.animation.setDuration(200)  # Durée en ms

        # Connecter l'état du toggle à l'animation
        self.stateChanged.connect(self.start_transition)

    def start_transition(self, value):
        """Lance l'animation lorsque l'état change"""
        self.animation.stop()
        if value:
            self.animation.setStartValue(self._circle_position)
            self.animation.setEndValue(self.width() - 17)  # Ajusté selon la taille
        else:
            self.animation.setStartValue(self._circle_position)
            self.animation.setEndValue(3)
        self.animation.start()

    # Propriété animable
    def get_circle_pos(self):
        return self._circle_position

    def set_circle_pos(self, pos):
        self._circle_position = pos
        self.update()

    circle_pos = pyqtProperty(int, fget=get_circle_pos, fset=set_circle_pos)

    def paintEvent(self, event):
        """Dessine le toggle et le cercle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fond
        if self.isChecked():
            painter.setBrush(QBrush(QColor("#4CAF50")))  # Vert
        else:
            painter.setBrush(QBrush(QColor("#ccc")))     # Gris
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRect(0, 0, self.width(), self.height()), self.height()//2, self.height()//2)

        # Cercle
        painter.setBrush(QBrush(QColor("#fff")))
        painter.drawEllipse(QRect(self._circle_position, 3, self.height() - 6, self.height() - 6))

    def sizeHint(self):
        """Taille par défaut"""
        return QSize(40, 20)
