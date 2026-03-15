# Termidock 🖥️

A browser based terminal emulator built as part of a hiring task. Users can launch an isolated Ubuntu Docker container directly from the browser, type commands, and see live output all in real time via WebSockets.

---

## Task Overview

> Build a Browser-Based Terminal App where the user opens the browser and clicks a **"Launch Lab"** button. A Docker container is created for that session. The user can type commands in the browser terminal, which run inside the container — just like Killercoda.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Terminal UI | [Xterm.js](https://xtermjs.org/) |
| Backend | Python, Django |
| Real-time | Django Channels (WebSocket) |
| Container | Docker (Ubuntu image) |
| Docker Integration | Docker SDK for Python |
| Server | ASGI via Daphne / Uvicorn |

---

## Project Structure

```
Terminal-project/
├── README.md
└── termidock/
    ├── manage.py                  # Django management script
    ├── requirements.txt           # Python dependencies
    ├── static/                    # Static files (CSS, JS, assets)
    ├── templates/
    │   └── index.html             # Main frontend — Launch Lab UI + Xterm.js terminal
    ├── lab/                       # Core Django app — terminal & Docker logic
    │   ├── __init__.py
    │   ├── consumers.py           # WebSocket consumer — bridges browser ↔ Docker container
    │   ├── routing.py             # WebSocket URL routing
    │   ├── urls.py                # HTTP URL patterns for the lab app
    │   └── views.py               # HTTP views — serves the frontend page
    └── terminal_lab/              # Django project configuration
        ├── __init__.py
        ├── asgi.py                # ASGI entry point — routes HTTP + WebSocket connections
        ├── settings.py            # Project settings (Channels, installed apps, etc.)
        └── urls.py                # Root URL configuration
```

---

## How It Works

```
Browser (Xterm.js)
      |
      |  WebSocket
      ↓
Django Channels (consumers.py)
      |
      |  Docker SDK for Python
      ↓
Ubuntu Docker Container
```

1. The user opens the app and sees the **Ubuntu Labs** page (`index.html`).
2. Clicking **Launch Lab** sends a request to the backend, which uses the Docker SDK to spin up a new Ubuntu container.
3. The browser opens a **WebSocket connection** handled by `lab/consumers.py`.
4. The consumer attaches to the container's shell (exec session), relaying input/output in real time.
5. Output from the container streams back to **Xterm.js** in the browser.
6. When the user clicks **End Lab** (or closes the tab), the consumer stops and removes the container automatically.

---

## Getting Started

### Prerequisites

- Python 3.12+
- Docker (running locally)
- pip

### Installation

```bash

# Clone the repository
git clone https://github.com/HashimN225/Terminal-Project.git
cd Terminal-Project/termidock

# Create and activate virtual environment
# Mac and Linux
python3 -m venv myvenv
source myvenv/bin/activate

# Windows
python -m venv myvenv
myvenv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Pull the Ubuntu Docker image (first time only)
docker pull ubuntu

# Run the development server
daphne -b 0.0.0.0 -p 8000 terminal_lab.asgi:application
Then open your browser and go to `http://localhost:8000`.

---

```

## Usage

1. Open `http://localhost:8000` in your browser.
2. Click **Launch Lab** — a Docker container starts and the terminal appears.
3. Type any Linux command (e.g., `ls`, `pwd`, `echo hello`) and hit Enter.
4. The command runs inside the container and output appears instantly.
5. Click **End Lab** to stop and remove the container.
6. *(Optional)* Click **Reset Lab** to restart with a fresh container.

---

## Requirements

See [`requirements.txt`](termidock/requirements.txt) for the full list of dependencies. Key packages include:

- `django` — Web framework
- `channels` — WebSocket support via ASGI
- `docker` — Docker SDK for Python
- `daphne` — ASGI server

---
