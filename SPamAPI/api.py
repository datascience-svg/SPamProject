from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import imaplib
import email
from email.header import decode_header
import os
import toml
import json

# === Secrets depuis .streamlit/secrets.toml ===
secrets = toml.load(".streamlit/secrets.toml")
EMAIL = secrets["EMAIL"]
PASSWORD = secrets["PASSWORD"]

# === Chargement du modèle et du vectorizer ===
model = joblib.load("model.joblib")
vectorizer = joblib.load("vectorizer.joblib")

# === Dossier d’historique ===
HISTORY_FILE = "historique.json"

# === Init FastAPI ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour développement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Schéma pour analyse de texte ===
class MailText(BaseModel):
    content: str

# === Chargement/Sauvegarde historique local ===
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# === Route : Analyser du texte libre ===
@app.post("/analyze-text")
def analyze_text(mail: MailText):
    vect = vectorizer.transform([mail.content])
    prediction = model.predict(vect)[0]

    # Ajout à l’historique
    history = load_history()
    history.append({
        "id": f"text_{len(history)+1}",
        "from": "utilisateur",
        "subject": "Texte collé",
        "body": mail.content,
        "prediction": "spam" if prediction == 1 else "ham"
    })
    save_history(history)

    return {"prediction": "spam" if prediction == 1 else "ham"}

# === Route : Analyser les 5 derniers mails de la boîte Gmail ===
@app.get("/analyze-latest")
def analyze_latest():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()[-10:]  # Les 5 derniers mails

        history = load_history()
        analyzed_ids = {h["id"] for h in history}

        new_results = []

        for msg_id in mail_ids:
            if msg_id.decode() in analyzed_ids:
                continue  # Déjà traité

            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Sujet
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            # Corps
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            content = subject + " " + body
            vect = vectorizer.transform([content])
            prediction = model.predict(vect)[0]

            result = {
                "id": msg_id.decode(),
                "from": msg.get("From"),
                "subject": subject,
                "body": body,
                "prediction": "spam" if prediction == 1 else "ham"
            }
            history.append(result)
            new_results.append(result)

        save_history(history)
        return {"results": new_results}

    except Exception as e:
        return {"error": str(e)}

# === Route : Consulter l’historique complet (ou les 5 derniers) ===
@app.get("/history")
def get_history():
    history = load_history()
    return history[-10:]  # les 5 derniers
