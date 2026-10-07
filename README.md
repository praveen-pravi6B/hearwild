# HearWild 🌿

> **Listen to the world. Discover what lives in it.**

HearWild is an open-source, offline-first AI nature companion that helps you identify birds by sound, build your personal flock, and get back outside.

It uses **BirdNET V3 ONNX** to identify bird sounds locally through a simple web interface.

The idea is simple:

**Listen → Discover → Learn → Go outside.**

---

## 🌿 Why HearWild?

AI should help you discover something outside — then get out of your way.

HearWild is designed around short interactions:

1. Record a bird sound for about 6 seconds.
2. Let local AI identify the bird.
3. Learn a little about what you heard.
4. Add confidently identified birds to your personal flock.
5. Earn XP as you discover more birds.
6. Put your phone away and keep exploring.

There are no accounts, feeds, maps, or endless scrolling.

---

## ✨ Features

### 🎙️ Identify birds by sound

Record a short bird sound directly from your browser.

The recording is sent to the local FastAPI backend, converted to WAV with FFmpeg, and analyzed using BirdNET V3 ONNX.

### 🧠 Local open-weight AI

Bird identification is powered by:

**BirdNET V3 ONNX**

The model runs locally through the backend rather than relying on a cloud AI service.

### 🐦 My Flock

Confidently identified birds are automatically added to your personal flock.

Each bird keeps track of:

- Bird name
- Scientific name
- Real bird image
- XP
- Number of times identified
- First seen time
- Last seen time

### ⭐ XP and levels

Discovering birds gives you XP.

| Discovery | XP |
|---|---:|
| New bird | +100 XP |
| Known bird | +25 XP |

Your flock level increases as your total XP grows.

### 🎯 Confidence-aware identification

HearWild does not treat every prediction as certain.

| Confidence | Result |
|---|---|
| **≥ 70%** | Confident identification → added to flock + XP |
| **20–69%** | Possible identification → no XP |
| **< 20%** | Unknown / unclear → no XP |

This keeps the collection focused on meaningful discoveries.

### 🌿 Keep Exploring

After an identification, HearWild briefly shows the result or reward and then encourages you to continue exploring.

The goal is not to keep you on the website.

The goal is to get you back outside.

---

## 🏗️ Architecture

```text
┌──────────────────────────────┐
│       Vue 3 Web App          │
│                              │
│  🎙️ Record bird sound        │
│  🐦 Identification result    │
│  ⭐ XP / reward               │
│  🌿 My Flock                  │
└──────────────┬───────────────┘
               │
               │ HTTP
               ▼
┌──────────────────────────────┐
│       FastAPI Backend        │
│                              │
│  Audio upload                │
│  FFmpeg conversion           │
│  BirdNET inference           │
│  Confidence handling         │
│  Flock / XP management       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       BirdNET V3 ONNX        │
│                              │
│  Bird sound identification   │
│  Species + confidence        │
└──────────────────────────────┘

               │
               ▼

┌──────────────────────────────┐
│           SQLite             │
│                              │
│  Personal flock              │
│  XP                          │
│  Discovery history           │
│  Bird image URLs             │
└──────────────────────────────┘
```

---

## 🧰 Tech Stack

### Frontend

- Vue 3
- Vite
- JavaScript
- Browser MediaRecorder API
- CSS

### Backend

- Python
- FastAPI
- FFmpeg
- SQLite
- HTTPX

### AI

- BirdNET V3
- ONNX

### Bird images

Bird images are retrieved from **Wikimedia Commons** and persisted in the local SQLite database.

---

## 📁 Project Structure

```text
hearwild/
├── backend/
│   ├── main.py
│   └── database.py
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── BrandHeader.vue
│       │   ├── RecordButton.vue
│       │   ├── RecordingStatus.vue
│       │   └── BirdResult.vue
│       ├── views/
│       │   └── FlockView.vue
│       ├── services/
│       │   └── birdApi.js
│       ├── App.vue
│       ├── main.js
│       └── style.css
│
├── test_birdnet.py
├── sample.mp3
├── bird_test.ogg
├── bird_test_1.ogg
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd hearwild
```

