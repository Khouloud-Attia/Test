import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, 
                            QGroupBox, QDateEdit, QTimeEdit, QListWidget, QTabWidget, QCheckBox)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont, QIcon

class ModernMeetingNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Meeting Minutes")
        self.setWindowIcon(QIcon('meeting_icon.png'))  # Remplacez par votre icône
        self.setGeometry(100, 100, 1000, 700)
        
        # Style moderne amélioré
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #495057;
            }
            QPushButton {
                background-color: #4e73df;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2e59d9;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QTextEdit, QLineEdit, QListWidget {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLabel {
                font-weight: bold;
                margin-bottom: 5px;
                color: #495057;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QTabBar::tab {
                padding: 8px 16px;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #4e73df;
            }
        """)
        
        # Widget central avec onglets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Onglet de saisie
        self.input_tab = QWidget()
        self.tabs.addTab(self.input_tab, "📝 Saisie des notes")
        self.create_input_tab()
        
        # Onglet de résultat
        self.output_tab = QWidget()
        self.tabs.addTab(self.output_tab, "📄 Compte-rendu")
        self.create_output_tab()
    
    def create_input_tab(self):
        """Crée l'onglet de saisie avec une interface moderne"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        self.input_tab.setLayout(layout)
        
        # Section informations de base
        info_group = QGroupBox("Informations de la réunion")
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)
        
        left_col = QVBoxLayout()
        left_col.setSpacing(5)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Ex: Revue du projet X")
        left_col.addWidget(QLabel("Titre de la réunion:"))
        left_col.addWidget(self.title_edit)
        
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        left_col.addWidget(QLabel("Date:"))
        left_col.addWidget(self.date_edit)
        
        mid_col = QVBoxLayout()
        mid_col.setSpacing(5)
        self.start_time = QTimeEdit(QTime.currentTime())
        mid_col.addWidget(QLabel("Heure de début:"))
        mid_col.addWidget(self.start_time)
        
        self.end_time = QTimeEdit(QTime.currentTime().addSecs(3600))
        mid_col.addWidget(QLabel("Heure de fin:"))
        mid_col.addWidget(self.end_time)
        
        right_col = QVBoxLayout()
        right_col.setSpacing(5)
        self.participants_list = QListWidget()
        self.participant_edit = QLineEdit()
        self.participant_edit.setPlaceholderText("Nom du participant")
        self.add_participant_btn = QPushButton("Ajouter")
        self.add_participant_btn.clicked.connect(self.add_participant)
        
        participant_controls = QHBoxLayout()
        participant_controls.addWidget(self.participant_edit)
        participant_controls.addWidget(self.add_participant_btn)
        
        right_col.addWidget(QLabel("Participants:"))
        right_col.addLayout(participant_controls)
        right_col.addWidget(self.participants_list)
        
        info_layout.addLayout(left_col, 40)
        info_layout.addLayout(mid_col, 20)
        info_layout.addLayout(right_col, 40)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Section ordre du jour
        agenda_group = QGroupBox("Ordre du jour")
        agenda_layout = QVBoxLayout()
        self.agenda_edit = QTextEdit()
        self.agenda_edit.setPlaceholderText("Listez les points à aborder dans la réunion...")
        agenda_layout.addWidget(self.agenda_edit)
        agenda_group.setLayout(agenda_layout)
        layout.addWidget(agenda_group)
        
        # Section notes avec onglets
        notes_tabs = QTabWidget()
        
        # Points discutés
        points_tab = QWidget()
        self.points_edit = QTextEdit()
        self.points_edit.setPlaceholderText("Notes sur les points discutés...")
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(self.points_edit)
        points_tab.setLayout(tab_layout)
        notes_tabs.addTab(points_tab, "Points discutés")
        
        # Décisions
        decisions_tab = QWidget()
        self.decisions_edit = QTextEdit()
        self.decisions_edit.setPlaceholderText("Décisions prises pendant la réunion...")
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(self.decisions_edit)
        decisions_tab.setLayout(tab_layout)
        notes_tabs.addTab(decisions_tab, "Décisions")
        
        # Actions
        actions_tab = QWidget()
        self.actions_edit = QTextEdit()
        self.actions_edit.setPlaceholderText("Actions à suivre (qui, quoi, quand)...")
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(self.actions_edit)
        actions_tab.setLayout(tab_layout)
        notes_tabs.addTab(actions_tab, "Actions")
        
        layout.addWidget(notes_tabs)
        
        # Bouton de génération
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.generate_btn = QPushButton("Générer le compte-rendu")
        self.generate_btn.clicked.connect(self.generate_mom)
        btn_layout.addWidget(self.generate_btn)
        layout.addLayout(btn_layout)
    
    def create_output_tab(self):
        """Crée l'onglet de résultat"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        self.output_tab.setLayout(layout)
        
        # Options de format
        format_group = QGroupBox("Options de formatage")
        format_layout = QHBoxLayout()
        format_layout.setSpacing(20)
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Standard", "Formel", "Technique", "Minimaliste"])
        format_layout.addWidget(QLabel("Modèle:"), 1)
        format_layout.addWidget(self.template_combo, 3)
        
        self.ai_checkbox = QCheckBox("Utiliser l'IA pour améliorer")
        format_layout.addWidget(self.ai_checkbox, 2)
        
        self.email_checkbox = QCheckBox("Format pour email")
        format_layout.addWidget(self.email_checkbox, 2)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Résultat
        self.result_edit = QTextEdit()
        self.result_edit.setFont(QFont("Arial", 11))
        layout.addWidget(self.result_edit)
        
        # Boutons d'action
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        self.copy_btn = QPushButton("Copier")
        self.copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
        
        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setIcon(QIcon.fromTheme("document-save"))
        
        self.email_btn = QPushButton("Envoyer par email")
        self.email_btn.setIcon(QIcon.fromTheme("mail-send"))
        
        action_layout.addWidget(self.copy_btn)
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.email_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
    
    def add_participant(self):
        """Ajoute un participant à la liste"""
        participant = self.participant_edit.text().strip()
        if participant:
            self.participants_list.addItem(participant)
            self.participant_edit.clear()
    
    def generate_mom(self):
        """Génère le compte-rendu"""
        # Récupère les données
        participants = []
        for i in range(self.participants_list.count()):
            participants.append(self.participants_list.item(i).text())
        
        data = {
            'title': self.title_edit.text(),
            'date': self.date_edit.date().toString("dd/MM/yyyy"),
            'start_time': self.start_time.time().toString("hh:mm"),
            'end_time': self.end_time.time().toString("hh:mm"),
            'participants': ", ".join(participants),
            'agenda': self.agenda_edit.toPlainText(),
            'discussion_points': self.points_edit.toPlainText(),
            'decisions': self.decisions_edit.toPlainText(),
            'action_items': self.actions_edit.toPlainText()
        }
        
        # Génère le compte-rendu
        if self.ai_checkbox.isChecked():
            mom_text = self.generate_with_ai(data)
        else:
            mom_text = self.generate_basic_mom(data)
        
        # Affiche le résultat
        self.result_edit.setHtml(mom_text)
        self.tabs.setCurrentIndex(1)  # Passe à l'onglet résultat
    
    def generate_basic_mom(self, data):
        """Génère un compte-rendu basique formaté en HTML"""
        # On remplace d'abord les sauts de ligne
        agenda = data['agenda'].replace('\n', '<br>')
        points = data['discussion_points'].replace('\n', '<br>')
        decisions = data['decisions'].replace('\n', '<br>')
        actions = data['action_items'].replace('\n', '<br>')
        
        return f"""
        <h2 style='color:#2c3e50;'>COMPTE-RENDU DE RÉUNION</h2>
        <h3>{data['title']}</h3>
        <p><strong>Date:</strong> {data['date']} | <strong>Heure:</strong> {data['start_time']} - {data['end_time']}</p>
        
        <h4 style='color:#3498db;'>Participants:</h4>
        <ul><li>{data['participants'].replace(',', '</li><li>')}</li></ul>
        
        <h4 style='color:#3498db;'>Ordre du jour:</h4>
        <p>{agenda}</p>
        
        <h4 style='color:#3498db;'>Points discutés:</h4>
        <p>{points}</p>
        
        <h4 style='color:#3498db;'>Décisions prises:</h4>
        <p>{decisions}</p>
        
        <h4 style='color:#3498db;'>Actions à suivre:</h4>
        <p>{actions}</p>
        """
    
    def generate_with_ai(self, data):
        """Version avec génération AI (optionnelle)"""
        try:
            # Note: Vous devez installer openai et configurer votre clé API
            import openai
            openai.api_key = "votre-clé-api-openai"  # Remplacez par votre clé
            
            prompt = f"""
            Génère un compte-rendu de réunion professionnel en français à partir des informations suivantes:
            
            Titre: {data['title']}
            Date: {data['date']} de {data['start_time']} à {data['end_time']}
            Participants: {data['participants']}
            
            Ordre du jour:
            {data['agenda']}
            
            Points discutés:
            {data['discussion_points']}
            
            Décisions:
            {data['decisions']}
            
            Actions:
            {data['action_items']}
            
            Structure le compte-rendu de manière professionnelle avec des sections claires.
            Utilise un style {self.template_combo.currentText().lower()}.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui génère des comptes-rendus de réunion professionnels en français."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message['content']
        except Exception as e:
            return f"<p style='color:red;'>Erreur lors de la génération AI: {str(e)}</p>"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Style moderne
    window = ModernMeetingNotesApp()
    window.show()
    sys.exit(app.exec_())