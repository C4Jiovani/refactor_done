# 🚀 Démarrage Rapide

## Installation en 5 minutes

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Configurer PostgreSQL
Créez une base de données PostgreSQL :
```sql
CREATE DATABASE student_documents_db;
```

### 3. Créer le fichier .env
```bash
cp env_example.txt .env
```
Puis modifiez `.env` avec vos informations de connexion PostgreSQL.

### 4. Initialiser la base de données
```bash
python init_db.py
```

Cela créera :
- Les tables de la base de données
- Un utilisateur admin (email: `admin@example.com`, password: `admin123`)

### 5. Lancer l'application
```bash
uvicorn main:app --reload
```

Ou utiliser le script :
```bash
./start.sh
```

### 6. Accéder à l'API
- **API** : http://localhost:8000
- **Documentation Swagger** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## Premier test avec Postman

1. **Inscrire un étudiant**
   - POST `http://localhost:8000/auth/register`
   - Body: `{"email": "etudiant@test.com", "full_name": "Test User", "password": "test123"}`

2. **Se connecter en admin**
   - POST `http://localhost:8000/auth/login`
   - Body: `{"email": "admin@example.com", "password": "admin123"}`
   - Copier le `access_token`

3. **Valider le compte étudiant**
   - PUT `http://localhost:8000/users/1`
   - Header: `Authorization: Bearer {token}`
   - Body: `{"is_active": true}`

4. **Se connecter en étudiant**
   - POST `http://localhost:8000/auth/login`
   - Body: `{"email": "etudiant@test.com", "password": "test123"}`
   - Copier le `access_token`

5. **Créer des demandes**
   - POST `http://localhost:8000/requests`
   - Header: `Authorization: Bearer {student_token}`
   - Body: `{"document_types": ["certificat de scolarité", "relevé de notes"]}`

## WebSocket - Notifications

Pour tester les notifications en temps réel :

1. Ouvrez Postman et créez une connexion WebSocket
2. URL: `ws://localhost:8000/ws/1` (remplacez 1 par l'ID de l'utilisateur)
3. Connectez-vous
4. Changez le statut d'une demande via l'API
5. Vous recevrez une notification en temps réel !

## 📚 Documentation complète

Consultez `README.md` et `POSTMAN_GUIDE.md` pour plus de détails.

