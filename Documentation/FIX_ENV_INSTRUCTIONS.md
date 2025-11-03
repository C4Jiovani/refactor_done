# 🔧 Instructions pour Corriger le Fichier .env

## Problème détecté

Votre fichier `.env` avait une erreur de format (duplication de `DATABASE_URL`). C'est corrigé maintenant, mais le mot de passe semble incomplet.

## ✅ Étape 1 : Vérifier et compléter le mot de passe

Ouvrez le fichier `.env` :

```bash
nano .env
```

**Trouvez cette ligne :**
```
DATABASE_URL=postgresql://postgres:Helloworld00...@localhost:5432/student_documents_db
```

**Remplacez `Helloworld00...` par votre mot de passe PostgreSQL complet.**

Le format correct doit être :
```
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE_COMPLET@localhost:5432/student_documents_db
```

### Si vous ne connaissez pas le mot de passe PostgreSQL

1. Connectez-vous à PostgreSQL :
```bash
sudo -u postgres psql
```

2. Changez le mot de passe :
```sql
ALTER USER postgres WITH PASSWORD 'votre_nouveau_mot_de_passe';
\q
```

3. Utilisez ce mot de passe dans le fichier `.env`

## ✅ Étape 2 : Créer la base de données (si elle n'existe pas)

Vérifiez si la base existe :
```bash
sudo -u postgres psql -l | grep student_documents_db
```

Si elle n'existe pas, créez-la :
```bash
sudo -u postgres psql -c "CREATE DATABASE student_documents_db;"
```

## ✅ Étape 3 : Tester la connexion

Une fois le fichier `.env` corrigé, testez :

```bash
python3 init_db.py
```

Si tout fonctionne, vous verrez :
```
✅ Admin créé avec succès!
   Email: admin@example.com
   Password: admin123
```

## ⚠️ Points importants

1. **Le mot de passe ne doit PAS contenir de `...`** - il doit être complet
2. **Pas d'espaces** autour du `=` dans le fichier `.env`
3. **Pas de guillemets** autour de la valeur (sauf si nécessaire pour des caractères spéciaux)
4. Le format exact : `postgresql://utilisateur:mot_de_passe@localhost:5432/nom_base`

## 🔍 Format correct complet

Voici un exemple de fichier `.env` correct :

```env
# Database
DATABASE_URL=postgresql://postgres:mon_mot_de_passe@localhost:5432/student_documents_db

# JWT
SECRET_KEY=NZfzMJfkLOY8vsQvpsiPuEmrxAv-CzdQ09RJVv5XRok
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin (pour créer le premier admin)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

