# SPAMPROJECT - Filtre Anti-Spam + Plugin Outlook

Bienvenue sur le dépôt de mon projet complet de filtre anti-spam basé sur l'intelligence artificielle.

## Objectif

Créer un système complet capable de :
- Détecter automatiquement les spams dans les emails.
- Analyser et classer les messages avec un modèle Machine Learning entraîné.
- Offrir deux interfaces d'utilisation : 
  - Une application **Streamlit** pour une utilisation locale.
  - Un **plugin Outlook** pour analyser directement les emails depuis Microsoft Outlook.

---

## Structure du Projet

| Dossier/Fichier    | Description                                  |
|--------------------|---------------------------------------------|
| **filtre/**         | Application Streamlit, modèle IA, historique, entraînement. |
| **SPamAPI/**        | Backend API FastAPI pour analyser les emails. |
| **SPamPlugin/**     | Add-in (plugin) Outlook avec interface web en HTML/CSS/JS. |
| **LICENSE**         | Licence MIT pour ce projet. |
| **README.md**       | Ce fichier, documentation générale du projet. |

---

## Comment utiliser ce projet
## Pré-requis

- Node.js et npm installés

- Office Add-in CLI (npm install -g yo generator-office)

-Compte Microsoft avec Office installé (version supportant les compléments)

## 1. Cloner le projet

```bash
git clone https://github.com/datascience-svg/SPAMPROJECT.git
cd SPAMPROJECT

## 2.Utiliser le filtre Streamlit localement

cd filtre
pip install -r requirements.txt
streamlit run app.py

## 3.Lancer le backend API (FastAPI)
NB: pour les prerequis il est important d'avoir outlook classic installé dans dans pc 

cd SPamAPI
pip install -r requirements.txt

configurer les acces Gmail
SPamAPI/.streamlit/secrets.toml
- Mettre son adresse Gmail
- Son mot de passe d'application (pas son vrai mot de passe Gmail !).
uvicorn api:app --reload --port 8000

## 4.Lancer le plugin Outlook

cd SPamPlugin
npm install
npm start
