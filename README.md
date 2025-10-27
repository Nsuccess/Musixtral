# 🎵 OpenDAW — AI-Powered Digital Audio Workstation for Everyone  

<p align="center">
  <img src="https://raw.githubusercontent.com/andremichelle/openDAW/refs/heads/main/packages/app/studio/public/favicon.svg" height="100"/>
  <h3 align="center">Bringing Music Creation to Everyone, Everywhere 🎶</h3>
</p>

<p align="center">
  <a href="https://musixtral.vercel.app"><img src="https://img.shields.io/badge/Live%20Demo-OpenDAW-green?style=for-the-badge" alt="OpenDAW Demo"></a>
  <a href="https://musictoolkit.vercel.app"><img src="https://img.shields.io/badge/AI%20Music%20Tools-MusicToolkit-blue?style=for-the-badge" alt="MusicToolkit Demo"></a>
  <a href="https://youthcoders.org"><img src="https://img.shields.io/badge/Hackathon-Youth%20Coders-orange?style=for-the-badge" alt="Youth Coders Hackathon"></a>
</p>

---

## 🌍 Project Overview  

**OpenDAW** (Open Digital Audio Workstation) empowers **young creators and independent artists** to make music using only their voice and a browser — no expensive hardware required.  

Built for the **Youth Coders Hackathon**, it aligns with the **Education Access** and **Equity & Accessibility** tracks by making **music production, composition, and learning tools** accessible to everyone, especially in regions with limited access to studios or instruments.

---

## 🚀 Core Features  

### 🎤 AI Humming-to-Music  
Hum a tune → get a full AI-generated track with drums, harmony, and instruments using **MusicGen**.

### 🎼 Audio-to-Music Score  
Upload a `.wav` file → automatically convert it into readable **MusicXML** notation and view an SVG sheet.

### 🎚️ Cloud-based DAW  
Work with multiple audio tracks, apply effects, and manage sessions in the browser.

### ☁️ Vercel-Powered Collaboration  
No setup required — everything runs on **Vercel’s serverless infrastructure**.

---

## 🧠 Why It Matters  

> “A world where anyone — with or without an instrument — can create and share music.”  

- 🎧 **Inclusive Creativity** — removes barriers for students and creators without hardware  
- 🧑🏽‍🏫 **Music Learning Aid** — turns recorded lessons or humming into notation for education  
- 🫱🏾‍🫲🏼 **Community Empowerment** — helps youth express themselves creatively and share culturally relevant music  
- 🌐 **Accessible Everywhere** — runs entirely in the browser with no installation

---

## 🧩 Architecture  

```text
User (Browser)
↓
OpenDAW Web App (Vercel)
├── FastMCP Server (Music Processing)
│   ├── Audio-to-MIDI
│   ├── Humming-to-Music
│   └── MusicXML Generation
└── MusicToolkit Server (AI Composition)
    ├── MusicGen Integration
    └── Verovio Score Rendering
```

---

## 🛠️ Tech Stack  

| **Layer** | **Technology** |
|-----------|----------------|
| Frontend | React (Next.js on Vercel) |
| Backend | FastMCP (Python) |
| AI Models | MusicGen, basic-pitch, music21 |
| Deployment | Vercel (serverless) |
| Storage | Local / optional AWS S3 |
| Protocol | Model Context Protocol (MCP) |

---

## ⚙️ Quick Start  

### 1️⃣ Clone the repo

```bash
git clone https://github.com/Nsuccess/Musixtral.git
cd Musixtral
```

### 2️⃣ Run locally

```bash
# MusicToolkit
cd MusicToolkit
uv run python music_toolkit_server.py

# OpenDAW
cd ../OpenDAW
python fastmcp_server.py
```

### 3️⃣ Deploy to Vercel

```bash
vercel --prod
```

---

## 🧩 MCP Tools  

### 🎼 `wav_to_music_score` — Convert WAV to sheet music notation

```json
{
  "name": "wav_to_music_score",
  "arguments": {
    "wav_file_path": "/path/to/audio.wav",
    "render_svg": true
  }
}
```

### 🎵 `generate_music_from_humming` — Turn a humming clip into a complete song

```json
{
  "name": "generate_music_from_humming",
  "arguments": {
    "humming_file_path": "/path/to/humming.wav",
    "style_prompt": "lofi chill with piano and drums",
    "generate_score": true
  }
}
```

---

## 🌐 Live Deployment  

| **Component** | **URL** | **Endpoint** |
|---------------|---------|--------------|
| MusicToolkit | https://musictoolkit.vercel.app | `/mcp` |
| OpenDAW | https://musixtral.vercel.app | `/api/mcp` |

---

## 📖 Hackathon Track Fit  

| **Track** | **How OpenDAW Fits** |
|-----------|----------------------|
| 💻 Education Access | Enables students to learn music theory interactively. |
| ♿ Equity & Accessibility | Makes professional tools free and usable without instruments or studios. |
| 🌐 Community Engagement | Connects youth through shared music and creativity. |

---

## 💡 Future Improvements  

- Real-time AI feedback during composition  
- Collaborative multi-user DAW sessions  
- Local language lyric support (Krio, Swahili, etc.)  
- Integrated voice-based songwriting assistant

---

## 📜 License  

Licensed under **AGPLv3** — open for all to remix and build upon.
