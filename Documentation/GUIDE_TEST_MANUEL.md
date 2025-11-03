# Guide de Test Manuel Rapide

## 🎯 Utilisation avec Swagger UI (Recommandé pour débuter)

Swagger UI est **le moyen le plus simple** de tester l'API !

### 1. Démarrer l'application
```bash
uvicorn main:app --reload
```

### 2. Ouvrir Swagger
http://localhost:8000/docs

### 3. Tester dans l'ordre

#### Étape 1: Connexion Admin
1. Cliquez sur `/auth/login` → "Try it out"
2. Modifiez le JSON :
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```
3. Cliquez sur "Execute"
4. **Copiez le token** (access_token) pour les étapes suivantes

#### Étape 2: Inscription Étudiant
1. Cliquez sur `/auth/register` → "Try it out"
2. Modifiez le JSON :
```json
{
  "email": "etudiant@example.com",
  "password": "password123",
  "full_name": "Jean Dupont",
  "matricule": "ETU001"
}
```
3. Exécutez → Compte créé mais **inactif**

#### Étape 3: Activer le compte
1. Cliquez sur `/users/{user_id}` → "Try it out"
2. Cliquez sur le petit cadenas 🔒 en haut
3. Collez le token admin : `Bearer VOTRE_TOKEN`
4. Mettez l'ID de l'étudiant (probablement 2)
5. Modifiez le body :
```json
{
  "is_active": true
}
```
6. Exécutez

#### Étape 4: Se connecter en tant qu'étudiant
1. `/auth/login` avec les identifiants de l'étudiant
2. Copiez ce nouveau token

#### Étape 5: Créer une demande
1. `/requests` → 🔒 Authentification avec le token étudiant
2. Body :
```json
{
  "document_types": ["RELEVER DE NOTE"]
}
```
3. Exécutez

#### Étape 6: Voir ses demandes
1. `/requests` → 🔒 Token étudiant
2. Exécutez → Vous voyez vos demandes

#### Étape 7: Valider la demande (Admin)
1. `/requests/{request_id}` → 🔒 Token admin
2. Body :
```json
{
  "status": "validate"
}
```
3. Exécutez

#### Étape 8: Voir le changement de statut
1. `/requests` → 🔒 Token étudiant
2. Exécutez → Le statut est maintenant "validate"

---

## 🚀 Test Automatique (Script Bash)

### Exécuter tous les tests en une fois

```bash
./test_api.sh
```

**Ce script teste automatiquement** :
- ✅ Connexion admin
- ✅ Inscription étudiant
- ✅ Activation de compte
- ✅ Création de demandes
- ✅ Validation de demandes
- ✅ Sécurité (accès refusé)
- ✅ Et plus encore !

---

## 📮 Utilisation avec Postman

### Import de la collection

1. **Ouvrir Postman**
2. **Nouvelle Collection** : "API Documents"
3. **Créer les requêtes** suivantes :

#### 1. Connexion Admin
```
POST http://localhost:8000/auth/login
Body (JSON):
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

**Important** : Créez une variable `token` avec le token reçu

#### 2. Inscription Étudiant
```
POST http://localhost:8000/auth/register
Body (JSON):
{
  "email": "etudiant.test@postman.com",
  "password": "password123",
  "full_name": "Test Postman",
  "matricule": "POST001"
}
```

#### 3. Activer Compte
```
PUT http://localhost:8000/users/2
Headers:
  Authorization: Bearer {{token}}
Body (JSON):
{
  "is_active": true
}
```

#### 4. Connexion Étudiant
```
POST http://localhost:8000/auth/login
Body (JSON):
{
  "email": "etudiant.test@postman.com",
  "password": "password123"
}
```

Créez une variable `student_token`

#### 5. Créer Demande
```
POST http://localhost:8000/requests
Headers:
  Authorization: Bearer {{student_token}}
Body (JSON):
{
  "document_types": ["RELEVER DE NOTE", "ATTESTATION DE REUSSITE"]
}
```

#### 6. Lister Demandes
```
GET http://localhost:8000/requests
Headers:
  Authorization: Bearer {{student_token}}
```

