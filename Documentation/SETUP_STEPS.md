# 🚀 Étapes de Configuration - Guide Rapide

## ✅ Étape 1 : Fichier .env créé
Le fichier `.env` a été créé avec succès !

## 📝 Étape 2 : Modifier le fichier .env

Ouvrez le fichier `.env` et modifiez la ligne `DATABASE_URL` :

```bash
nano .env
```

**Trouvez cette ligne :**
```
DATABASE_URL=postgresql://user:password@localhost:5432/student_documents_db
```

**Remplacez-la par :**
```
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/student_documents_db
```

⚠️ **Important :** Remplacez `VOTRE_MOT_DE_PASSE` par le mot de passe de l'utilisateur PostgreSQL `postgres`.

### Comment obtenir/réinitialiser le mot de passe PostgreSQL ?

Si vous ne connaissez pas le mot de passe, exécutez :

```bash
sudo -u postgres psql
```

Puis dans PostgreSQL :
```sql
ALTER USER postgres WITH PASSWORD 'nouveau_mot_de_passe';
\q
```

Remplacez `nouveau_mot_de_passe` par le mot de passe que vous souhaitez utiliser.

## 🗄️ Étape 3 : Créer la base de données PostgreSQL

Exécutez cette commande (vous devrez entrer votre mot de passe sudo) :

```bash
sudo -u postgres psql -c "CREATE DATABASE student_documents_db;"
```

**OU** connectez-vous à PostgreSQL et créez la base manuellement :

```bash
sudo -u postgres psql
```

Puis dans PostgreSQL :
```sql
CREATE DATABASE student_documents_db;
\q
```

Pour vérifier que la base a été créée :
```bash
sudo -u postgres psql -l | grep student_documents_db
```

## ✅ Étape 4 : Vérifier la configuration

Vérifiez que votre fichier `.env` contient bien :
- ✅ `DATABASE_URL` avec le bon mot de passe
- ✅ `SECRET_KEY` avec la clé générée
- ✅ Les autres valeurs configurées

## 🎯 Étape 5 : Initialiser la base de données

Une fois PostgreSQL configuré et le `.env` mis à jour, initialisez la base :

```bash
python3 init_db.py
```

Cette commande va :
- Créer toutes les tables nécessaires
- Créer un utilisateur admin (email: admin@example.com, password: admin123)

## 🚀 Étape 6 : Lancer l'application

```bash
uvicorn main:app --reload
```

Ou utilisez le script :
```bash
./start.sh
```

Accédez ensuite à :
- API : http://localhost:8000
- Documentation : http://localhost:8000/docs

---

## 🔍 Dépannage Rapide

### Erreur : "password authentication failed"
→ Vérifiez que le mot de passe dans `DATABASE_URL` est correct

### Erreur : "database does not exist"
→ Créez la base de données avec la commande de l'Étape 3

### Erreur : "permission denied"
→ Vérifiez que l'utilisateur PostgreSQL a les bonnes permissions

