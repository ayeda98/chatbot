# 📖 Guide de déploiement — Chatbot Juridique Bénin

## Fichiers du projet
```
chatbot-juridique/
├── app.py            ← Code principal du bot
├── requirements.txt  ← Dépendances Python
├── render.yaml       ← Config déploiement
└── GUIDE.md          ← Ce fichier
```

---

## ÉTAPE 1 — Obtenir la clé API Groq (5 min)

1. Va sur https://console.groq.com
2. Crée un compte gratuit
3. Va dans **"API Keys"** → **"Create API Key"**
4. Copie la clé (commence par `gsk_...`)
5. **Garde-la précieusement !**

---

## ÉTAPE 2 — Créer une Page Facebook + App Meta (20 min)

### 2a. Créer une Page Facebook
1. Va sur facebook.com → **"Créer une Page"**
2. Choisis **"Entreprise ou marque"**
3. Nom : ex. "Assistant Juridique Bénin"
4. Catégorie : Services juridiques

### 2b. Créer l'application Meta Developer
1. Va sur https://developers.facebook.com
2. **"Mes applications"** → **"Créer une application"**
3. Choisis **"Entreprise"**
4. Nom de l'app : ex. "ChatbotJuridique"
5. Dans le dashboard → **"Ajouter un produit"** → **"Messenger"** → Configurer

### 2c. Générer le Page Access Token
1. Dans Messenger → **"Tokens d'accès"**
2. Sélectionne ta Page Facebook
3. Clique **"Générer un token"**
4. Copie ce token (très long)

---

## ÉTAPE 3 — Déployer sur Render.com (10 min)

1. Crée un compte sur https://render.com (gratuit)
2. Va sur https://github.com → crée un **nouveau dépôt** public
3. Upload les 3 fichiers (app.py, requirements.txt, render.yaml)
4. Sur Render : **"New"** → **"Web Service"** → connecte ton GitHub
5. Sélectionne ton dépôt → **"Create Web Service"**
6. Dans **"Environment Variables"**, ajoute :
   - `GROQ_API_KEY` → ta clé Groq
   - `PAGE_ACCESS_TOKEN` → ton token Meta
   - `VERIFY_TOKEN` → `mon_token_secret_123`
7. Clique **"Deploy"** → attends 2-3 minutes
8. Ton URL sera : `https://chatbot-juridique-benin.onrender.com`

---

## ÉTAPE 4 — Connecter le Webhook Meta (10 min)

1. Dans Meta Developer → Messenger → **"Webhooks"**
2. Clique **"Modifier les callbacks"**
3. URL du callback : `https://TON-URL.onrender.com/webhook`
4. Token de vérification : `mon_token_secret_123`
5. Clique **"Vérifier et enregistrer"** ✅
6. Coche les abonnements : `messages`, `messaging_postbacks`
7. Clique **"Ajouter des abonnements"** sur ta Page

---

## ÉTAPE 5 — Ajouter le bouton "Démarrer" (optionnel)

Lance cette commande dans un terminal (ou utilise Postman) :

```bash
curl -X POST "https://graph.facebook.com/v18.0/me/messenger_profile" \
  -H "Content-Type: application/json" \
  -d '{
    "get_started": {"payload": "GET_STARTED"},
    "greeting": [{"locale": "default", "text": "Bienvenue ! Je suis votre assistant juridique spécialisé dans le droit béninois. 👨‍⚖️"}]
  }' \
  "?access_token=TON_PAGE_ACCESS_TOKEN"
```

---

## ✅ Test du bot

1. Va sur ta Page Facebook
2. Clique **"Envoyer un message"**
3. Pose une question comme :
   - *"Quels sont mes droits en cas de licenciement ?"*
   - *"Comment créer une SARL au Bénin ?"*
   - *"Mon propriétaire veut m'expulser, que faire ?"*

---

## 🔧 Personnalisation

Pour modifier le comportement du bot, édite le `SYSTEM_PROMPT` dans `app.py` :
- Ajoute des domaines juridiques spécifiques
- Change la langue ou le ton
- Ajoute des références à des lois précises

---

## ❓ Problèmes fréquents

| Problème | Solution |
|---|---|
| Webhook non vérifié | Vérifie que VERIFY_TOKEN correspond exactement |
| Bot ne répond pas | Vérifie le PAGE_ACCESS_TOKEN dans Render |
| Erreur Groq | Vérifie la clé API et les limites gratuites |
| Timeout Render | Le service gratuit "dort" après 15min d'inactivité |

---

## 📊 Limites du plan gratuit

| Service | Limite gratuite |
|---|---|
| Groq | ~14,400 requêtes/jour (Llama 3 70B) |
| Render | 750h/mois (suffit pour 1 service) |
| Meta Messenger | Illimité en mode développement |

---

*Guide créé pour le projet Chatbot Juridique Bénin 🇧🇯*
