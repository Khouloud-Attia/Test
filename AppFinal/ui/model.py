import json
from PyQt5.QtCore import QThread, QObject, pyqtSignal,QSize

from PyQt5.QtWidgets import (
   QVBoxLayout, QTextEdit, QPushButton, 
    QAction, QLabel,  QDialog
    
)

from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtCore import Qt, QSize
import subprocess

import requests

class MomWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, prompt, parent=None):
        super().__init__()
        self.prompt = prompt
        self.parent = parent

    def run(self):
        try:
            mom_text = self.parent.generate_mom_with_ollama(self.prompt)
            self.finished.emit(mom_text)
        except Exception as e:
            self.error.emit(str(e))

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)  # Pas de bordure
        self.setModal(True)
        self.resize(100, 50)
        self.setStyleSheet("""
            background-color: #0a192f	;
            border-radius: 15px;
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # GIF
        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignCenter)
        movie = QMovie("C:/Users/khoul/OneDrive/Desktop/App/MeetNotesApp/ui/loading.gif")
        movie.setScaledSize(QSize(60, 60))  
        gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(gif_label)

        # Texte
        text_label = QLabel("Generating Minutes of Meeting...\nPlease wait")
        text_label.setFont(QFont("Segoe UI", 10))
        text_label.setStyleSheet("color: white;")
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)



class model ():
    def generate_mom_with_ollama(self, prompt_text):
        try:
            result = subprocess.run(
                ["ollama", "run", "mistral"],
                input=prompt_text,
                capture_output=True,
                text=True,
                encoding="utf-8", 
                check=True
                )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Ollama Error: {e}")
            return "Error generating MoM."
   
        
    def clean_notes(self,text):
    # Supprime les puces "• " et espaces inutiles
        return "\n".join(line.lstrip("• ").strip() for line in text.splitlines() if line.strip())

    def generate_mom(self):
        # Initialisation de mom_raw
        mom_raw = f"Meeting Type: {self.current_meeting_type}\n"
        mom_raw += f"Date & Time: {self.current_datetime.toString()}\n"

    # Participants
        mom_raw += "Participants:\n"
        for name, role in self.participants:
            mom_raw += f"- {name} ({role})\n"

    # Notes nettoyées
        for label, _, _ in self.note_types:
            raw_text = self.note_inputs[label].toPlainText()
            cleaned_text = self.clean_notes(raw_text)
            if cleaned_text:
                mom_raw += f"\n{label}:\n{cleaned_text}\n"

    # Prompt strict
        prompt = f"""
You are a professional meeting documentation specialist.
The provided meeting notes are technical keywords, abbreviations, and short phrases.
Your task is to produce a **clear, professional, and well-structured Minutes of Meeting (MoM)**
that can be easily understood by recipients who were not present at the meeting.

Important rules:
- Interpret abbreviations and expand them when possible .
- Convert fragmented technical notes into clear, complete, and concise sentences.
- Preserve the technical meaning but make it understandable for a broader audience.
- Do NOT merge content between sections.
- Avoid redundancy — each point should appear in only one section.

Raw meeting notes:
{mom_raw}

Generate the MoM in the following structured format:

1. **Meeting Overview**
   - Meeting Type: [exactly as given]
   - Date & Time: [exactly as given]
   - Participants: [exactly as given, no actions or decisions here]

2. **Decisions Made**
   - Use ONLY the "Decision" notes
   - Reformulate short/technical notes into clear decision statements
   - Each bullet point should be one complete, concise decision

3. **Actions & Responsibilities**
   - Use ONLY the "Action" notes
   - Expand short/technical phrases into clear, actionable statements
   - If a responsible person is mentioned, clearly include them
     (e.g., "John - Prepare the final project report by Monday")

4. **Key Discussions**
   - Use ONLY the "Discussion" notes
   - Expand and clarify technical discussion points so they are understandable
   - Keep them concise and relevant

Formatting rules:
- Use bold section titles exactly as above
- Use "•" for all bullet points
- Write in a professional tone
- Keep sentences short, clear, and precise
"""


    # Lancer génération avec Ollama
        self.loading_dialog = LoadingDialog(self) # type: ignore
        self.thread = QThread()
        self.worker = MomWorker(prompt, self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_mom_generated)
        self.worker.error.connect(self.on_mom_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        self.loading_dialog.show()


    def on_mom_generated(self, mom_text):
        self.loading_dialog.close()
        self.generated_mom = mom_text

    # Afficher le résultat dans un QDialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Generated Minutes of Meeting")
        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit(dialog)
        text_edit.setReadOnly(True)
        text_edit.setPlainText(self.generated_mom)
        layout.addWidget(text_edit)
        
        btn_email = QPushButton("📧 Generate Email", dialog)
        btn_email.setFixedHeight(40)
        btn_email.setFont(QFont("Arial", 12))
        btn_email.setStyleSheet("""
                                QPushButton {
                                    background-color: #9f7aea;
                                    color: white;
                                    font-weight: bold;
                                    border-radius: 6px;
                                    }
                                    QPushButton:hover {
                                        background-color: #805ad5;
                                        }
                                        """)
        btn_email.clicked.connect(lambda: self.generate_email())
        layout.addWidget(btn_email)

       
        
        dialog.resize(600, 400)
        dialog.exec_()


    def on_mom_error(self, error_msg):
        self.loading_dialog.close()
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", f"Could not generate MoM:\n{error_msg}")
        
    