# 📊 Installation pgAdmin4 Web - Guide Complet

## ✅ État Actuel de Votre Système

### PostgreSQL
- ✅ **Installé** : PostgreSQL 14.15 (Ubuntu)
- ✅ **Service actif** : PostgreSQL est en cours d'exécution
- ✅ **Prêt à l'emploi**

### pgAdmin4
- ❌ **Non installé** : pgAdmin4 (version web) n'est pas présent sur votre système

---

## 🔧 Installation de pgAdmin4 Web

### Méthode Recommandée : Installation via le dépôt officiel

pgAdmin4 peut être installé de plusieurs façons sur Ubuntu/ZorinOS. Voici la méthode la plus simple et recommandée :

### Étape 1 : Ajouter le dépôt officiel pgAdmin

```bash
sudo curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
```

```bash
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'
```

### Étape 2 : Mettre à jour les dépôts

```bash
sudo apt update
```

### Étape 3 : Installer pgAdmin4 (version web)

```bash
sudo apt install pgadmin4-web
```

**Note** : Il y a aussi `pgadmin4-desktop` pour une version avec interface graphique, mais pour votre cas, la version web (`pgadmin4-web`) est suffisante.

### Étape 4 : Exécuter le script de configuration

Après l'installation, vous devez configurer pgAdmin4 web. Exécutez cette commande :

```bash
sudo /usr/pgadmin4/bin/setup-web.sh
```

Ce script va :
1. Vous demander l'adresse email pour le compte administrateur
2. Vous demander un mot de passe pour ce compte
3. Configurer le serveur web (Apache/Nginx)
4. Générer un fichier de configuration

### Étape 5 : Démarrer le service

```bash
sudo systemctl enable pgadmin4
sudo systemctl start pgadmin4
```

**OU** si vous utilisez Apache :

```bash
sudo systemctl enable apache2
sudo systemctl start apache2
```

---

## 🌐 Accéder à pgAdmin4 via le Navigateur

### URL d'accès locale

Une fois configuré, accédez à pgAdmin4 via :

```
http://localhost/pgadmin4
```

**OU**

```
http://127.0.0.1/pgadmin4
```

### Première connexion

1. **Ouvrez votre navigateur** et allez à `http://localhost/pgadmin4`

2. **Page de connexion** : Utilisez les identifiants que vous avez créés lors de l'exécution de `setup-web.sh` :
   - **Email** : L'email que vous avez entré
   - **Password** : Le mot de passe que vous avez défini

3. **Premier lancement** : pgAdmin4 vous demandera peut-être de définir une "Master Password" pour protéger les mots de passe sauvegardés. C'est optionnel mais recommandé.

---

## 🔗 Connexion à PostgreSQL depuis pgAdmin4

Une fois connecté à pgAdmin4, pour vous connecter à votre base de données PostgreSQL :

### Étape 1 : Ajouter un serveur

1. **Clic droit** sur "Servers" dans le panneau de gauche
2. Sélectionnez **"Register" > "Server..."**

### Étape 2 : Onglet "General"

- **Name** : `Local PostgreSQL` (ou un nom de votre choix)

### Étape 3 : Onglet "Connection"

- **Host name/address** : `localhost` (ou `127.0.0.1`)
- **Port** : `5432` (port par défaut PostgreSQL)
- **Maintenance database** : `postgres`
- **Username** : `postgres`
- **Password** : Votre mot de passe PostgreSQL (le même que dans votre `.env`)

**Optionnel** : Cochez "Save password" pour ne pas avoir à le ressaisir.

### Étape 4 : Connexion

Cliquez sur **"Save"**. pgAdmin4 devrait maintenant se connecter à PostgreSQL.

---

## 📋 Vérification de l'Installation

Après installation, vérifiez que tout fonctionne :

```bash
# Vérifier que pgAdmin4 est installé
dpkg -l | grep pgadmin

# Vérifier le statut du service
sudo systemctl status pgadmin4

# OU si Apache est utilisé
sudo systemctl status apache2
```

---

## 🔍 Alternative : Installation via Snap (Plus Simple)

Si la méthode ci-dessus pose problème, vous pouvez utiliser Snap :

```bash
# Installer via snap
sudo snap install pgadmin4

# L'URL sera différente : http://localhost:5050
```

---

## ⚠️ Dépannage

### Si vous ne pouvez pas accéder à http://localhost/pgadmin4

1. **Vérifiez que le service est actif** :
   ```bash
   sudo systemctl status pgadmin4
   sudo systemctl status apache2
   ```

2. **Vérifiez les logs** :
   ```bash
   sudo journalctl -u pgadmin4 -f
   ```

3. **Vérifiez le port** :
   ```bash
   sudo netstat -tulpn | grep pgadmin
   ```

### Si le script setup-web.sh n'existe pas

Parfois, pgAdmin4 s'installe dans un répertoire différent. Cherchez-le :

```bash
find /usr -name setup-web.sh 2>/dev/null
find /opt -name setup-web.sh 2>/dev/null
```

---

## 📝 Résumé des Commandes

Voici toutes les commandes dans l'ordre :

```bash
# 1. Ajouter le dépôt
sudo curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'

# 2. Mettre à jour
sudo apt update

# 3. Installer
sudo apt install pgadmin4-web

# 4. Configurer
sudo /usr/pgadmin4/bin/setup-web.sh

# 5. Démarrer les services
sudo systemctl enable pgadmin4
sudo systemctl start pgadmin4
sudo systemctl enable apache2
sudo systemctl start apache2

# 6. Accéder via navigateur
# http://localhost/pgadmin4
```

---

**Une fois installé, vous pourrez gérer facilement votre base de données `student_documents_db` via l'interface web de pgAdmin4 !** 🎉

