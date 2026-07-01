# Motion Studio — IMU Sensor Dashboard

A real-time web dashboard that turns your smartphone into an IMU controller. The phone streams orientation (yaw / pitch / roll) over WebSocket to a Flask server, which broadcasts it live to a desktop browser running one of five interactive apps.

**Live demo:** https://imu-motion-studio.onrender.com/sessions

---

## What it does

| Page | What happens |
|------|-------------|
| `/draw` | Phone tilt controls a paintbrush — draw in the air |
| `/cube` | A Three.js 3D cube rotates to match your phone's orientation |
| `/phone3d` | A 3D phone model mirrors your physical device in real time |
| `/drums` | Threshold-based gesture detection triggers drum sounds via Web Audio API |
| `/sessions` | Record IMU sessions to SQLite and review them as time-series charts |

---

## How it works

```
Phone (/sender)  ──WebSocket──►  Flask server  ──WebSocket broadcast──►  Desktop browser
                                       │
                                  SQLite DB
                                (session recordings)
```

- The phone opens `/sender` in its browser and fires `DeviceOrientationEvent` data to the server via Socket.IO.
- The server re-broadcasts the `imu` event to all connected desktop clients instantly.
- An HTTP POST endpoint `/data` is also supported as a fallback for the **Sensor Logger** app.
- Sessions can be started/stopped from any app page; readings are saved to SQLite and charted in `/sessions`.

---

## Run locally (Windows)

**Double-click `start.bat`** — it auto-creates a virtual environment, installs dependencies, starts the server, and opens Chrome.

Or manually:

```bash
cd localhost
pip install -r requirements.txt
python main.py
```

Server starts at `http://localhost:8000`. The terminal prints the phone URL (your LAN IP):

```
  Motion Studio
  Dashboard: http://localhost:8000
  Sender:    http://192.168.x.x:8000/sender
```

Open the Sender URL on your phone's browser and grant motion sensor permission. Then open any app on your desktop.

---

## Tech stack

- **Backend** — Python 3.11, Flask 3.0, Flask-SocketIO 5.3, eventlet
- **Database** — SQLite (auto-created on first run; persistent disk `/data` on Render)
- **Frontend** — Socket.IO, Three.js, Chart.js, Web Audio API, Material Symbols
- **Deployment** — Render.com (Gunicorn, persistent disk for SQLite)

---

## Project structure

```
IMU/
├── localhost/
│   ├── main.py          # Flask server — routes, SocketIO events, session API
│   ├── database.py      # SQLite helpers (sessions, imu_readings, session_events)
│   ├── requirements.txt
│   ├── static/          # Bundled JS (Three.js, Chart.js, Socket.IO client)
│   └── templates/       # Jinja2 HTML pages
│       ├── base.html
│       ├── sender.html  # Phone sensor transmitter
│       ├── draw.html
│       ├── cube.html
│       ├── phone3d.html
│       ├── drums.html
│       ├── sessions.html
│       └── session_detail.html
├── render/              # Render.com deployment config (separate)
├── start.bat            # Windows one-click launcher
└── .gitignore
```
