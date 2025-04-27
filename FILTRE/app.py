import streamlit as st
import joblib
import imaplib
import email
import os
import json
from email.header import decode_header
from sklearn.feature_extraction.text import TfidfVectorizer
import uuid

# === Chargement du modèle et vectorizer ===
model = joblib.load("naive_bayes_model.joblib")
vectorizer = joblib.load("tfid.joblib")

# === Fichiers d'historique ===
HISTORIQUE_FILE = "historique.json"

# === Dossiers de classement local ===
os.makedirs("SPAM", exist_ok=True)
os.makedirs("HAM", exist_ok=True)

# === Fonctions utilitaires ===
def charger_historique():
    if os.path.exists(HISTORIQUE_FILE):
        with open(HISTORIQUE_FILE, "r") as f:
            return json.load(f)
    return []

def sauvegarder_historique(data):
    with open(HISTORIQUE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def nettoyer_texte(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""

def analyser_mail(msg_id, raw_email):
    msg = email.message_from_bytes(raw_email)
    subject = decode_header(msg["Subject"])[0][0]
    subject = subject.decode() if isinstance(subject, bytes) else subject
    from_ = msg.get("From")
    body = nettoyer_texte(msg)

    vect = vectorizer.transform([subject + " " + body])
    pred = model.predict(vect)[0]

    dossier = "SPAM" if pred == 1 else "HAM"
    with open(f"{dossier}/mail_{msg_id}.txt", "w", encoding="utf-8") as f:
        f.write(f"From: {from_}\nSubject: {subject}\n\n{body}")

    return {
        "id": msg_id,
        "from": from_,
        "subject": subject,
        "prediction": "SPAM" if pred == 1 else "HAM",
        "body": body
    }

# === Interface Streamlit ===
st.title("📧 Analyseur de mails ")

EMAIL = st.secrets["EMAIL"]
PASSWORD = st.secrets["PASSWORD"]
IMAP_SERVER = "imap.gmail.com"

def analyser_boite(boite="inbox", prefix="inbox"):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select(boite)
    status, messages = mail.search(None, "ALL")
    mail_ids = messages[0].split()[-5:]  # Derniers 5 mails

    historique = charger_historique()
    ids_existants = {m["id"] for m in historique}

    for msg_id in mail_ids:
        msg_id_str = f"{prefix}_{msg_id.decode()}"
        if msg_id_str in ids_existants:
            continue
        status, data = mail.fetch(msg_id, "(RFC822)")
        raw_email = data[0][1]
        info = analyser_mail(msg_id_str, raw_email)
        historique.append(info)

    sauvegarder_historique(historique)
    st.success(f"Analyse de la boîte {boite} terminée ✅")

# === Boutons d’analyse
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Analyser l'Inbox Gmail"):
        analyser_boite("inbox", "inbox")

with col2:
    if st.button("🧹 Analyser le dossier SPAM Gmail"):
        analyser_boite("[Gmail]/Spam", "spam")
    
    
# === Affichage de l’historique ===
st.subheader("📜 Historique des analyses")

# Charger l'historique une seule fois (même si tu réactualises l'appli)
if "historique" not in st.session_state:
    st.session_state.historique = charger_historique()

if "mail_affiche" not in st.session_state:
    st.session_state.mail_affiche = None  # pour suivre le mail affiché

historique = st.session_state.historique

if historique:
    for i, mail_info in enumerate(reversed(historique[-20:])):  # les 20 derniers
        mail_key = f"{mail_info['id']}_{i}"

        with st.expander(f"📩 {mail_info['subject']} ({mail_info['prediction']})", expanded=False):
            st.write(f"**From:** {mail_info['from']}")
            st.write(f"**Sujet:** {mail_info['subject']}")

            if st.button("📖 Voir le contenu", key=f"btn_{mail_key}"):
                st.session_state.mail_affiche = mail_key

            if st.session_state.mail_affiche == mail_key:
                st.text_area("Contenu du mail", mail_info["body"], height=300, key=f"txt_{mail_key}")
else:
    st.info("Aucun mail analysé pour l’instant.")


