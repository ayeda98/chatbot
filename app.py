import os
import json
import requests
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# ============================================================
# CONFIGURATION — Remplace par tes vraies clés
# ============================================================
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mon_token_secret_123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "COLLE_TON_TOKEN_ICI")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "COLLE_TA_CLE_GROQ_ICI")

# ============================================================
# SYSTÈME PROMPT — Personnalité juridique du bot
# ============================================================
SYSTEM_PROMPT = """Tu es un assistant juridique spécialisé dans le droit béninois et 
le droit en Afrique francophone. Tu aides les citoyens à comprendre leurs droits 
et les procédures légales de manière simple et accessible.

Domaines couverts :
- Droit civil (famille, successions, contrats, propriété)
- Droit du travail (contrat de travail, licenciement, congés)
- Droit pénal (infractions courantes, procédures)
- Droit foncier et immobilier (BÉNIN)
- Droit des affaires (OHADA, création d'entreprise, SARL, SA)
- Procédures administratives et judiciaires au Bénin

Règles importantes :
1. Réponds TOUJOURS en français simple et clair, compréhensible par tous.
2. Base-toi sur le droit béninois (codes, lois OHADA, UEMOA) en priorité.
3. Pour chaque réponse, structure ainsi : 
   - La règle générale
   - Ce que ça signifie concrètement
   - Les démarches possibles
4. Ajoute TOUJOURS une note de fin : "⚠️ Ceci est une information générale. 
   Pour votre situation spécifique, consultez un avocat ou notaire."
5. Si la question sort du domaine juridique, redirige poliment.
6. Ne donne jamais de conseils médicaux, financiers ou politiques.
"""

# ============================================================
# CLIENT GROQ
# ============================================================
client = Groq(api_key=GROQ_API_KEY)

# Historique simple en mémoire (réinitialisé au redémarrage)
conversation_history = {}

def get_groq_response(user_id, user_message):
    """Envoie le message à Groq et retourne la réponse."""
    
    # Initialiser l'historique si nouvel utilisateur
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    # Ajouter le message de l'utilisateur
    conversation_history[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Garder seulement les 10 derniers échanges (mémoire limitée)
    recent_history = conversation_history[user_id][-10:]
    
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Modèle gratuit Groq
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *recent_history
            ],
            max_tokens=800,
            temperature=0.3  # Réponses précises (juridique)
        )
        
        assistant_message = response.choices[0].message.content
        
        # Sauvegarder la réponse dans l'historique
        conversation_history[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
        
    except Exception as e:
        print(f"Erreur Groq: {e}")
        return "Désolé, je rencontre une difficulté technique. Veuillez réessayer dans quelques instants."


def send_messenger_message(recipient_id, message_text):
    """Envoie un message via l'API Messenger."""
    
    # Découper les messages longs (limite Messenger : 2000 chars)
    chunks = [message_text[i:i+1900] for i in range(0, len(message_text), 1900)]
    
    for chunk in chunks:
        data = {
            "recipient": {"id": recipient_id},
            "message": {"text": chunk}
        }
        
        response = requests.post(
            f"https://graph.facebook.com/v18.0/me/messages",
            params={"access_token": PAGE_ACCESS_TOKEN},
            headers={"Content-Type": "application/json"},
            json=data
        )
        
        if response.status_code != 200:
            print(f"Erreur Messenger: {response.text}")


def send_typing_indicator(recipient_id, action="typing_on"):
    """Affiche l'indicateur de frappe (réalisme)."""
    data = {
        "recipient": {"id": recipient_id},
        "sender_action": action
    }
    requests.post(
        f"https://graph.facebook.com/v18.0/me/messages",
        params={"access_token": PAGE_ACCESS_TOKEN},
        json=data
    )


# ============================================================
# WEBHOOK — Vérification Meta
# ============================================================
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta vérifie ton webhook avec ce endpoint."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook vérifié avec succès !")
        return challenge, 200
    else:
        print("❌ Vérification échouée")
        return "Forbidden", 403


# ============================================================
# WEBHOOK — Réception des messages
# ============================================================
@app.route("/webhook", methods=["POST"])
def receive_message():
    """Reçoit et traite les messages Messenger."""
    data = request.get_json()
    
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging in entry.get("messaging", []):
                
                sender_id = messaging["sender"]["id"]
                
                # Message texte classique
                if "message" in messaging and "text" in messaging["message"]:
                    user_text = messaging["message"]["text"]
                    
                    print(f"📩 Message reçu de {sender_id}: {user_text}")
                    
                    # Afficher "en train d'écrire..."
                    send_typing_indicator(sender_id, "typing_on")
                    
                    # Obtenir la réponse de Groq
                    response_text = get_groq_response(sender_id, user_text)
                    
                    # Arrêter l'indicateur et envoyer la réponse
                    send_typing_indicator(sender_id, "typing_off")
                    send_messenger_message(sender_id, response_text)
                    
                    print(f"✅ Réponse envoyée à {sender_id}")
                
                # Postback (boutons cliquables)
                elif "postback" in messaging:
                    payload = messaging["postback"]["payload"]
                    if payload == "GET_STARTED":
                        welcome = (
                            "👋 Bonjour ! Je suis votre assistant juridique spécialisé "
                            "dans le droit béninois et africain.\n\n"
                            "📚 Je peux vous aider sur :\n"
                            "• Droit du travail\n"
                            "• Droit de la famille\n"
                            "• Droit foncier\n"
                            "• Droit des affaires (OHADA)\n"
                            "• Procédures judiciaires\n\n"
                            "💬 Posez votre question juridique en français !"
                        )
                        send_messenger_message(sender_id, welcome)
    
    return jsonify({"status": "ok"}), 200


# ============================================================
# PAGE D'ACCUEIL (test)
# ============================================================
@app.route("/", methods=["GET"])
def home():
    return "✅ Chatbot Juridique Bénin — Actif !", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Serveur démarré sur le port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
