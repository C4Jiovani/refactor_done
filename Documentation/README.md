# API Gestion Documents Étudiants - Backend

Backend FastAPI pour la gestion des demandes de documents administratifs pour étudiants.

## 🚀 Fonctionnalités

- ✅ Authentification JWT avec rôles (user/admin)
- ✅ Inscription avec validation par admin
- ✅ Gestion des demandes de documents (création multiple)
- ✅ Notifications en temps réel via WebSocket
- ✅ Documentation automatique Swagger
- ✅ Gestion d'erreurs complète

## 📋 Prérequis

- Python 3.8+
- PostgreSQL 12+
- pip

## 🛠️ Installation

1. **Cloner le projet** (si applicable)

2. **Créer un environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données PostgreSQL**

Créer une base de données PostgreSQL :
```sql
CREATE DATABASE student_documents_db;
```

5. **Configurer les variables d'environnement**

Créer un fichier `.env` à la racine du projet :
```env
DATABASE_URL=postgresql://user:password@localhost:5432/student_documents_db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

6. **Initialiser la base de données**
```bash
python init_db.py
```

Cela créera les tables et un utilisateur admin par défaut.

## 🏃 Lancer l'application

```bash
uvicorn main:app --reload
```

L'API sera accessible sur `http://localhost:8000`

## 📚 Documentation API

Une fois l'application lancée, accédez à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🧪 Tester avec Postman

### 1. Inscription d'un utilisateur

**POST** `/auth/register`
```json
{
  "email": "etudiant@example.com",
  "full_name": "Jean Dupont",
  "password": "motdepasse123"
}
```

### 2. Connexion (Admin)

**POST** `/auth/login`
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

Réponse :
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 3. Valider un compte utilisateur (Admin)

**PUT** `/users/{user_id}`
Headers : `Authorization: Bearer {token}`
```json
{
  "is_active": true
}
```

### 4. Créer des demandes de documents

**POST** `/requests`
Headers : `Authorization: Bearer {token}`
```json
{
  "document_types": [
    "certificat de scolarité",
    "relevé de notes"
  ]
}
```

### 5. Voir toutes les demandes

**GET** `/requests`
Headers : `Authorization: Bearer {token}`

### 6. Modifier le statut d'une demande (Admin)

**PUT** `/requests/{request_id}`
Headers : `Authorization: Bearer {token}`
```json
{
  "status": "validée"
}
```

Statuts possibles : `"en attente"`, `"en cours"`, `"validée"`, `"refusée"`

### 7. WebSocket pour notifications

**Connexion WebSocket** : `ws://localhost:8000/ws/{user_id}`

Les notifications sont envoyées automatiquement quand :
- Un compte est validé/refusé
- Le statut d'une demande change

## 📁 Structure du projet

```
.
├── main.py                 # Point d'entrée FastAPI avec toutes les routes
├── models.py              # Modèles SQLAlchemy
├── schemas.py             # Schémas Pydantic
├── database.py            # Configuration base de données
├── auth.py                # Authentification JWT
├── crud.py                # Opérations CRUD
├── websocket_manager.py   # Gestionnaire WebSocket
├── init_db.py             # Script d'initialisation
├── requirements.txt        # Dépendances Python
└── README.md              # Ce fichier
```

## 🔐 Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification.

**Comment utiliser les tokens :**
1. Appeler `/auth/login` pour obtenir un token
2. Inclure le token dans les requêtes suivantes :
   ```
   Authorization: Bearer {token}
   ```

**Rôles :**
- `user` : Utilisateur standard (étudiant)
- `admin` : Administrateur (peut gérer utilisateurs et demandes)

## 📡 WebSocket

Les notifications en temps réel sont disponibles via WebSocket.

**Connexion :**
```
ws://localhost:8000/ws/{user_id}
```

**Types de notifications :**
- `account_validated` : Compte validé par admin
- `account_rejected` : Compte refusé
- `request_status_changed` : Statut d'une demande modifié

**Format des notifications :**
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

## 🔧 Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | URL de connexion PostgreSQL | - |
| `SECRET_KEY` | Clé secrète pour JWT | - |
| `ALGORITHM` | Algorithme JWT | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de validité du token | 30 |
| `ADMIN_EMAIL` | Email de l'admin par défaut | admin@example.com |
| `ADMIN_PASSWORD` | Mot de passe de l'admin | admin123 |

## 🐛 Gestion des erreurs

L'API retourne des codes HTTP standards :
- `200` : Succès
- `201` : Créé
- `400` : Requête invalide
- `401` : Non authentifié
- `403` : Non autorisé
- `404` : Ressource non trouvée
- `500` : Erreur serveur

## 📝 Notes

- Par défaut, les nouveaux comptes sont **inactifs** et doivent être validés par un admin
- Un utilisateur ne peut voir que ses propres demandes (sauf admin)
- Les admins peuvent voir et modifier toutes les demandes
- Les notifications WebSocket nécessitent une connexion active

## 🤝 Contribution

Ce projet est développé dans le cadre d'un projet de fin d'année.

## 📄 License

Ce projet est à usage éducatif.

