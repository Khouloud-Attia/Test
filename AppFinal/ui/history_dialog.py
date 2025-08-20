from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QTextEdit, QLabel, QHBoxLayout,
    QGroupBox, QListWidgetItem, QScrollArea, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sqlite3

import os

def get_user_db_path():
    """Retourne le chemin de la base de données pour l'utilisateur courant"""
    appdata = os.getenv('APPDATA') or os.path.expanduser("~/.config")
    db_dir = os.path.join(appdata, "MeetNotesAI")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "meeting_notes.db")


class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        
        super().__init__(parent)
        self.setWindowTitle("📜 Meeting History")
        self.setMinimumSize(1000, 600)
        self.DB_PATH = get_user_db_path()
        self.conn = sqlite3.connect(self.DB_PATH)

        # Layout principal horizontal
        main_layout = QHBoxLayout(self)

        # Colonne gauche : liste + bouton
        left_layout = QVBoxLayout()
        
        self.meeting_list = QListWidget()
        self.meeting_list.setFixedWidth(300)
        self.meeting_list.itemClicked.connect(self.display_meeting_details)
        
        # Bouton supprimer
        self.delete_button = QPushButton("🗑️ Supprimer")
        self.delete_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.delete_button.clicked.connect(self.delete_selected_meeting)

        left_layout.addWidget(self.meeting_list)
        left_layout.addWidget(self.delete_button)

        # Zone détails
        self.details_area = QTextEdit()
        self.details_area.setReadOnly(True)
        self.details_area.setFont(QFont("Arial", 11))

        # Ajouter au layout principal
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.details_area)

        # Charger les réunions
        self.load_meetings()

    def load_meetings(self):
        self.meeting_list.clear()
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, type, datetime FROM meetings ORDER BY created_at DESC")
        meetings = cursor.fetchall()
        for meeting in meetings:
            item = QListWidgetItem(f"{meeting[1]} ({meeting[2]})\n{meeting[3]}")
            item.setData(Qt.UserRole, meeting[0])  # store meeting_id
            self.meeting_list.addItem(item)

    def display_meeting_details(self, item):
        meeting_id = item.data(Qt.UserRole)
        cursor = self.conn.cursor()

        cursor.execute("SELECT title, type, datetime, participants, mom_content FROM meetings WHERE id = ?", (meeting_id,))
        meeting = cursor.fetchone()

        cursor.execute("SELECT note_type, content FROM notes WHERE meeting_id = ?", (meeting_id,))
        notes = cursor.fetchall()

        if not meeting:
            self.details_area.setText("No details found.")
            return

        title, mtype, datetime_str, participants, mom = meeting

        # Regrouper les notes par type
        decisions, actions, discussions = [], [], []

        for note_type, content in notes:
            if note_type.lower() == "decision":
                decisions.append(content.strip())
            elif note_type.lower() == "action":
                actions.append(content.strip())
            elif note_type.lower() == "discussion":
                discussions.append(content.strip())

        # Construire l'affichage
        details = f"""<b>📝 Title:</b> {title}<br>
<b>📁 Type:</b> {mtype}<br>
<b>🕒 Date/Time:</b> {datetime_str}<br><br>
<b>👥 Participants:</b><br>
{participants.replace(', ', '<br>')}<br><br>
"""

        if decisions:
            details += "<b>🗒️ Decisions:</b><br>" + "".join(f"• {d}<br>" for d in decisions) + "<br>"
        if actions:
            details += "<b>✅ Actions:</b><br>" + "".join(f"• {a}<br>" for a in actions) + "<br>"
        if discussions:
            details += "<b>💬 Discussions:</b><br>" + "".join(f"• {disc}<br>" for disc in discussions) + "<br>"

        details += f"<b>📄 Minutes of Meeting:</b><br>{mom}" if mom else "<i>No MoM recorded.</i>"

        self.details_area.setHtml(details)

    def delete_selected_meeting(self):
        selected_item = self.meeting_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Suppression", "Veuillez sélectionner une réunion à supprimer.")
            return

        meeting_id = selected_item.data(Qt.UserRole)

        # Demander confirmation
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            "Confirm deletion !",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM notes WHERE meeting_id = ?", (meeting_id,))
            cursor.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
            self.conn.commit()

            # Actualiser la liste
            self.load_meetings()
            self.details_area.clear()
