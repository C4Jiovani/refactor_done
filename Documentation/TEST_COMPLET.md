# Guide de Test Complet - API Gestion Documents Académiques

## 📋 Table des Matières

1. [Préparation](#préparation)
2. [Tests d'Authentification](#tests-dauthentification)
3. [Tests Utilisateurs](#tests-utilisateurs)
4. [Tests Documents](#tests-documents)
5. [Tests WebSocket](#tests-websocket)
6. [Tests d'Intégration](#tests-dintégration)

---

## 🔧 Préparation

### 1. Lancer l'Application

```bash
# Dans le terminal
uvicorn main:app --reload
```

**Explication**: Cette commande démarre le serveur FastAPI en mode reload, ce qui signifie que toute modification du code redémarrera automatiquement le serveur. L'API sera disponible sur `http://localhost:8000`.

### 2. Accéder à la Documentation

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

**Explication**: Ces interfaces permettent de visualiser et tester tous les endpoints sans utiliser Postman. Swagger offre un interface interactif, tandis que ReDoc affiche une documentation plus structurée.

### 3. Initialiser la Base de Données (si nécessaire)

```bash
python init_db.py
```

**Explication**: Ce script crée les tables de la base de données et initialise un compte administrateur par défaut.

---

## 🔐 Tests d'Authentification

### Test 1: Vérifier que l'API est accessible

**Endpoint**: `GET /`

**Méthode**: GET

**URL**: http://localhost:8000/

**Headers**: Aucun

**Réponse attendue**:
```json
{
  "message": "API Gestion Documents Étudiants",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

**Explication**: Ce test vérifie que le serveur est bien démarré et que l'API répond correctement. C'est le premier test à faire avant de tester les autres endpoints.

---

### Test 2: Inscription d'un nouvel étudiant

**Endpoint**: `POST /auth/register`

**Méthode**: POST

**URL**: http://localhost:8000/auth/register

**Headers**: 
```json
{
  "Content-Type": "application/json"
}
```

**Body**:
```json
{
  "email": "etudiant1@example.com",
  "password": "password123",
  "full_name": "Jean Dupont",
  "matricule": "ETU001"
}
```

**Explication**: 
- Crée un nouveau compte étudiant
- Par défaut, le compte est **inactif** (`is_active: false`)
- Un matricule sera automatiquement généré si non fourni (format: STUXXXXXX)
- L'utilisateur devra attendre la validation par un admin pour se connecter

**Réponse attendue (201 Created)**:
```json
{
  "id": 2,
  "email": "etudiant1@example.com",
  "full_name": "Jean Dupont",
  "is_active": false,
  "role": "etudiant",
  "type": "etudiant",
  "matricule": "ETU001",
  "nom": "Dupont",
  "prenom": "Jean",
  "created_at": "2025-01-XX..."
}
```

**⚠️ Note**: Le compte est créé mais **inactif**. Vous ne pourrez pas vous connecter immédiatement.

---

### Test 3: Tentative de connexion avec compte inactif

**Endpoint**: `POST /auth/login`

**Méthode**: POST

**URL**: http://localhost:8000/auth/login

**Body**:
```json
{
  "email": "etudiant1@example.com",
  "password": "password123"
}
```

**Explication**: On tente de se connecter avec le compte qu'on vient de créer, mais comme il est inactif, la connexion devrait échouer.

**Réponse attendue (403 Forbidden)**:
```json
{
  "detail": "Account not activated. Please wait for admin approval."
}
```

**✅ Vérification**: Ce comportement est correct et assure la sécurité du système.

---

### Test 4: Connexion en tant qu'administrateur

**Endpoint**: `POST /auth/login`

**Méthode**: POST

**URL**: http://localhost:8000/auth/login

**Body**:
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

**Explication**: On se connecte avec le compte admin créé automatiquement lors de l'initialisation.

**Réponse attendue (200 OK)**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**🔑 Important**: Copiez ce `access_token` ! Il sera nécessaire pour tous les tests suivants nécessitant une authentification.

**Durée de validité**: 30 minutes par défaut (configuré dans `ACCESS_TOKEN_EXPIRE_MINUTES`)

---

### Test 5: Vérifier le profil utilisateur connecté

**Endpoint**: `GET /users/me`

**Méthode**: GET

**URL**: http://localhost:8000/users/me

**Headers**: 
```
Authorization: Bearer {VOTRE_TOKEN_ICI}
```

**Explication**: Retourne les informations de l'utilisateur actuellement connecté. Teste la validité du token JWT.

**Réponse attendue (200 OK)**:
```json
{
  "id": 1,
  "email": "admin@example.com",
  "matricule": "ADMIN001",
  "full_name": "Système Administrateur",
  "nom": "Administrateur",
  "prenom": "Système",
  "is_active": true,
  "role": "admin",
  "type": "admin",
  "created_at": "2025-01-XX..."
}
```

**✅ Vérification**: Si vous obtenez cette réponse, votre token est valide !

---

## 👥 Tests Utilisateurs (Admin uniquement)

### Test 6: Récupérer tous les utilisateurs

**Endpoint**: `GET /users`

**Méthode**: GET

**URL**: http://localhost:8000/users?skip=0&limit=100

**Headers**: 
```
Authorization: Bearer {VOTRE_TOKEN_ADMIN}
```

**Explication**: 
- Liste tous les utilisateurs du système
- **Admin seulement** : les utilisateurs normaux obtiendraient une erreur 403
- `skip` et `limit` permettent la pagination

**Réponse attendue (200 OK)**:
```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "matricule": "ADMIN001",
    "full_name": "Système Administrateur",
    "is_active": true,
    "role": "admin",
    "created_at": "2025-01-XX..."
  },
  {
    "id": 2,
    "email": "etudiant1@example.com",
    "matricule": "ETU001",
    "full_name": "Jean Dupont",
    "is_active": false,
    "role": "etudiant",
    "created_at": "2025-01-XX..."
  }
]
```

**✅ Vérification**: Vous devriez voir au moins l'admin et l'étudiant que vous avez créé.

---

### Test 7: Récupérer les utilisateurs en attente de validation

**Endpoint**: `GET /users/pending`

**Méthode**: GET

**URL**: http://localhost:8000/users/pending

**Headers**: 
```
Authorization: Bearer {VOTRE_TOKEN_ADMIN}
```

**Explication**: Liste uniquement les utilisateurs avec `is_active: false`, c'est-à-dire ceux qui attendent d'être validés par un admin.

**Réponse attendue (200 OK)**:
```json
[
  {
    "id": 2,
    "email": "etudiant1@example.com",
    "matricule": "ETU001",
    "full_name": "Jean Dupont",
    "is_active": false,
    "role": "etudiant",
    "created_at": "2025-01-XX..."
  }
]
```

**✅ Vérification**: Devrait contenir l'étudiant créé à l'étape précédente.

---

### Test 8: Activer un compte utilisateur

**Endpoint**: `PUT /users/{user_id}`

**Méthode**: PUT

**URL**: http://localhost:8000/users/2

**Headers**: 
```
Authorization: Bearer {VOTRE_TOKEN_ADMIN}
Content-Type: application/json
```

**Body**:
```json
{
  "is_active": true
}
```

**Explication**: 
- Active le compte de l'utilisateur (permet la connexion)
- **Important** : Cet endpoint génère une notification WebSocket si connecté
- L'utilisateur peut maintenant se connecter

**Réponse attendue (200 OK)**:
```json
{
  "id": 2,
  "email": "etudiant1@example.com",
  "matricule": "ETU001",
  "full_name": "Jean Dupont",
  "is_active": true,
  "role": "etudiant",
  "created_at": "2025-01-XX..."
}
```

**✅ Vérification**: Le champ `is_active` doit passer à `true`.

---

### Test 9: Connexion avec le compte maintenant actif

**Endpoint**: `POST /auth/login`

**Méthode**: POST

**URL**: http://localhost:8000/auth/login

**Body**:
```json
{
  "email": "etudiant1@example.com",
  "password": "password123"
}
```

**Explication**: Maintenant que le compte est actif, la connexion devrait fonctionner.

**Réponse attendue (200 OK)**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**🔑 Important**: Copiez ce nouveau token ! Ce sera le token de l'étudiant pour les tests suivants.

---

### Test 10: Créer un deuxième étudiant

**Endpoint**: `POST /auth/register`

**Méthode**: POST

**URL**: http://localhost:8000/auth/register

**Body**:
```json
{
  "email": "etudiant2@example.com",
  "password": "password123",
  "full_name": "Marie Martin",
  "matricule": "ETU002"
}
```

**Explication**: On crée un deuxième compte pour avoir plus de données de test.

**Réponse attendue (201 Created)**: Un nouvel utilisateur avec `is_active: false`

---

## 📄 Tests Documents

### Test 11: Créer une demande de document (Étudiant)

**Endpoint**: `POST /requests`

**Méthode**: POST

**URL**: http://localhost:8000/requests

**Headers**: 
```
Authorization: Bearer {TOKEN_ETUDIANT}
Content-Type: application/json
```

**Body**:
```json
{
  "document_types": [
    "RELEVER DE NOTE",
    "ATTESTATION DE REUSSITE"
  ]
}
```

**Explication**: 
- Crée une ou plusieurs demandes de documents en une seule requête
- Les types de documents doivent correspondre aux catégories créées
- Le système cherche automatiquement la catégorie correspondante
- Par défaut, le statut est `pending` et `est_paye` est `false`

**Réponse attendue (201 Created)**:
```json
[
  {
    "id": 1,
    "user_id": 2,
    "document_type": "RELEVER DE NOTE",
    "status": "pending",
    "created_at": "2025-01-XX...",
    "updated_at": null,
    "user": {
      "id": 2,
      "email": "etudiant1@example.com",
      ...
    }
  },
  {
    "id": 2,
    "user_id": 2,
    "document_type": "ATTESTATION DE REUSSITE",
    "status": "pending",
    "created_at": "2025-01-XX...",
    "updated_at": null,
    "user": {...}
  }
]
```

**✅ Vérification**: 
- Deux documents créés
- Statut: `pending`
- L'utilisateur est correctement associé

---

### Test 12: Récupérer toutes les demandes (Étudiant)

**Endpoint**: `GET /requests`

**Méthode**: GET

**URL**: http://localhost:8000/requests

**Headers**: 
```
Authorization: Bearer {TOKEN_ETUDIANT}
```

**Explication**: 
- Les utilisateurs normaux voient **uniquement leurs propres** demandes
- Les admins voient **toutes** les demandes

**Réponse attendue (200 OK)**:
```json
[
  {
    "id": 1,
    "user_id": 2,
    "document_type": "RELEVER DE NOTE",
    "status": "pending",
    "created_at": "2025-01-XX...",
    "updated_at": null
  },
  {
    "id": 2,
    "user_id": 2,
    "document_type": "ATTESTATION DE REUSSITE",
    "status": "pending",
    "created_at": "2025-01-XX...",
    "updated_at": null
  }
]
```

**✅ Vérification**: Vous devriez voir uniquement les demandes de votre compte.

---

### Test 13: Récupérer une demande spécifique

**Endpoint**: `GET /requests/{request_id}`

**Méthode**: GET

**URL**: http://localhost:8000/requests/1

**Headers**: 
```
Authorization: Bearer {TOKEN_ETUDIANT}
```

**Explication**: Retourne les détails d'une demande spécifique.

**Réponse attendue (200 OK)**:
```json
{
  "id": 1,
  "user_id": 2,
  "document_type": "RELEVER DE NOTE",
  "status": "pending",
  "created_at": "2025-01-XX...",
  "updated_at": null,
  "user": {
    "id": 2,
    "email": "etudiant1@example.com",
    ...
  }
}
```

**✅ Vérification**: Les informations du document sont correctes.

---

### Test 14: Voir toutes les demandes (Admin)

**Endpoint**: `GET /requests`

**Méthode**: GET

**URL**: http://localhost:8000/requests

**Headers**: 
```
Authorization: Bearer {TOKEN_ADMIN}
```

**Explication**: Les admins voient toutes les demandes de tous les utilisateurs.

**Réponse attendue (200 OK)**:
```json
[
  {
    "id": 1,
    "user_id": 2,
    "document_type": "RELEVER DE NOTE",
    "status": "pending",
    "created_at": "2025-01-XX...",
    "user": {...}
  },
  {
    "id": 2,
    "user_id": 2,
    "document_type": "ATTESTATION DE REUSSITE",
    "status": "pending",
    "created_at": "2025-01-XX...",
    "user": {...}
  }
]
```

**✅ Vérification**: Vous voyez toutes les demandes, pas seulement les vôtres.

---

### Test 15: Valider une demande de document (Admin)

**Endpoint**: `PUT /requests/{request_id}`

**Méthode**: PUT

**URL**: http://localhost:8000/requests/1

**Headers**: 
```
Authorization: Bearer {TOKEN_ADMIN}
Content-Type: application/json
```

**Body**:
```json
{
  "status": "validate"
}
```

**Explication**: 
- Change le statut d'une demande
- Statuts possibles : `pending`, `validate`, `refuse`
- Génère une notification WebSocket pour l'utilisateur
- Met à jour automatiquement `date_de_validation` si le statut passe à `validate`

**Réponse attendue (200 OK)**:
```json
{
  "id": 1,
  "user_id": 2,
  "document_type": "RELEVER DE NOTE",
  "status": "validate",
  "created_at": "2025-01-XX...",
  "updated_at": "2025-01-XX...",
  "user": {...}
}
```

**✅ Vérification**: Le statut doit être `validate` et `updated_at` doit avoir changé.

---

### Test 16: Refuser une demande

**Endpoint**: `PUT /requests/{request_id}`

**Méthode**: PUT

**URL**: http://localhost:8000/requests/2

**Headers**: 
```
Authorization: Bearer {TOKEN_ADMIN}
Content-Type: application/json
```

**Body**:
```json
{
  "status": "refuse"
}
```

**Explication**: Change le statut à `refuse`, indiquant que la demande a été refusée.

**Réponse attendue (200 OK)**:
```json
{
  "id": 2,
  "user_id": 2,
  "document_type": "ATTESTATION DE REUSSITE",
  "status": "refuse",
  "created_at": "2025-01-XX...",
  "updated_at": "2025-01-XX...",
  "user": {...}
}
```

---

### Test 17: Tentative d'accès non autorisé

**Endpoint**: `PUT /requests/{request_id}`

**Méthode**: PUT

**URL**: http://localhost:8000/requests/1

**Headers**: 
```
Authorization: Bearer {TOKEN_ETUDIANT}
Content-Type: application/json
```

**Body**:
```json
{
  "status": "validate"
}
```

**Explication**: Un utilisateur normal essaie de modifier une demande.

**Réponse attendue (403 Forbidden)**:
```json
{
  "detail": "Not enough permissions"
}
```

**✅ Vérification**: Seuls les admins peuvent modifier les statuts.

---

### Test 18: Supprimer une demande (Admin)

**Endpoint**: `DELETE /requests/{request_id}`

**Méthode**: DELETE

**URL**: http://localhost:8000/requests/2

**Headers**: 
```
Authorization: Bearer {TOKEN_ADMIN}
```

**Explication**: Supprime définitivement une demande de la base de données.

**Réponse attendue (204 No Content)**: Pas de contenu dans la réponse.

**⚠️ Attention**: Cette action est irréversible !

---

### Test 19: Créer plusieurs demandes avec différents types

**Endpoint**: `POST /requests`

**Méthode**: POST

**URL**: http://localhost:8000/requests

**Headers**: 
```
Authorization: Bearer {TOKEN_ETUDIANT}
Content-Type: application/json
```

**Body**:
```json
{
  "document_types": [
    "CERTIFICAT DE FIN D'ETUDE",
    "RELEVER DE NOTE",
    "ATTESTATION DE REUSSITE"
  ]
}
```

**Explication**: Teste la création de plusieurs demandes en une seule requête.

**Réponse attendue (201 Created)**: Array avec les 3 documents créés.

---

## 🌐 Tests WebSocket

### Test 20: Connexion WebSocket

**Outils**: Utilisez `wscat` ou un client WebSocket en ligne

**Installation wscat** (si nécessaire):
```bash
npm install -g wscat
```

**URL de connexion**: `ws://localhost:8000/ws/2`

**Explication**: 
- Remplacez `2` par l'ID de l'utilisateur (pas le matricule !)
- L'utilisateur 2 est l'étudiant que nous avons créé

**Commande wscat**:
```bash
wscat -c ws://localhost:8000/ws/2
```

**Réponse attendue**: Connexion établie, pas de message initial.

**Test d'envoi**: Tapez `{"type":"ping","message":"test"}`

**Réponse attendue**: `{"type":"pong","message":"Connection alive"}`

**Explication**: Cette fonctionnalité ping/pong vérifie que la connexion est active.

---

### Test 21: Recevoir une notification (WebSocket)

**Étape 1**: Connectez-vous au WebSocket (Test 20)

**Étape 2**: Dans un autre terminal, en tant qu'admin, modifiez le statut d'une demande :

```bash
# Commande curl (remplacez TOKEN_ADMIN)
curl -X PUT "http://localhost:8000/requests/1" \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"status":"validate"}'
```

**Explication**: 
- Modifier le statut d'une demande génère automatiquement une notification
- Si vous êtes connecté en WebSocket en tant que l'utilisateur propriétaire de la demande, vous devriez recevoir une notification

**Notification attendue dans wscat**:
```json
{
  "type": "request_status_changed",
  "message": "Le statut de votre demande a changé: validate",
  "data": {
    "request_id": 1,
    "old_status": "pending",
    "new_status": "validate",
    "document_type": "RELEVER DE NOTE"
  }
}
```

**✅ Vérification**: Les notifications fonctionnent en temps réel !

---

### Test 22: Notification de validation de compte

**Étape 1**: Créez un nouveau compte (inactif)

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "etudiant3@example.com",
    "password": "password123",
    "full_name": "Pierre Dubois",
    "matricule": "ETU003"
  }'
```

**Étape 2**: Connectez-vous en WebSocket avec l'ID du nouveau compte (vérifiez l'ID dans la réponse)

**Étape 3**: En tant qu'admin, activez le compte :

```bash
curl -X PUT "http://localhost:8000/users/ID_DU_NOUVEAU_COMPTE" \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"is_active":true}'
```

**Notification attendue**:
```json
{
  "type": "account_validated",
  "message": "Votre compte a été validé",
  "data": {
    "user_id": ID_DU_COMPTE,
    "is_active": true
  }
}
```

---

## 🧪 Tests d'Intégration

### Test 23: Workflow Complet - Étudiant

**Objectif**: Simuler le workflow complet d'un étudiant du début à la fin

1. **Créer un compte** : `POST /auth/register`
2. **Vérifier qu'on ne peut pas se connecter** : `POST /auth/login` (doit échouer)
3. **Admin active le compte** : `PUT /users/{id}` avec `is_active: true`
4. **Se connecter** : `POST /auth/login` (doit réussir)
5. **Créer des demandes** : `POST /requests`
6. **Voir mes demandes** : `GET /requests`
7. **Admin valide** : `PUT /requests/{id}` avec `status: validate`
8. **Voir les demandes validées** : `GET /requests` (doit montrer le nouveau statut)

**✅ Vérification**: Le workflow complet fonctionne sans erreur.

---

### Test 24: Test de Sécurité - Accès Non Autorisé

**Test 1 - Accès sans token**:
```bash
curl http://localhost:8000/users/me
```
**Attendu**: 401 Unauthorized

**Test 2 - Accès avec token invalide**:
```bash
curl -H "Authorization: Bearer token_invalide" http://localhost:8000/users/me
```
**Attendu**: 401 Unauthorized

**Test 3 - Étudiant essaie de voir tous les utilisateurs**:
```bash
curl -H "Authorization: Bearer TOKEN_ETUDIANT" http://localhost:8000/users
```
**Attendu**: 403 Forbidden

**Explication**: Les mécanismes de sécurité JWT et de rôles fonctionnent correctement.

---

### Test 25: Test de Performance - Pagination

**Endpoint**: `GET /users`

**Test avec limite**:
```bash
curl -H "Authorization: Bearer TOKEN_ADMIN" "http://localhost:8000/users?skip=0&limit=5"
```

**Explication**: 
- `skip`: nombre d'éléments à ignorer
- `limit`: nombre maximum d'éléments à retourner
- Utile pour gérer de grandes quantités de données

**Réponse attendue**: Maximum 5 utilisateurs, peu importe le nombre total.

---

### Test 26: Créer un utilisateur SCO

**Endpoint**: `POST /auth/register`

**Body**:
```json
{
  "email": "scolarite@university.com",
  "password": "password123",
  "full_name": "Service Scolarité",
  "matricule": "SCO001",
  "fonction": "Gestionnaire de scolarité"
}
```

**Explication**: Crée un compte pour le personnel de scolarité. Le type sera `etudiant` par défaut, mais on peut le changer après création.

**Modifier le type**:
```bash
curl -X PUT "http://localhost:8000/users/ID_SCO" \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"type":"sco"}'
```

---

## 📊 Tests de Validation

### Test 27: Erreurs de Validation

**Test 1 - Email invalide**:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "email_invalide",
    "password": "password123",
    "full_name": "Test"
  }'
```
**Attendu**: 422 Validation Error

**Test 2 - Mot de passe trop court**:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "123",
    "full_name": "Test"
  }'
