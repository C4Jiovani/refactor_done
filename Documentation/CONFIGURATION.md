# 📋 Guide de Configuration PostgreSQL et .env

## Étape 1 : Configurer PostgreSQL

### 1.1 Se connecter à PostgreSQL

Par défaut, PostgreSQL utilise l'utilisateur `postgres`. Connectez-vous :

```bash
sudo -u postgres psql
```

Ou si vous avez un utilisateur PostgreSQL configuré :
```bash
psql -U votre_utilisateur
```

### 1.2 Créer la base de données

Une fois connecté à PostgreSQL, exécutez :

```sql
CREATE DATABASE student_documents_db;
```

Pour vérifier que la base a été créée :
```sql
\l
```

Vous devriez voir `student_documents_db` dans la liste.

### 1.3 Créer un utilisateur (optionnel mais recommandé)

Pour des raisons de sécurité, créez un utilisateur dédié :

```sql
CREATE USER student_admin WITH PASSWORD 'votre_mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE student_documents_db TO student_admin;
\q
```

**Note :** Si vous préférez utiliser l'utilisateur `postgres` par défaut, vous pouvez sauter cette étape.

## Étape 2 : Créer le fichier .env

### 2.1 Copier le fichier d'exemple

```bash
cp env_example.txt .env
```

### 2.2 Modifier le fichier .env

Ouvrez le fichier `.env` avec votre éditeur de texte préféré :

```bash
nano .env
# ou
gedit .env
# ou
code .env  # si vous utilisez VS Code
```

### 2.3 Configurer les variables

Modifiez les valeurs selon votre configuration :

#### Configuration de la base de données

**Si vous utilisez l'utilisateur `postgres` par défaut :**
```env
DATABASE_URL=postgresql://postgres:votre_mot_de_passe@localhost:5432/student_documents_db
```

**Si vous avez créé un utilisateur dédié :**
```env
DATABASE_URL=postgresql://student_admin:votre_mot_de_passe_securise@localhost:5432/student_documents_db
```

**Format général :**
```
postgresql://[utilisateur]:[mot_de_passe]@[hôte]:[port]/[nom_base]
```

#### Clé secrète JWT

Générez une clé secrète sécurisée. Vous pouvez utiliser Python :

```python
import secrets
print(secrets.token_urlsafe(32))
```

Ou utilisez cette commande :
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Remplacez `SECRET_KEY` dans le `.env` par la clé générée.

#### Configuration Admin

Les identifiants admin par défaut sont :
```env
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

Vous pouvez les changer si vous le souhaitez.

### Exemple de fichier .env complet :

```env
# Database
DATABASE_URL=postgresql://postgres:mon_mot_de_passe@localhost:5432/student_documents_db

# JWT
SECRET_KEY=MaCléSecrèteTrèsLongueEtAléatoirePourLaProduction123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin (pour créer le premier admin)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

## Étape 3 : Vérifier la configuration

### 3.1 Tester la connexion à la base de données

```bash
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
db_url = os.getenv('DATABASE_URL')
print('✅ DATABASE_URL configurée:', db_url[:50] + '...')
"
```

### 3.2 Initialiser la base de données

Une fois le `.env` configuré, initialisez la base :

```bash
python3 init_db.py
```

Cela devrait :
- Créer les tables nécessaires
- Créer un utilisateur admin

## 🔧 Dépannage

### Problème : "password authentication failed"

**Solution :** Vérifiez :
1. Le mot de passe dans `DATABASE_URL` est correct
2. L'utilisateur PostgreSQL existe
3. Les permissions sont correctes

Pour réinitialiser le mot de passe PostgreSQL :
```bash
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD 'nouveau_mot_de_passe';
```

### Problème : "database does not exist"

**Solution :** Créez la base de données :
```bash
sudo -u postgres createdb student_documents_db
```

### Problème : "permission denied"

**Solution :** Vérifiez les permissions :
```sql
GRANT ALL PRIVILEGES ON DATABASE student_documents_db TO votre_utilisateur;
```

### Vérifier que PostgreSQL écoute sur le bon port

```bash
sudo netstat -tulpn | grep postgres
```

Par défaut, PostgreSQL écoute sur le port 5432.