#### 7. Valider Demande
```
PUT http://localhost:8000/requests/1
Headers:
  Authorization: Bearer {{token}}
Body (JSON):
{
  "status": "validate"
}
```

### Utiliser les Variables Postman

**Étape 1** : Cliquez sur "Variables" dans votre collection

**Étape 2** : Ajoutez :
- `token` : Token admin
- `student_token` : Token étudiant
- `base_url` : `http://localhost:8000`

**Étape 3** : Utilisez `{{variable}}` dans vos requêtes

---

## 🌐 Utilisation avec cURL

### Quick Start

```bash
# 1. Connexion Admin
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Inscription Étudiant
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"etudiant@curl.com",
    "password":"password123",
    "full_name":"Curl Test",
    "matricule":"CURL001"
  }'

# 3. Créer une demande
curl -X POST "http://localhost:8000/requests" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_types":["RELEVER DE NOTE"]}'

# 4. Lister les demandes
curl -X GET "http://localhost:8000/requests" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔍 Test WebSocket

### Option 1: wscat (En ligne de commande)

```bash
# Installer wscat
npm install -g wscat

# Se connecter (remplacez 2 par l'ID utilisateur)
wscat -c ws://localhost:8000/ws/2
```

**Dans la session wscat** :
- Tapez : `{"type":"ping","message":"test"}`
- Vous devriez recevoir : `{"type":"pong","message":"Connection alive"}`

### Option 2: Client Web en ligne

**Visitez**: https://www.websocket.org/echo.html

**URL**: `ws://localhost:8000/ws/2`

**Message de test**:
```json
{
  "type": "ping",
  "message": "test"
}
```

### Option 3: Python Script

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/2"
    async with websockets.connect(uri) as websocket:
        # Envoyer un ping
        await websocket.send(json.dumps({"type": "ping", "message": "test"}))
        
        # Recevoir la réponse
        response = await websocket.recv()
        print(f"Réponse: {response}")

asyncio.run(test_websocket())
```

---

## 📊 Workflow Complet de Test

### Test de bout en bout (5 minutes)

1. **Swagger**: http://localhost:8000/docs
2. **Login Admin** → Copier token
3. **Register Étudiant** → Noter l'ID
4. **Activate User** (PUT /users/{id})
5. **Login Étudiant** → Copier token étudiant
6. **Créer Request** (POST /requests)
7. **Lister Requests** (GET /requests) → Vérifier pending
8. **Validate Request** (PUT /requests/{id} avec token admin)
9. **Lister Requests** → Vérifier validate

**✅ Si tout passe, votre API fonctionne !**

---

## 🐛 Dépannage Rapide

### "API non accessible"
```bash
# Vérifier que le serveur est lancé
curl http://localhost:8000/

# Relancer si nécessaire
uvicorn main:app --reload
```

### "Authentication failed"
```bash
# Réinitialiser la base de données
python init_db.py
```

### "Not enough permissions"
- Vérifiez que vous utilisez le bon token (admin pour admin actions)
- Vérifiez l'URL (remplacez {user_id} par un vrai ID)

### "Document request not found"
- Vérifiez que vous avez créé une demande d'abord
- Utilisez un ID valide (probablement 1 ou 2)

### "Database error"
```bash
# Réinitialiser complètement
python init_db.py
```

---

## ✅ Checklist de Test Basique

**Test minimal (pour vérifier que tout marche)** :

- [ ] `GET /` → 200 OK
- [ ] `POST /auth/login` (admin) → Token reçu
- [ ] `POST /auth/register` (étudiant) → Compte créé
- [ ] `PUT /users/{id}` (activation) → 200 OK
- [ ] `POST /auth/login` (étudiant) → Token reçu
- [ ] `POST /requests` → Demande créée
- [ ] `GET /requests` → Liste affichée
- [ ] `PUT /requests/{id}` → Statut changé

**Si ces 8 tests passent** → Votre API fonctionne ! 🎉

---

## 📚 Fichiers de Test Disponibles

1. **TEST_COMPLET.md** → Guide détaillé avec 30 tests
2. **test_api.sh** → Script automatique de test
3. **GUIDE_TEST_MANUEL.md** → Ce fichier (démarrage rapide)

---

**💡 Astuce** : Commencez par Swagger, puis testez avec votre méthode préférée !