```
**Attendu**: 422 Validation Error

**Test 3 - Champ manquant**:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com"}'
```
**Attendu**: 422 Validation Error

**Explication**: Pydantic valide automatiquement tous les champs selon les schémas définis.

---

### Test 28: Ressource Non Trouvée

**Endpoint**: `GET /users/999999`

**Réponse attendue (404 Not Found)**:
```json
{
  "detail": "User not found"
}
```

**Explication**: Gestion propre des erreurs 404 pour les ressources inexistantes.

---

## 🔍 Tests de Debugging

### Test 29: Voir les logs du serveur

**Explication**: 
- Ouvrez le terminal où `uvicorn` est lancé
- Vous verrez les logs de toutes les requêtes HTTP
- Les erreurs apparaissent en rouge

**Exemple de log**:
```
INFO:     127.0.0.1:XXXXX - "POST /auth/login HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "GET /users/me HTTP/1.1" 200 OK
ERROR:    Invalid token
WARNING:  User not found
```

---

### Test 30: Vérifier la Base de Données

**Option 1 - Via Python**:
```python
python
>>> from database import SessionLocal
>>> from models import User, Document
>>> db = SessionLocal()
>>> users = db.query(User).all()
>>> print([u.email for u in users])
>>> db.close()
```

**Option 2 - Via pgAdmin**:
- Connectez-vous à PostgreSQL avec pgAdmin
- Naviguez vers `student_documents_db`
- Visualisez les tables et données

