# Guide Postman - API Gestion Documents Étudiants

Ce guide vous montre comment tester l'API avec Postman.

## 📋 Configuration initiale

### 1. Créer un environnement Postman

Créez un nouvel environnement avec les variables suivantes :
- `base_url` : `http://localhost:8000`
- `token` : (laissé vide, sera rempli après connexion)

### 2. Variables globales

Dans les variables de collection, vous pouvez définir :
- `admin_email` : `admin@example.com`
- `admin_password` : `admin123`

## 🔐 Authentification

### Étape 1 : Inscription d'un étudiant

**Méthode :** `POST`  
**URL :** `{{base_url}}/auth/register`  
**Body (JSON) :**
```json
{
  "email": "etudiant1@example.com",
  "full_name": "Marie Martin",
  "password": "password123"
}
```

**Réponse attendue :** 201 Created
```json
{
  "id": 1,
  "email": "etudiant1@example.com",
  "full_name": "Marie Martin",
  "is_active": false,
  "role": "user",
  "created_at": "2024-01-15T10:30:00"
}
```

### Étape 2 : Connexion Admin

**Méthode :** `POST`  
**URL :** `{{base_url}}/auth/login`  
**Body (JSON) :**
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

**Réponse attendue :**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Action Postman :** Créez un script de test pour enregistrer automatiquement le token :
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("token", jsonData.access_token);
}
```

### Étape 3 : Validation du compte étudiant (Admin)

**Méthode :** `PUT`  
**URL :** `{{base_url}}/users/1`  
**Headers :**
```
Authorization: Bearer {{token}}
Content-Type: application/json
```
**Body (JSON) :**
```json
{
  "is_active": true
}
```

**Réponse attendue :**
```json
{
  "id": 1,
  "email": "etudiant1@example.com",
  "full_name": "Marie Martin",
  "is_active": true,
  "role": "user",
  "created_at": "2024-01-15T10:30:00"
}
```

### Étape 4 : Connexion étudiant

**Méthode :** `POST`  
**URL :** `{{base_url}}/auth/login`  
**Body (JSON) :**
```json
{
  "email": "etudiant1@example.com",
  "password": "password123"
}
```

Enregistrez ce token dans une variable `student_token`.

## 📄 Gestion des demandes de documents

### Créer plusieurs demandes en une fois

**Méthode :** `POST`  
**URL :** `{{base_url}}/requests`  
**Headers :**
```
Authorization: Bearer {{student_token}}
Content-Type: application/json
```
**Body (JSON) :**
```json
{
  "document_types": [
    "certificat de scolarité",
    "relevé de notes",
    "attestation d'inscription"
  ]
}
```

**Réponse attendue :** 201 Created
```json
[
  {
    "id": 1,
    "user_id": 1,
    "document_type": "certificat de scolarité",
    "status": "en attente",
    "created_at": "2024-01-15T10:35:00",
    "updated_at": null
  },
  {
    "id": 2,
    "user_id": 1,
    "document_type": "relevé de notes",
    "status": "en attente",
    "created_at": "2024-01-15T10:35:00",
    "updated_at": null
  },
  {
    "id": 3,
    "user_id": 1,
    "document_type": "attestation d'inscription",
    "status": "en attente",
    "created_at": "2024-01-15T10:35:00",
    "updated_at": null
  }
]
```

### Voir toutes les demandes (étudiant)

**Méthode :** `GET`  
**URL :** `{{base_url}}/requests`  
**Headers :**
```
Authorization: Bearer {{student_token}}
```

### Voir toutes les demandes (admin)

**Méthode :** `GET`  
**URL :** `{{base_url}}/requests`  
**Headers :**
```
Authorization: Bearer {{token}}
```

### Modifier le statut d'une demande (Admin)

**Méthode :** `PUT`  
**URL :** `{{base_url}}/requests/1`  
**Headers :**
```
Authorization: Bearer {{token}}
Content-Type: application/json
```
**Body (JSON) :**
```json
{
  "status": "en cours"
}
```

**Statuts possibles :**
- `"en attente"`
- `"en cours"`
- `"validée"`
- `"refusée"`

### Supprimer une demande (Admin)

**Méthode :** `DELETE`  
**URL :** `{{base_url}}/requests/1`  
**Headers :**
```
Authorization: Bearer {{token}}
```

## 👥 Gestion des utilisateurs (Admin uniquement)

### Lister tous les utilisateurs

**Méthode :** `GET`  
**URL :** `{{base_url}}/users`  
**Headers :**
```
Authorization: Bearer {{token}}
```

### Voir les utilisateurs en attente

**Méthode :** `GET`  
**URL :** `{{base_url}}/users/pending`  
**Headers :**
```
Authorization: Bearer {{token}}
```

### Voir un utilisateur spécifique

**Méthode :** `GET`  
**URL :** `{{base_url}}/users/1`  
**Headers :**
```
Authorization: Bearer {{token}}
```

### Modifier un utilisateur

**Méthode :** `PUT`  
**URL :** `{{base_url}}/users/1`  
**Headers :**
```
Authorization: Bearer {{token}}
Content-Type: application/json
```
**Body (JSON) :**
```json
{
  "is_active": true,
  "full_name": "Marie Martin (Modifiée)"
}
```

### Supprimer un utilisateur

**Méthode :** `DELETE`  
**URL :** `{{base_url}}/users/1`  
**Headers :**
```
Authorization: Bearer {{token}}
```

## 🔔 WebSocket - Notifications en temps réel

Pour tester les WebSockets avec Postman :

1. Ouvrez un onglet WebSocket dans Postman
2. URL : `ws://localhost:8000/ws/1` (remplacez 1 par l'ID de l'utilisateur)
3. Connectez-vous

**Notifications reçues automatiquement :**
- Quand un compte est validé/refusé
- Quand le statut d'une demande change

**Format d'une notification :**
```json
{
  "type": "request_status_changed",
  "message": "Le statut de votre demande a changé: validée",
  "data": {
    "request_id": 1,
    "old_status": "en attente",
    "new_status": "validée",
    "document_type": "certificat de scolarité"
  }
}
```

## 🧪 Scénario de test complet

### 1. Inscription et validation
1. Inscrire un étudiant → `/auth/register`
2. Se connecter en admin → `/auth/login`
3. Voir les utilisateurs en attente → `/users/pending`
4. Valider l'étudiant → `PUT /users/{id}` avec `{"is_active": true}`

### 2. Création de demandes
1. Se connecter en étudiant → `/auth/login`
2. Créer des demandes → `POST /requests` avec plusieurs types
3. Voir ses demandes → `GET /requests`

### 3. Gestion par admin
1. Se connecter en admin → `/auth/login`
2. Voir toutes les demandes → `GET /requests`
3. Changer le statut → `PUT /requests/{id}` avec nouveau statut
4. Vérifier les notifications WebSocket

## ⚠️ Erreurs courantes

### 401 Unauthorized
- Vérifiez que le token est présent dans les headers
- Vérifiez que le token n'a pas expiré
- Vérifiez le format : `Authorization: Bearer {token}`

### 403 Forbidden
- L'utilisateur n'a pas les droits nécessaires (doit être admin)
- Le compte n'est pas actif (doit être validé par admin)

### 404 Not Found
- La ressource demandée n'existe pas
- Vérifiez l'ID dans l'URL

### 400 Bad Request
- Les données envoyées sont invalides
- Vérifiez le format JSON
- Vérifiez les champs requis

