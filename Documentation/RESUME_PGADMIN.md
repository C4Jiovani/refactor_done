# 📋 Résumé : Installation pgAdmin4 Web

## ✅ État Actuel

- **PostgreSQL** : ✅ Installé (version 14.15) et actif
- **pgAdmin4** : ❌ Non installé

## 🚀 Installation pgAdmin4 Web (Méthode Simple)

### Option 1 : Via Dépôt Officiel (Recommandé)

```bash
# 1. Ajouter le dépôt
sudo curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'

# 2. Mettre à jour et installer
sudo apt update
sudo apt install pgadmin4-web

# 3. Configurer (créera votre compte admin)
sudo /usr/pgadmin4/bin/setup-web.sh

# 4. Démarrer
sudo systemctl enable pgadmin4
sudo systemctl start pgadmin4
sudo systemctl enable apache2
sudo systemctl start apache2
```

### Option 2 : Via Snap (Plus Simple)

```bash
sudo snap install pgadmin4
```

## 🌐 Accès Web

### Via Dépôt (Apache)
- **URL** : `http://localhost/pgadmin4`

### Via Snap
- **URL** : `http://localhost:5050`

## 🔐 Connexion

### 1. Connexion à pgAdmin4
- Utilisez l'**email** et le **mot de passe** définis lors de `setup-web.sh`

### 2. Ajouter votre serveur PostgreSQL
- **Host** : `localhost`
- **Port** : `5432`
- **Database** : `postgres`
- **Username** : `postgres`
- **Password** : Votre mot de passe PostgreSQL (celui de votre `.env`)

---

**Consultez `INSTALL_PGADMIN.md` pour les détails complets.**