---

## 📋 Checklist de Test

### Authentification
- [ ] API accessible
- [ ] Inscription fonctionne
- [ ] Compte inactif ne peut pas se connecter
- [ ] Login admin fonctionne
- [ ] Login étudiant fonctionne
- [ ] Token JWT valide
- [ ] Token expire après délai

### Utilisateurs
- [ ] Admin voit tous les utilisateurs
- [ ] Admin voit les utilisateurs en attente
- [ ] Activation de compte fonctionne
- [ ] Étudiant ne peut pas voir tous les users
- [ ] Soft delete fonctionne

### Documents
- [ ] Création de demande(s)
- [ ] Étudiant voit ses demandes
- [ ] Admin voit toutes les demandes
- [ ] Changement de statut fonctionne
- [ ] Refus d'accès non autorisé
- [ ] Suppression fonctionne

### WebSocket
- [ ] Connexion établie
- [ ] Ping/Pong fonctionne
- [ ] Notifications reçues
- [ ] Notification validation compte
- [ ] Notification changement statut

### Sécurité
- [ ] Accès sans token refusé
- [ ] Token invalide refusé
- [ ] Permissions respectées
- [ ] Validation des données

---

## 🎯 Résultats Attendus

### ✅ Tous les tests passent
Votre API est **entièrement fonctionnelle** et prête pour la production !

