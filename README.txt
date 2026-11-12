JARVIS - Futuristic personal AI web app

FILES
- main.py: FastAPI backend and SQLite conversation memory
- index.html: Iron Man-inspired HUD interface, chat, browser speech input/output
- requirements.txt / Dockerfile: deployment setup

SETUP (server/hosting)
1. Install Python 3.11+.
2. Run: pip install -r requirements.txt
3. Set GEMINI_API_KEY as an environment variable (do not put it in index.html or public files).
4. Run: uvicorn main:app --host 0.0.0.0 --port 7860
5. Open the URL shown by your host.

API key: create/manage it at Google AI Studio. Gemini API quotas and pricing/free tier can change; check your account before use.
Memory: SQLite is stored on the host filesystem. On hosts with ephemeral storage it can reset after rebuild/restart.
Voice: Chrome/HTTPS and microphone permission are recommended. Speech recognition availability varies by browser/language.
This is a starter personal assistant, not full phone/computer control. Any future device automation should require your explicit permission.
