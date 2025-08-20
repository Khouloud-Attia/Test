# 📘 MeetNotesAI  

MeetNotesAI is a modern desktop application built with **PyQt5** to simplify note-taking during meetings.  
It integrates **AI models (via Ollama and Docker)** to automatically generate clear and structured **Minutes of Meeting (MoM)** from your notes.  

---

## ✨ Features  

- 📝 Live note-taking with dedicated fields (Decisions, Actions, Discussions).  
- 🤖 AI-powered MoM generation using local models (TinyLlama, Phi-3, etc.) through Ollama (Dockerized).  
- 💾 Save meetings and notes into a local **SQLite database**.  
- 📅 Schedule meetings with **Outlook integration**.  
- 📤 Send MoM via email using **Microsoft Graph API (Outlook)**.  
- 🎨 Modern UI with light/dark themes, animations, and smooth navigation.  

---

## 🛠️ Tech Stack  

- **Language**: Python 3.10+  
- **UI Framework**: PyQt5  
- **Database**: SQLite  
- **AI**: Phi-3 / Mistral via Ollama (Dockerized)  
- **APIs**: Microsoft Graph API  
- **Dependency Management**: pip  

---

## 🚀 Running (Docker + App)  

### 1. Install Docker Desktop  
Download and install **Docker Desktop** from:  
👉 [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)  

Make sure Docker Desktop is running before continuing.  

### 2. Load or Build the Docker Image  
- **Load a prebuilt image** (if provided as `meetnotes_ollama.tar`):  
```bash
docker load -i meetnotes_ollama.tar
