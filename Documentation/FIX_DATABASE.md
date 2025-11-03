# 🔧 Guide de Réparation Rapide - Erreur Base de Données

## 🐛 Problème Courant

Si vous obtenez cette erreur:
```
sqlalchemy.exc.ProgrammingError: column "user_id" of relation "document" does not exist
```

**Cause**: Votre base de données a été créée avec d'anciens modèles et la structure ne correspond plus aux nouveaux modèles.

---

## ✅ Solution Rapide

### Option 1: Réinitialisation Automatique (Recommandé)

```bash
# Étape 1: Réinitialiser la base de données
python reset_database.py

# Répondez "oui" quand demandé

# Étape 2: Initialiser avec les données de base
python init_db.py

# Étape 3: Relancer l'application
uvicorn main:app --reload
```

**⏱️ Temps**: 30 secondes

### Option 2: Réinitialisation Manuelle

```bash
# Se connecter à PostgreSQL
psql -U votre_username -d student_documents_db

# Dans psql, exécuter:
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;
\q

# Retour au terminal
python init_db.py
```

---

## 🔍 Vérifier que c'est Résolu

### Test Rapide

```bash
# Terminal 1: Démarrer l'application
uvicorn main:app --reload

# Terminal 2: Tester une connexion
curl http://localhost:8000/

# Si vous obtenez: {"message":"API Gestion Documents Étudiants",...}
# ✅ Tout fonctionne!
```

### Test Complet

```bash
# Exécuter tous les tests
./test_api.sh
```

Si tous les tests passent ✅ → Problème résolu !

---

## 📋 Checklist de Diagnostic

| Symptôme | Cause Probable | Solution |
|----------|---------------|----------|
| `column "user_id" does not exist` | Ancienne structure DB | `python reset_database.py` |
| `table "users" already exists` | Conflict de schéma | `python reset_database.py` |
| `relation "document" does not exist` | Tables non créées | `python init_db.py` |
| `duplicate key value` | Données déjà existantes | Vérifier avant réinitialisation |

---

## ⚠️ Important

### Sauvegarder vos Données (si nécessaire)

Si vous avez des données importantes dans l'ancienne base:

```bash
# Sauvegarder
pg_dump -U votre_username student_documents_db > backup_avant_migration.sql

# Après migration, restaurer si besoin
psql -U votre_username student_documents_db < backup_avant_migration.sql
```

**Note**: Si vous restaurez, vous devrez adapter les données aux nouveaux schémas.

---

## 🔄 Quand Faire Une Réinitialisation

### ✅ À faire:
- Après avoir modifié les modèles SQLAlchemy
- Lors d'erreurs de colonnes manquantes
- En développement (pas en production)
- Si la structure DB est inconsistance

### ❌ À ne pas faire:
- En production avec données importantes
- Sans sauvegarde préalable
- Si vous n'avez pas modifié les modèles

---

## 🚀 Workflow Recommandé

### Développement Normal

```bash
# 1. Modifier models.py

# 2. Réinitialiser la DB
python reset_database.py  # Répondre "oui"

# 3. Réinitialiser les données de base
python init_db.py

# 4. Tester
./test_api.sh

# 5. Continuer le développement
uvicorn main:app --reload
```

### Après Erreur de Migration

```bash
# 1. Arrêter le serveur (Ctrl+C)

# 2. Réinitialiser
python reset_database.py

# 3. Réinitialiser les données
python init_db.py

# 4. Relancer
uvicorn main:app --reload

# 5. Tester
curl http://localhost:8000/
```

---

## 🆘 Autres Erreurs Possibles

### Erreur: "Cannot connect to database"

```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql

# Si non démarré:
sudo systemctl start postgresql
```

### Erreur: "database does not exist"

```bash
# Créer la base de données
createdb -U votre_username student_documents_db

# Ou via psql:
psql -U postgres
CREATE DATABASE student_documents_db;
\q
```

### Erreur: "permission denied"

```bash
# Vérifier les permissions dans .env
# S'assurer que l'utilisateur a les droits

# Ou créer un utilisateur dédié:
createuser -U postgres votre_utilisateur
createdb -U postgres -O votre_utilisateur student_documents_db
```

---

## 📞 Support

Si le problème persiste:

1. ✅ Vérifiez que PostgreSQL est démarré
2. ✅ Vérifiez le fichier `.env` (DATABASE_URL)
3. ✅ Consultez les logs: Terminal où `uvicorn` tourne
4. ✅ Vérifiez les imports: `python -c "from models import User, Document"`
5. ✅ Vérifiez la structure: `python init_db.py`

---

## 🎯 Résumé en Une Ligne

**Problème de colonne manquante ?** → `python reset_database.py` puis `python init_db.py` ✅

