from email.charset import BASE64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QSize, QUrl, QEasingCurve
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QPushButton, QListWidget,
    QAction, QLabel, QGroupBox, QMessageBox, QScrollArea,
    QDateTimeEdit, QFrame, QDialog, QTextBrowser, QLineEdit, 
    QCompleter, QInputDialog, QCheckBox, QSizePolicy,QGraphicsOpacityEffect,QListWidgetItem
)
from PyQt5.QtGui import QDesktopServices, QFont, QPalette, QColor, QIcon, QFontDatabase
from PyQt5.QtCore import Qt, QPropertyAnimation, QDateTime, QSize, QTimer,QTimeZone
import subprocess
import datetime
import sqlite3

import requests
from utils.translator import Translator

from ui.history_dialog import HistoryDialog
from PyQt5.QtCore import Qt, QEvent
import urllib.parse
import webbrowser
from PyQt5.QtGui import QMovie
from ui.toggle import ToggleSwitch
from ui.home import home_page
from ui.model import MomWorker, LoadingDialog, model
from ui.ms_graph_api import get_upcoming_ms_events as get_upcoming_events
from utils.auth import get_access_token
from ui.ms_graph_api import create_ms_event
from utils.ressource import resource_path

import os
import sqlite3

def get_user_db_path():
    """Retourne le chemin de la base de données pour l'utilisateur courant"""
    appdata = os.getenv('APPDATA') or os.path.expanduser("~/.config")
    db_dir = os.path.join(appdata, "MeetNotesAI")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "meeting_notes.db")

def get_user_token_path():
    """Retourne le chemin du token cache pour l'utilisateur courant"""
    appdata = os.getenv('APPDATA') or os.path.expanduser("~/.config")
    db_dir = os.path.join(appdata, "MeetNotesAI")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "token_cache.bin")