### ⚠️ Certains tests échouent
1. Consultez les logs du serveur
2. Vérifiez les erreurs de la base de données
3. Assurez-vous que les tokens sont valides
4. Vérifiez que les permissions sont correctes

### ❌ Beaucoup de tests échouent
1. Vérifiez que la base de données est initialisée : `python init_db.py`
2. Vérifiez les imports : `python -c "from main import app"`
3. Vérifiez les variables d'environnement : `.env` correctement configuré
4. Consultez `CORRECTIONS_APPLIQUEES.md` pour les corrections

---

## 🆘 Dépannage

### Erreur: "Cannot import name 'DocumentRequest'"
**Solution**: Les imports ont été corrigés. Vérifiez que vous avez les dernières versions des fichiers.

### Erreur: "Relation does not exist"
**Solution**: Exécutez `python init_db.py` pour créer les tables.

### Erreur: "Authentication failed"
**Solution**: Vérifiez que vous utilisez les bons identifiants (admin@example.com / admin123)

### Erreur: "Not enough permissions"
**Solution**: Utilisez un token admin pour les actions admin.

### WebSocket ne fonctionne pas
**Solution**: 
- Vérifiez que vous utilisez `ws://` et non `http://`
- Utilisez l'ID utilisateur (pas le matricule)
- Vérifiez que le serveur est démarré

---

## 📚 Ressources Utiles

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **README.md**: Guide principal
- **POSTMAN_GUIDE.md**: Guide spécifique Postman
- **comprehension.md**: Compréhension du projet
- **CORRECTIONS_APPLIQUEES.md**: Log des corrections

---

**✅ Bon courage pour vos tests ! 🚀**