### 2. Create the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install fastapi uvicorn python-multipart httpx birdnet
```

Make sure FFmpeg is installed on your system.

On macOS with Homebrew:

```bash
brew install ffmpeg
```

### 4. Start the backend

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 5. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will provide the local development URL.

Open it in your browser and allow microphone access.

---

## 🔌 API

### Health check

```http
GET /health
```

Example:

```json
{
  "status": "ok"
}
```

### Identify a bird

```http
POST /identify
```

Send a browser-recorded audio file as multipart form data.

Example response:

```json
{
  "species": "House Sparrow",
  "scientific_name": "Passer domesticus",
  "confidence": 0.819,
  "added_to_flock": true,
  "xp_earned": 100
}
```

### Get flock

```http
GET /flock
```

Returns the user's current flock, XP, level, discovery count, and persisted bird images.

---

## 🧠 Bird Identification Flow

```text
Browser
   │
   │ 6-second recording
   ▼
MediaRecorder
   │
   │ WebM / Opus
   ▼
FastAPI
   │
   │ FFmpeg
   ▼
WAV audio
   │
   ▼
BirdNET V3 ONNX
   │
   ├── Species
   └── Confidence
        │
        ▼
Confidence handling
        │
        ├── ≥ 70%
        │      └── Add to flock + XP
        │
        ├── 20–69%
        │      └── Show possible result
        │
        └── < 20%
               └── Treat as unknown
```

---

## 🐦 Flock Progression

A new discovery:

```text
✨ ADDED TO YOUR FLOCK

🐦 House Sparrow

⭐ +100 XP

LEVEL 1
████░░░░░░
```

A repeat discovery:

```text
🐦 HOUSE SPARROW

Already in your flock

⭐ +25 XP

LEVEL 3
████████░░
```

The collection is intentionally simple.

It is meant to give you a reason to keep listening outside, not another reason to stay on a screen.

---

## 🌍 Real Bird Images

When a bird is confidently identified, HearWild looks up an appropriate image from Wikimedia Commons.

The image URL is stored in SQLite so that the flock can continue displaying the image without repeatedly requesting it.

Existing flock entries can also be backfilled with missing images when the flock endpoint is requested.

---

## 🔒 Privacy & Offline-first Design

HearWild is designed around local processing.

The core bird identification pipeline is:

```text
Microphone
    ↓
Local browser
    ↓
Local FastAPI server
    ↓
Local BirdNET model
    ↓
SQLite
```

There is no user account or authentication system.

No personal profile is required.

The core AI identification does not depend on a cloud AI inference API.

---

## 🎯 Hacktoberfest: Touch Grass

HearWild was built for the **Hacktoberfest 2026 Open-Source AI Challenge Week 1**.

The challenge:

> Build something with open-source AI at its core that encourages people to get off the screen and into the world.

Many AI applications try to keep people engaged with a screen.

HearWild takes the opposite approach.

It uses AI for one small interaction:

**Listen to the world.**

Then:

**Put the phone away.**

The product is intentionally designed so that the AI interaction is short and the real experience happens outside.

---

## 🛣️ Future Ideas

Possible future improvements include:

- Better outdoor recording validation
- More detailed bird information
- Improved audio preprocessing
- Additional nature sound categories
- Better identification history
- More lightweight offline packaging

The MVP intentionally avoids adding unnecessary features such as:

- User accounts
- Social feeds
- Maps
- GPS tracking
- Weather integrations
- Native mobile applications
- AI agents

The focus is the core loop:

**Listen → Identify → Discover → Go outside.**

---

## 🤝 Contributing

HearWild is open source and contributions are welcome.

Potential contribution areas:

- UI improvements
- Accessibility
- Bird information
- Audio processing
- BirdNET integration
- Testing
- Documentation
- Performance improvements

Please keep contributions aligned with the project's goal of helping people spend more time outside.

---

## 📄 License

This project is open source.

Check the repository for the current license and the licenses of the third-party models and datasets used by the project.

BirdNET and Wikimedia Commons content remain subject to their respective licenses and terms.

---

## 🌿 HearWild

**Listen to the world. Discover what lives in it.**

AI should help you discover something outside — then get out of your way.