class MainWindow(QMainWindow, home_page, model):
    
    
    def __init__(self):
        super().__init__()
        home_page.__init__(self, parent=self)
        self.DB_PATH = get_user_db_path()
        self.TOKEN_PATH = get_user_token_path()
        self.init_db()
        
        self.translator = Translator("en")
        self.setWindowTitle("📝 MeetNotesAI - Smart Meeting Assistant")
        self.setMinimumSize(1200, 800)
        
        # Modern color palette
        self.primary_color = "#4361ee"
        self.secondary_color = "#3a0ca3"
        self.accent_color = "#4cc9f0"
        self.dark_bg = "#1a1a2e"
        self.light_bg = "#f8f9fa"
        self.card_bg = "#ffffff"
        self.text_color = "#14213d"
        self.highlight_color = "#3a0ca3"
        
        self.primary_color = "#4361ee"
        self.secondary_color = "#3a0ca3"
        self.accent_color = "#4fc3f7"
        self.light_bg = "#f8f9fa"
        self.dark_bg = "#1a1a2e"
        self.card_bg = "#ffffff"
        self.text_color = "#2d3748"
        
        # Shadow effect settings
        self.shadow_color = QColor(30, 30, 30, 40)
        
        self.note_types = [
            ("Decision", "✅", "#2ecc71"),
            ("Action", "🛠", "#3498db"),
            ("Discussion", "💬", "#e67e22")
        ]

        self.note_inputs = {}
        self.note_lists = {}
        self.participants = []

        self.current_meeting_type = ""
        self.current_datetime = None
        self.current_event = None
        self.generated_mom = ""

        # Initialize database
        self.init_db()

        self.setup_ui()
        self.setup_menu()
        self.load_google_events()
        self.apply_modern_theme()
        
        # Add subtle animation to the main window
        self.fade_in_animation()
        
        self.current_meet_link = None  # Ajouter cet attribut


    def fade_in_animation(self):
        """Add a subtle fade-in animation when the app starts"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.start()

    def init_db(self):
        self.conn = sqlite3.connect(self.DB_PATH)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                type TEXT,
                datetime TEXT,
                participants TEXT,
                mom_content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id INTEGER,
                note_type TEXT,
                content TEXT,
                FOREIGN KEY(meeting_id) REFERENCES meetings(id)
            )
        ''')
        
        self.conn.commit()
        
    def save_notes_to_db(self):
        try:
            participants_str = ", ".join([f"{name} ({role})" for name, role in self.participants])
        
            self.cursor.execute('''
                INSERT INTO meetings (title, type, datetime, participants, mom_content)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                getattr(self, "current_event", {}).get('summary', "Untitled"),
                self.current_meeting_type,
                self.current_datetime.toString(),
                participants_str,
                self.generated_mom if hasattr(self, 'generated_mom') else ""
            ))
        
            meeting_id = self.cursor.lastrowid
        
            for label, _, _ in self.note_types:
                raw_text = self.note_inputs[label].toPlainText().strip()
                if raw_text:
                    notes = [line.strip() for line in raw_text.splitlines() if line.strip()]
                    for note in notes:
                        self.cursor.execute('''
                            INSERT INTO notes (meeting_id, note_type, content)
                            VALUES (?, ?, ?)
                        ''', (meeting_id, label, note))
        
            self.conn.commit()
            
            # Utilisation correcte de show_notification
            self.show_notification("Meeting notes saved successfully!", "success")
    
        except Exception as e:
            # Utilisation correcte de show_notification
            self.show_notification(f"Failed to save notes: {str(e)}", "error")
    

    def apply_modern_theme(self, mode=None):
        """
        Applique un thème moderne complet avec support light/dark
        Args:
            mode: 'light' ou 'dark' (si None, détecte automatiquement)
        """
        # Détection automatique du mode si non spécifié
        if mode is None:
            mode = "dark" if hasattr(self, 'theme_switch') and self.theme_switch.isChecked() else "light"
        
        is_dark = mode == "dark"
        
        # Définition des couleurs dynamiques
        colors = {
            "bg": self.dark_bg if is_dark else self.light_bg,
            "text": "white" if is_dark else self.text_color,
            "widget": "#2d3748" if is_dark else self.card_bg,
            "border": "#4a5568" if is_dark else "#e2e8f0",
            "input_bg": "#2d3748" if is_dark else "white",
            "hover": "#4a5568" if is_dark else "#f1f5f9",
            "selection": "#4a6fa5" if is_dark else self.accent_color
        }

        # Stylesheet complet avec template
        stylesheet = f"""
            /* ===== STYLES DE BASE ===== */
            QMainWindow, QDialog, QWidget {{
                background-color: {colors['bg']};
                color: {colors['text']};
                font-family: 'Roboto';
            }}
            
            /* ===== TITRES ET TEXTES ===== */
            QLabel {{
                color: {colors['text']};
            }}
            
            QLabel#TitleLabel {{
                font-size: 24px;
                font-weight: 500;
                color: {self.primary_color};
            }}
            
            /* ===== BOUTONS ===== */
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-family: 'Roboto Medium';
                font-size: 14px;
                min-width: 120px;
            }}
            
            QPushButton:hover {{
                background-color: {self.secondary_color};
            }}
            
            QPushButton:pressed {{
                background-color: {self.secondary_color};
                padding-top: 11px;
                padding-bottom: 9px;
            }}
            
            QPushButton#SecondaryButton {{
                background-color: {'#4a5568' if is_dark else '#e9ecef'};
                color: {colors['text']};
            }}
            
            /* ===== CHAMPS DE SAISIE ===== */
            QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QDateTimeEdit {{
                background-color: {colors['input_bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 8px 12px;
                selection-background-color: {colors['selection']};
                selection-color: white;
            }}
            
            QComboBox::drop-down, QDateTimeEdit::drop-down {{
                width: 30px;
                border-left: 1px solid {colors['border']};
            }}
            
            /* ===== GROUPES ET CADRES ===== */
            QGroupBox {{
                background-color: {colors['widget']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 24px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
            
            /* ===== LISTES ET TABLES ===== */
            QListWidget, QTableView, QTreeView {{
                background-color: {colors['widget']};
                border: 1px solid {colors['border']};
                alternate-background-color: {'#2d3748' if is_dark else '#f8f9fa'};
            }}
            
            QListWidget::item, QTableView::item, QTreeView::item {{
                padding: 8px;
                border-bottom: 1px solid {colors['border']};
            }}
            
            QListWidget::item:hover, QTableView::item:hover, QTreeView::item:hover {{
                background-color: {colors['hover']};
            }}
            
            /* ===== BARRES DE DÉFILEMENT ===== */
            QScrollBar:vertical {{
                background: {colors['widget']};
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {'#4a5568' if is_dark else '#cbd5e1'};
                min-height: 20px;
                border-radius: 5px;
            }}
            
            /* ===== MENUS ===== */
            QMenuBar {{
                background-color: {self.primary_color};
                color: white;
            }}
            
            QMenu {{
                background-color: {colors['widget']};
                border: 1px solid {colors['border']};
            }}
            
            QMenu::item:selected {{
                background-color: {colors['selection']};
            }}
            
            /* ===== TOGGLE SWITCH PERSONNALISÉ ===== */
            ToggleSwitch {{
                background-color: {'#4a5568' if is_dark else '#e2e8f0'};
                border-radius: 15px;
            }}
            
            ToggleSwitch::handle {{
                background-color: white;
                width: 26px;
                height: 26px;
                border-radius: 13px;
            }}
            
            ToggleSwitch::handle:checked {{
                background-color: #4CAF50;
            }}
        """
        
        # Application du style
        self.setStyleSheet(stylesheet)
        
        # Configuration de la palette Qt
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(colors['bg']))
        palette.setColor(QPalette.WindowText, QColor(colors['text']))
        palette.setColor(QPalette.Base, QColor(colors['input_bg']))
        palette.setColor(QPalette.AlternateBase, QColor(colors['widget']))
        palette.setColor(QPalette.Text, QColor(colors['text']))
        palette.setColor(QPalette.Button, QColor(self.primary_color))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(colors['selection']))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)
        
        # Force la mise à jour immédiate
        self.update()

    def create_theme_switch(self):
        """Crée et configure l'interrupteur de thème"""
        theme_switch = ToggleSwitch()
        theme_switch.setFixedSize(50, 24)
        theme_switch.stateChanged.connect(self.toggle_theme)
        return theme_switch

    def toggle_theme(self, state):
        """Bascule entre les thèmes clair/sombre avec gestion complète"""
        theme = "dark" if state else "light"
        self.apply_modern_theme(theme)
        
        # Mise à jour visuelle immédiate
        if hasattr(self, 'emoji_label'):
            self.emoji_label.setText("☀️" if state else "🌙")
        # Pas besoin de setChecked ici pour éviter la récursion


    
    def show_notification(self, message, type="info"):
        """Show an animated notification message"""
        notification = QLabel(message)
        notification.setAlignment(Qt.AlignCenter)
        notification.setFixedHeight(50)
        notification.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        if type == "success":
            notification.setStyleSheet(f"""
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
                border-radius: 8px;
                padding: 10px;
            """)
        elif type == "error":
            notification.setStyleSheet(f"""
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                border-radius: 8px;
                padding: 10px;
            """)
        else:
            notification.setStyleSheet(f"""
                background-color: #e2e3e5;
                color: #383d41;
                border: 1px solid #d6d8db;
                border-radius: 8px;
                padding: 10px;
            """)
        
        # Correction ici : utiliser self.layout au lieu de self.layout()
        self.layout.insertWidget(0, notification)  # <-- Changement ici
        
        # Animate
        notification.setGraphicsEffect(QGraphicsOpacityEffect())
        notification.graphicsEffect().setOpacity(0)
        
        fade_in = QPropertyAnimation(notification.graphicsEffect(), b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Auto-remove after delay
        QTimer.singleShot(3000, lambda: self.fade_out_notification(notification))
        
        fade_in.start()

    def fade_out_notification(self, notification):
        fade_out = QPropertyAnimation(notification.graphicsEffect(), b"opacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        fade_out.finished.connect(lambda: notification.deleteLater())
        fade_out.start()

    def generate_email(self):
        if not hasattr(self, 'generated_mom') or not self.generated_mom:
            self.show_notification("Please generate MoM first!", "error")
            return

        try:
            to_emails = [email for email, _ in getattr(self, 'participants', [])]
            if not to_emails:
                self.show_notification("No participants found to send the email.", "error")
                return

            # Outlook utilise ";" comme séparateur
            to_str = ";".join(to_emails)

            meeting_title = (
                self.current_event.get('subject')
                or self.current_event.get('summary')
                or "Meeting"
            ) if self.current_event else "Meeting"

            subject = f"📝 Minutes of Meeting - {meeting_title}"
            body = (
                "Hello Team,\r\n\r\n"
                f"Please find below the minutes of our meeting \"{meeting_title}\":\r\n\r\n"
                f"{self.generated_mom}\r\n\r\n"
                "Best regards,\r\n"
            )

            # Encodage URL
            to_encoded = urllib.parse.quote(to_str)
            subject_encoded = urllib.parse.quote(subject)
            body_encoded = urllib.parse.quote(body)

            # Pour compte personnel → outlook.live.com
            outlook_url = (
                f"https://outlook.live.com/mail/deeplink/compose"
                f"?to={to_encoded}"
                f"&subject={subject_encoded}"
                f"&body={body_encoded}"
            )

            # Ouvre dans le navigateur par défaut
            webbrowser.open_new_tab(outlook_url)

        except Exception as e:
            self.show_notification(f"Failed to open Outlook draft: {str(e)}", "error")

    def show_history(self):
        dialog = HistoryDialog(self)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.light_bg};
                border-radius: 12px;
            }}
            QTableView {{
                background-color: {self.card_bg};
                border: 1px solid #e9ecef;
                border-radius: 8px;
                alternate-background-color: #f8f9fa;
            }}
            QHeaderView::section {{
                background-color: {self.primary_color};
                color: white;
                padding: 8px;
                border: none;
                font-family: 'Roboto Medium';
            }}
        """)
        dialog.exec_()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout with some spacing
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Initialize widgets with modern styling
        self.event_combo = QComboBox()
        self.event_combo.setFixedHeight(40)
        
        self.event_summary_label = QLabel()
        self.event_summary_label.setObjectName("TitleLabel")
        
        self.event_link_label = QLabel()
        self.event_link_label.hide()
        
        self.event_description_label = QLabel()
        self.event_description_label.setWordWrap(True)
        
        self.datetime_picker = QDateTimeEdit()
        self.datetime_picker.setCalendarPopup(True)
        self.datetime_picker.setFixedHeight(40)
        
        self.meeting_type_combo = QComboBox()
        self.meeting_type_combo.setFixedHeight(40)
        
        self.participants_list = QListWidget()
        self.participants_list.setFixedHeight(120)
        
        # Create theme switch
        self.theme_switch = self.create_theme_switch()

        self.init_home_page()
    def open_meeting_link(self):
        """Ouvre le lien Google Meet dans le navigateur par défaut"""
        if hasattr(self, 'current_meet_link') and self.current_meet_link:
            QDesktopServices.openUrl(QUrl(self.current_meet_link))
        else:
            self.show_notification("No meeting link available", "error")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def show_schedule_meeting_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("📅 Schedule Meeting")
        dialog.setMinimumWidth(500)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Apply modern styling
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.light_bg};
                font-family: 'Roboto';
            }}
            
            QLabel {{
                color: {self.text_color};
                font-size: 14px;
                font-weight: 500;
            }}
            
            QLineEdit, QTextEdit, QDateTimeEdit {{
                background-color: {self.card_bg};
                border: 1px solid #ced4da;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                min-height: 40px;
            }}
            
            QTextEdit {{
                min-height: 100px;
            }}
            
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border-radius: 8px;
                padding: 10px 15px;
                font-family: 'Roboto Medium';
                font-size: 14px;
                min-width: 100px;
            }}
            
            QPushButton:hover {{
                background-color: {self.secondary_color};
            }}
            
            QPushButton#SecondaryButton {{
                background-color: #e9ecef;
                color: {self.text_color};
            }}
            
            QPushButton#SecondaryButton:hover {{
                background-color: #dee2e6;
            }}
            
            QGroupBox {{
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)

        # Title field
        title_edit = QLineEdit()
        title_edit.setPlaceholderText("📌 Meeting Title")
        layout.addWidget(title_edit)

        # Description field
        desc_edit = QTextEdit()
        desc_edit.setPlaceholderText("📝 Description...")
        layout.addWidget(desc_edit)

        # Date/time fields
        time_layout = QHBoxLayout()
        
        start_group = QGroupBox("Start Time")
        start_layout = QVBoxLayout(start_group)
        start_picker = QDateTimeEdit(QDateTime.currentDateTime())
        start_picker.setCalendarPopup(True)
        start_picker.setDisplayFormat("MMM d, yyyy h:mm AP")
        start_layout.addWidget(start_picker)
        time_layout.addWidget(start_group)
        
        end_group = QGroupBox("End Time")
        end_layout = QVBoxLayout(end_group)
        end_picker = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))
        end_picker.setCalendarPopup(True)
        end_picker.setDisplayFormat("MMM d, yyyy h:mm AP")
        end_layout.addWidget(end_picker)
        time_layout.addWidget(end_group)
        
        layout.addLayout(time_layout)

        # Participants section
        participants_group = QGroupBox("👥 Participants")
        participants_layout = QVBoxLayout(participants_group)
        
        # Tags container for participants
        tags_container = QWidget()
        tags_layout = QHBoxLayout(tags_container)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(6)
        tags_layout.addStretch()

        tags_scroll = QScrollArea()
        tags_scroll.setWidgetResizable(True)
        tags_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tags_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tags_scroll.setWidget(tags_container)
        tags_scroll.setFixedHeight(50)
        participants_layout.addWidget(tags_scroll)
        
        participants_list = []

        def create_tag(email):
            tag = QFrame()
            tag.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.secondary_color};
                    border-radius: 12px;
                    padding: 2px 8px;
                }}
                QLabel {{
                    color: white;
                    font-size: 12px;
                }}
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 0;
                    min-width: 0;
                }}
                QPushButton:hover {{
                    color: #ff6b6b;
                }}
            """)
            tag_layout = QHBoxLayout(tag)
            tag_layout.setContentsMargins(4, 2, 4, 2)
            tag_layout.setSpacing(4)

            lbl = QLabel(email)
            remove_btn = QPushButton("×")
            remove_btn.setFixedSize(16, 16)
            remove_btn.clicked.connect(lambda: remove_participant(email))

            tag_layout.addWidget(lbl)
            tag_layout.addWidget(remove_btn)
            return tag

        def refresh_tags():
            # Clear existing tags
            for i in reversed(range(tags_layout.count())):
                item = tags_layout.takeAt(i)
                if item.widget():
                    item.widget().deleteLater()
            
            # Add current participants
            for email in participants_list:
                tags_layout.insertWidget(tags_layout.count()-1, create_tag(email))

        def remove_participant(email):
            if email in participants_list:
                participants_list.remove(email)
                refresh_tags()

        # Participant input field
        participant_input_layout = QHBoxLayout()
        participants_edit = QLineEdit()
        participants_edit.setPlaceholderText("Enter participant email...")
        add_btn = QPushButton("➕ Add")
        add_btn.setObjectName("SecondaryButton")
        add_btn.setFixedWidth(80)

        def add_participant():
            email = participants_edit.text().strip()
            if not email:
                return
                
            if "@" not in email:
                QMessageBox.warning(dialog, "Invalid Email", "Please enter a valid email address")
                return
                
            if email in participants_list:
                QMessageBox.warning(dialog, "Duplicate", "This participant is already added")
                return
                
            participants_list.append(email)
            refresh_tags()
            participants_edit.clear()

        add_btn.clicked.connect(add_participant)
        participants_edit.returnPressed.connect(add_participant)

        participant_input_layout.addWidget(participants_edit)
        participant_input_layout.addWidget(add_btn)
        participants_layout.addLayout(participant_input_layout)
        
        layout.addWidget(participants_group)

        # Buttons at bottom
        btn_box = QHBoxLayout()
        btn_box.setSpacing(15)
        
        create_btn = QPushButton("📅 Create Meeting")
        create_btn.setIcon(QIcon.fromTheme("calendar"))
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        
        btn_box.addStretch()
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(create_btn)
        layout.addLayout(btn_box)

        cancel_btn.clicked.connect(dialog.reject)

        def create_event():
            title = title_edit.text().strip()
            desc = desc_edit.toPlainText().strip()
            start_dt = start_picker.dateTime().toPyDateTime()
            end_dt = end_picker.dateTime().toPyDateTime()
            
            if not title:
                QMessageBox.warning(dialog, "Error", "Meeting title is required")
                return
                
            if not participants_list:
                QMessageBox.warning(dialog, "Error", "Please add at least one participant")
                return
                
            if start_dt >= end_dt:
                QMessageBox.warning(dialog, "Error", "End time must be after start time")
                return
                
            try:
                create_btn.setEnabled(False)
                create_btn.setText("Creating...")
                QApplication.processEvents()
                
                # 🔹 Création du meeting via Microsoft Graph
                from ui.ms_graph_api import create_ms_event
                access_token = get_access_token()  # Vous devez implémenter cette fonction

                event = create_ms_event(
                    access_token,
                    title,
                    desc,
                    start_dt,
                    end_dt,
                    participants_list
                )
                
                meet_link = event.get("joinUrl", "") or event.get("link", "No link available")
                
                # 🔹 Message succès
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("Meeting Created")
                msg_box.setText(f"Meeting created successfully!\n\nLink: {meet_link}")
                
                copy_btn = msg_box.addButton("Copy Link", QMessageBox.ActionRole)
                email_btn = msg_box.addButton("Email Participants", QMessageBox.ActionRole)
                msg_box.addButton(QMessageBox.Ok)
                
                msg_box.exec_()
                
                if msg_box.clickedButton() == copy_btn:
                    QApplication.clipboard().setText(meet_link)
                
                elif msg_box.clickedButton() == email_btn:
                    self.send_meeting_invites_ms(title, start_dt, end_dt, meet_link, participants_list, desc)
                
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to create meeting:\n{str(e)}")
            finally:
                create_btn.setEnabled(True)
                create_btn.setText("📅 Create Meeting")

                

        create_btn.clicked.connect(create_event)
            
        dialog.exec_()


    def send_meeting_invites_ms(self, title, start_dt, end_dt, meet_link, participants, description=""):
        """
        Ouvre un draft Outlook Web pré-rempli avec les détails du meeting
        """
        try:
            if not participants:
                QMessageBox.warning(self, "No Participants", "Please add at least one participant")
                return

            # Outlook utilise ";" comme séparateur pour les adresses
            to_str = ";".join(participants)

            subject = f"📅 Invitation: {title}"
            body = (
                f"Hello Team,\r\n\r\n"
                f"You are invited to the meeting \"{title}\":\r\n\r\n"
                f"📅 Date: {start_dt.strftime('%A, %d %B %Y')}\r\n"
                f"⏰ Time: {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}\r\n"
                f"🔗 Link: {meet_link}\r\n\r\n"
                f"{description}\r\n\r\n"
                "Best regards,\r\n"
            )

            # Encodage URL
            import urllib.parse
            to_encoded = urllib.parse.quote(to_str)
            subject_encoded = urllib.parse.quote(subject)
            body_encoded = urllib.parse.quote(body)

            # Pour compte pro → outlook.office.com
            outlook_url = (
                f"https://outlook.live.com/mail/deeplink/compose"
                f"?to={to_encoded}"
                f"&subject={subject_encoded}"
                f"&body={body_encoded}"
            )

            # Ouvre le draft dans Outlook Web
            import webbrowser
            webbrowser.open_new_tab(outlook_url)

            QMessageBox.information(self, "Succès", "Draft Outlook ouvert avec les détails de la réunion.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Outlook draft:\n{str(e)}")


    # Dans MainWindow, à la place de load_google_events originale

    def load_google_events(self):
        """Compatibilité : charge les événements depuis Microsoft Graph au lieu de Google"""
        token = get_access_token()
        self.events = get_upcoming_events(token, max_results=10)
        self.event_combo.clear()
        self.participants_list.clear()

        if not self.events:
            self.event_combo.addItem("No upcoming events found")
            return

        for ev in self.events:
            self.event_combo.addItem(ev['summary'])

        self.on_event_selected(0)


    def on_event_selected(self, index):
        if not self.events or index < 0 or index >= len(self.events):
            return
            
        self.current_event = self.events[index]
        event = self.current_event

        # Gestion de la date/heure
        dt = datetime.datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
        self.datetime_picker.setDateTime(QDateTime(dt))

        # Affichage des infos de base
        self.event_summary_label.setText(f"📌 {event['summary']}")
        self.event_description_label.setText(f"📝 {event.get('description', 'No description')}")
        self.event_link_label.hide()

        # Détection automatique du type de réunion
        title = event['summary'].lower()
        if "tech" in title:
            self.meeting_type_combo.setCurrentText("Technical")
        elif "hr" in title:
            self.meeting_type_combo.setCurrentText("HR")
        elif "client" in title:
            self.meeting_type_combo.setCurrentText("Client")
        else:
            self.meeting_type_combo.setCurrentText("Other")

        # Gestion des participants
        self.participants = []
        self.participants_list.clear()
        for email in event.get('attendees', []):
            self.participants.append((email, "Other"))
            item = QListWidgetItem(f"✉️ {email}")
            item.setData(Qt.UserRole, email)
            self.participants_list.addItem(item)

        # Lien visio
        meet_link = self._extract_meeting_link(event)
        if meet_link:
            self.meet_link_button.show()
            self.current_meet_link = meet_link
            self._configure_meet_button(meet_link)
        else:
            self.meet_link_button.hide()
            self.current_meet_link = None

    def _extract_meeting_link(self, event):
        """Extrait le lien de meeting depuis l'événement Microsoft"""

        online_meeting = event.get("onlineMeeting")
        if online_meeting and online_meeting.get("joinUrl"):
            return online_meeting.get("joinUrl")

        # Si pas de lien Teams, retourner lien web classique
        if event.get("link"):
            return event.get("link")

        # Pas de lien trouvé
        return ""



    def _configure_meet_button(self, meet_link):
        """Configure le bouton de meeting selon le type de lien"""
        button_style = f"""
            QPushButton {{
                background-color: {self.secondary_color};
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
                font-family: 'Roboto Medium';
            }}
            QPushButton:hover {{
                background-color: {self.primary_color};
            }}
        """
        
        if 'zoom.us' in meet_link:
            self.meet_link_button.setText("🎥 Join Zoom")
            self.meet_link_button.setStyleSheet(button_style.replace(self.secondary_color, "#2D8CFF"))
        elif 'teams.microsoft.com' in meet_link:
            self.meet_link_button.setText("🎥 Join Teams")
            self.meet_link_button.setStyleSheet(button_style.replace(self.secondary_color, "#6264A7"))
        else:
            self.meet_link_button.setText("🎥 Join Meet")
            self.meet_link_button.setStyleSheet(button_style)
    def show_note_interface(self):
        self.current_meeting_type = self.meeting_type_combo.currentText()
        self.current_datetime = self.datetime_picker.dateTime()
        self.clear_layout(self.layout)

        # ==== HEADER ====
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_frame.setStyleSheet(f"""
            QFrame#HeaderFrame {{
                background-color: {self.card_bg};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        header_layout = QHBoxLayout()
        header_frame.setLayout(header_layout)

        back_button = QPushButton("← Back to Home")
        back_button.setFixedWidth(150)
        back_button.setObjectName("SecondaryButton")
        back_button.clicked.connect(self.reset_to_home)

        meeting_title = QLabel(f"📝 {self.current_meeting_type} Meeting Notes")
        meeting_title.setObjectName("TitleLabel")
        meeting_title.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(back_button)
        header_layout.addStretch()
        header_layout.addWidget(meeting_title)
        header_layout.addStretch()
        self.layout.addWidget(header_frame)

        # ==== NOTES CONTAINER ====
        notes_container = QWidget()
        notes_layout = QHBoxLayout()
        notes_container.setLayout(notes_layout)
        notes_layout.setSpacing(20)

        self.note_inputs = {}

        for label, emoji, color in self.note_types:
            group = QGroupBox(f"{emoji} {label}")
            group.setStyleSheet(f"""
                QGroupBox {{
                    border: 2px solid {color};
                    border-radius: 12px;
                    margin-top: 20px;
                }}
                QGroupBox::title {{
                    color: {color};
                    font-family: 'Roboto Medium';
                    font-size: 16px;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px;
                }}
            """)

            vbox = QVBoxLayout()
            vbox.setSpacing(12)

            note_input = QTextEdit()
            note_input.setPlaceholderText(f"Write {label.lower()} points here...")
            note_input.setStyleSheet(f"""
                QTextEdit {{
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    min-height: 300px;
                    font-size: 14px;
                    padding: 12px;
                }}
                QTextEdit:focus {{
                    border: 2px solid {color};
                }}
            """)
            note_input.installEventFilter(self)

            vbox.addWidget(note_input)
            self.note_inputs[label] = note_input
            
            group.setLayout(vbox)
            notes_layout.addWidget(group)

        self.layout.addWidget(notes_container)

        # ==== BUTTONS ====
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout()
        buttons_frame.setLayout(buttons_layout)
        buttons_layout.setSpacing(20)

        save_btn = QPushButton("💾 Save Notes")
        save_btn.setFixedHeight(50)
        save_btn.setFont(QFont("Roboto Medium", 12))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                font-weight: 500;
                border-radius: 8px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {self.secondary_color};
            }}
        """)
        save_btn.clicked.connect(self.save_notes_to_db)

        generate_btn = QPushButton("🚀 Generate Minutes of Meeting")
        generate_btn.setFixedHeight(50)
        generate_btn.setFont(QFont("Roboto Medium", 12))
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.highlight_color};
                color: white;
                font-weight: 500;
                border-radius: 8px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: #d90429;
            }}
        """)
        generate_btn.clicked.connect(self.generate_mom)

        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(generate_btn)
        buttons_layout.addStretch()
        self.layout.addWidget(buttons_frame)

        # Setup note inputs
        self.setup_note_inputs()

    def setup_note_inputs(self):
        for label, widget in self.note_inputs.items():
            widget.installEventFilter(self)
            widget.focusInEvent = self.make_focus_in_event(widget)
        
    def make_focus_in_event(self, widget):
        original_focus_in = widget.focusInEvent

        def new_focus_in(event):
            if widget.toPlainText().strip() == "":
                widget.setPlainText("• ")
                cursor = widget.textCursor()
                cursor.movePosition(cursor.End)
                widget.setTextCursor(cursor)
            original_focus_in(event)

        return new_focus_in
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and isinstance(obj, QTextEdit):
            note_type = None
            for label, widget in self.note_inputs.items():
                if widget is obj:
                    note_type = label
                    break

            if note_type is None:
                return False

            labels = list(self.note_inputs.keys())
            idx = labels.index(note_type)

            if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
                cursor = obj.textCursor()
                cursor.movePosition(cursor.End)
                obj.setTextCursor(cursor)

                text = obj.toPlainText().strip()
                if text == "":
                    obj.insertPlainText("• ")
                else:
                    obj.insertPlainText("\n• ")

                return True

            if event.key() == Qt.Key_Right:
                next_idx = (idx + 1) % len(labels)
                self.note_inputs[labels[next_idx]].setFocus()
                return True

            if event.key() == Qt.Key_Left:
                prev_idx = (idx - 1) % len(labels)
                self.note_inputs[labels[prev_idx]].setFocus()
                return True

        return super().eventFilter(obj, event)

    def reset_to_home(self):
        self.setup_ui()
        self.load_google_events()

    def add_note_from_type(self, note_type):
        if note_type not in self.note_inputs:
            return
        note_input = self.note_inputs[note_type]
        cursor = note_input.textCursor()
        cursor.movePosition(cursor.End)
        note_input.setTextCursor(cursor)
        note_input.insertPlainText("\n")