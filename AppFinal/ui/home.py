# ui/home.py
from PyQt5.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QListWidget, QGroupBox, QDateTimeEdit, QWidget, QMessageBox
)
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import Qt, QUrl
from ui.toggle import ToggleSwitch
import datetime

class home_page:
    def __init__(self, parent=None):
        self.parent = parent
        self.current_meet_link = None

    def setup_menu(self):
        menubar = self.parent.menuBar()
        # Ajoutez ici vos menus si nécessaire

    def init_home_page(self):
        self.clear_layout(self.parent.layout)
        
        # Header Frame
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Partie gauche vide pour équilibrer
        header_layout.addStretch()

        # Partie centrale avec le message de bienvenue
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignCenter)
        
        welcome_label = QLabel("Welcome to MeetNotesAI")
        welcome_label.setFont(QFont("Roboto", 18, QFont.Bold))
        welcome_label.setStyleSheet(f"color: {self.parent.primary_color};")
        
        subtitle_label = QLabel("Take smart and structured meeting notes with ease!")
        subtitle_label.setFont(QFont("Roboto", 12))
        subtitle_label.setStyleSheet("color: #6b7280;")
        
        center_layout.addWidget(welcome_label, alignment=Qt.AlignCenter)
        center_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        
        header_layout.addWidget(center_widget, stretch=1)  # Prend l'espace disponible

        # Partie droite avec les boutons
        right_buttons = QHBoxLayout()
        right_buttons.setSpacing(10)
        right_buttons.setAlignment(Qt.AlignRight)

        # Bouton Join Meet - TOUJOURS VISIBLE
        self.meet_link_button = QPushButton("🔗 Join Google Meet")
        self.meet_link_button.setFixedHeight(40)
        self.meet_link_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.meet_link_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {self.secondary_color};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """)
        self.meet_link_button.clicked.connect(self.open_meeting_link)
        right_buttons.addWidget(self.meet_link_button)

        # Contrôle du thème
        self.emoji_label = QLabel("🌙")
        self.emoji_label.setFont(QFont("Arial", 14))
        
        self.theme_switch = self.create_theme_switch()
        self.theme_switch.setFixedSize(50, 24)
        right_buttons.addWidget(self.emoji_label)
        right_buttons.addWidget(self.theme_switch)

        header_layout.addLayout(right_buttons)
        self.parent.layout.addWidget(header_frame)

        event_group = QGroupBox("📅 Select Meeting from Calendar")
        event_layout = QVBoxLayout(event_group)

        self.event_combo = QComboBox()
        self.event_combo.setFixedHeight(40)
        self.event_combo.currentIndexChanged.connect(self.on_event_selected)

        
           

            # Résumé de l'événement (titre)
        self.event_summary_label = QLabel()
        self.event_summary_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.event_summary_label.setAlignment(Qt.AlignCenter)
        self.event_summary_label.setStyleSheet("""
            QLabel {
                color: #2d3748;
                padding: 4px 8px;
                background-color: #f7fafc;
                border-radius: 6px;
            }
        """)

    # Lien de l'événement
        self.event_link_label = QLabel()
        self.event_link_label.setFont(QFont("Segoe UI", 11))
        self.event_link_label.setAlignment(Qt.AlignCenter)
        self.event_link_label.setStyleSheet("""
            QLabel {
                color: #4a5568;
                padding: 6px 10px;
                background-color: #edf2f7;
                border-radius: 6px;
            }
        """)

            # Description de l'événement
        self.event_description_label = QLabel()
        self.event_description_label.setFont(QFont("Segoe UI", 11))
        self.event_description_label.setWordWrap(True)
        self.event_description_label.setAlignment(Qt.AlignCenter)
        self.event_description_label.setStyleSheet("""
            QLabel {
                color: #4a5568;
                padding: 6px 10px;
                background-color: #edf2f7;
                border-radius: 6px;
            }
        """)


        event_layout.addWidget(self.event_combo)
            #event_layout.addWidget(self.event_summary_label)
        event_layout.addWidget(self.event_link_label)
        event_layout.addWidget(self.event_description_label)
        self.layout.addWidget(event_group)
        
       

        # Détails de la réunion
        details_group = QGroupBox("📝 Meeting Details")
        details_layout = QVBoxLayout(details_group)
        
        # Date et heure
        dt_frame = QFrame()
        dt_layout = QHBoxLayout(dt_frame)
        dt_layout.addWidget(QLabel("🕒 Time:"))
        self.datetime_picker = QDateTimeEdit()
        self.datetime_picker.setCalendarPopup(True)
        self.datetime_picker.setEnabled(False)
        dt_layout.addWidget(self.datetime_picker)
        details_layout.addWidget(dt_frame)

        # Type de réunion
        type_frame = QFrame()
        type_layout = QHBoxLayout(type_frame)
        type_layout.addWidget(QLabel("📁 Type:"))
        self.meeting_type_combo = QComboBox()
        self.meeting_type_combo.addItems(["Project", "Technical", "HR", "Client", "Other"])
        type_layout.addWidget(self.meeting_type_combo)
        details_layout.addWidget(type_frame)
        self.parent.layout.addWidget(details_group)

        # Participants
        participant_box = QGroupBox("👥 Participants")
        participant_layout = QVBoxLayout(participant_box)
        self.participants_list = QListWidget()
        self.participants_list.setFixedHeight(150)
        participant_layout.addWidget(self.participants_list)
        self.layout.addWidget(participant_box)

        # Boutons d'action
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        buttons = [
            ("🚀 Start Notes", self.parent.show_note_interface, self.parent.primary_color),
            ("📜 History", self.parent.show_history, self.parent.secondary_color),
            ("📅 Schedule", self.parent.show_schedule_meeting_dialog, "#FF9800")
        ]
        
        for text, callback, color in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 120px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """)
            btn.clicked.connect(callback)
            buttons_layout.addWidget(btn)
        
        self.parent.layout.addWidget(buttons_frame)

    def create_theme_switch(self):
        """Crée un interrupteur de thème personnalisé"""
        switch = ToggleSwitch()
        switch.setFixedSize(50, 24)
        switch.stateChanged.connect(self.parent.toggle_theme)
        return switch

    def open_meeting_link(self):
        """Ouvre le lien de meeting dans le navigateur par défaut"""
        if hasattr(self, 'current_meet_link') and self.current_meet_link:
            QDesktopServices.openUrl(QUrl(self.current_meet_link))
        else:
            QMessageBox.warning(self, "Info", "No meeting link available")

    def clear_layout(self, layout):
        """Vide un layout de tous ses widgets"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())