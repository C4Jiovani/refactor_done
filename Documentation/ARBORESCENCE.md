# Arborescence du Projet - Gestion Documents Académiques

```
Projet Fin d'année Backend/
│
├── 📄 Fichiers Principaux
│   ├── main.py                      # Point d'entrée FastAPI avec toutes les routes
│   ├── models.py                    # Modèles SQLAlchemy (User, Document, etc.)
│   ├── schemas.py                   # Schémas Pydantic pour validation
│   ├── database.py                  # Configuration de la base de données
│   ├── auth.py                      # Authentification JWT
│   ├── crud.py                      # Opérations CRUD sur la base
│   ├── websocket_manager.py         # Gestion des connexions WebSocket
│   └── init_db.py                   # Script d'initialisation de la BDD
│
├── 📚 Documentation
│   ├── README.md                    # Guide principal du projet
│   ├── QUICKSTART.md                # Démarrage rapide
│   ├── comprehension.md             # Compréhension du projet (NOUVEAU)
│   ├── CORRECTIONS_APPLIQUEES.md    # Log des corrections (NOUVEAU)
│   ├── DATABASE_SCHEMA.md           # Schéma de la base de données
│   ├── POSTMAN_GUIDE.md             # Guide d'utilisation avec Postman
│   ├── CONFIGURATION.md             # Configuration de l'environnement
│   ├── SETUP_STEPS.md               # Étapes d'installation
│   ├── TEST_APP.md                  # Guide de test
│   ├── FIX_ENV_INSTRUCTIONS.md      # Instructions pour corriger l'environnement
│   ├── INSTALL_PGADMIN.md           # Installation de pgAdmin
│   └── RESUME_PGADMIN.md            # Résumé pgAdmin
│
├── 🔧 Configuration
│   ├── requirements.txt             # Dépendances Python
│   ├── env_example.txt              # Exemple de fichier .env
│   ├── setup_postgres.sh            # Script de configuration PostgreSQL
│   ├── fix_env.sh                   # Script de correction env
│   └── start.sh                     # Script de démarrage
│
└── 📂 Autres
    ├── __pycache__/                 # Fichiers Python compilés
    └── VF/                          # Dossier (contenu non spécifié)
```

## 📋 Description des Fichiers Principaux

### `main.py`
- Point d'entrée de l'application FastAPI
- Toutes les routes API (auth, users, requests)
- Configuration CORS
- Gestion WebSocket

### `models.py`
- **User** : Utilisateurs (admin/etudiant/sco) avec matricule
- **Document** : Demandes de documents académiques
- **Niveau** : Niveaux d'études (Licence, Master, etc.)
- **AnneeUniv** : Années universitaires
- **Categori** : Catégories de documents (Relevé, Attestation, etc.)
- **Notification** : Notifications pour les utilisateurs

### `schemas.py`
- Schémas Pydantic pour validation des données
- UserBase, UserCreate, UserResponse, UserUpdate
- DocumentRequest (alias Document)
- LoginRequest, Token

### `database.py`
- Configuration SQLAlchemy
- Session de base de données
- URL de connexion PostgreSQL

### `auth.py`
- Authentification JWT
- Hash des mots de passe
- Vérification des tokens
- Dépendances pour admin/user

### `crud.py`
- Opérations Create, Read, Update, Delete
- CRUD User (create, get, update, delete)
- CRUD Document (create, get_all, update, delete)
- Soft delete pour User

### `websocket_manager.py`
- Gestion des connexions WebSocket
- Envoi de notifications temps réel
- Broadcast aux administrateurs

### `init_db.py`
- Création des tables
- Initialisation de l'admin par défaut
- Création des catégories de documents

## 🗄️ Base de Données

### Tables Principales
1. **users** - Utilisateurs du système
2. **document** - Demandes de documents
3. **niveau** - Niveaux académiques
4. **annee_univ** - Années universitaires
5. **categori** - Catégories de documents
6. **notification** - Notifications utilisateurs

### Relations
```
User 1---N Document
User 1---N Notification
Niveau 1---N Document
AnneeUniv 1---N Document
Categori 1---N Document
Document 1---N Notification
```

## 🚀 Lancement du Projet

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer la base de données
python init_db.py

# 3. Lancer l'application
uvicorn main:app --reload

# Accéder à la documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## 📦 Dépendances Principales

- **fastapi** : Framework web moderne
- **sqlalchemy** : ORM pour PostgreSQL
- **pydantic** : Validation des données
- **python-jose** : JWT
- **passlib** : Hash des mots de passe
- **uvicorn** : Serveur ASGI
- **websockets** : Support WebSocket
- **psycopg2-binary** : Driver PostgreSQL

## 🔐 Identifiants par Défaut

- **Email** : admin@example.com
- **Mot de passe** : admin123
- **Matricule** : ADMIN001

## 📞 Endpoints Principaux

### Authentification
- `POST /auth/register` - Inscription
- `POST /auth/login` - Connexion

### Utilisateurs
- `GET /users/me` - Profil utilisateur
- `GET /users` - Liste des utilisateurs (admin)
- `PUT /users/{id}` - Modifier un utilisateur (admin)

### Documents
- `POST /requests` - Créer une demande
- `GET /requests` - Liste des demandes
- `PUT /requests/{id}` - Modifier une demande (admin)

### WebSocket
- `WS /ws/{user_id}` - Connexion WebSocket

## 🎯 Fonctionnalités

✅ Authentification JWT
✅ Gestion multi-rôles (admin/etudiant/sco)
✅ Demandes de documents multiples
✅ Notifications temps réel (WebSocket)
✅ Soft delete
✅ Validation par admin
✅ Suivi des paiements
✅ Documentation automatique (Swagger)

