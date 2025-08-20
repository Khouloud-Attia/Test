# 📘 MeetNotesAI

MeetNotesAI is a modern desktop application built with **PyQt5** to simplify note-taking during meetings.  
It integrates **AI models (via Ollama and Docker)** to automatically generate clear and structured **Minutes of Meeting (MoM)** from your notes.

---

## ✨ Features

- 📝 **Live note-taking** with dedicated fields (Decisions, Actions, Discussions).  
- 🤖 **AI-powered MoM generation** using local models (TinyLlama, Phi-3, etc.) through Ollama.  
- 💾 **Save meetings and notes** into a local SQLite database.  
- 📅 **Schedule meetings** with Outlook integration.  
- 📤 **Send MoM via email** using Microsoft Graph API (Outlook).  
- 🎨 **Modern UI** with light/dark themes, animations, and smooth navigation.  

---

## 🛠 Tech Stack

- **Language:** Python 3.10+  
- **UI Framework:** PyQt5  
- **Database:** SQLite  
- **AI Models:** Phi-3 / Mistral via Ollama  
- **APIs:** Microsoft Graph API  
- **Dependency Management:** pip  

---

## 🚀 Installation & Usage

### 1. Install Ollama  
Download and install Ollama from:  
👉 [https://ollama.com/download](https://ollama.com/download)

### 2. Install Required AI Models  
After installing Ollama, open a terminal and run:  
```bash
ollama pull mistral
# or
ollama pull phi3
