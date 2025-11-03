# 🧪 Guide de Test - API Gestion Documents Académiques

## 🎯 Démarrage Rapide

Vous avez **3 façons** de tester l'API :

### 1️⃣ **Swagger UI (Le plus simple !)** ⭐

```bash
# 1. Démarrer l'application
uvicorn main:app --reload

# 2. Ouvrir dans le navigateur
http://localhost:8000/docs
```

✅ **Pourquoi Swagger ?**
- Interface graphique interactive
- Pas besoin d'installer d'autres outils
- Documentation intégrée
- Test direct dans le navigateur

📖 **Guide détaillé** : `GUIDE_TEST_MANUEL.md`

---

### 2️⃣ **Script Automatique** 🤖

```bash
# Exécuter tous les tests en une fois
./test_api.sh
```

✅ **Avantages :**
- Tests automatiques complets
- Résultat rapide
- Parfait pour la CI/CD

📖 **14 tests automatiques** en quelques secondes !

---

### 3️⃣ **Tests Manuels Détaillés** 📝

Pour tester **chacun des 30 endpoints** en détail :

📖 **Guide complet** : `TEST_COMPLET.md`

---

## 📚 Fichiers de Documentation

| Fichier | Description | Quand l'utiliser |
|---------|-------------|------------------|
| **TEST_COMPLET.md** | Guide complet avec 30 tests détaillés | Pour tester tout en profondeur |
| **GUIDE_TEST_MANUEL.md** | Démarrage rapide avec Swagger/Postman | Pour commencer rapidement |
| **test_api.sh** | Script de test automatique | Pour valider rapidement |
| **README_TEST.md** | Ce fichier (vue d'ensemble) | Pour savoir quoi utiliser |

---

## 🚀 Tests Minimum à Faire

**Pour vérifier que l'API fonctionne**, testez au minimum :

1. ✅ API accessible : `GET /` → 200 OK
2. ✅ Login Admin : `POST /auth/login` → Token reçu
3. ✅ Register Étudiant : `POST /auth/register` → Compte créé
4. ✅ Activer Compte : `PUT /users/{id}` → 200 OK
5. ✅ Login Étudiant : `POST /auth/login` → Token reçu
6. ✅ Créer Demande : `POST /requests` → Demande créée
7. ✅ Lister Demandes : `GET /requests` → Liste affichée
8. ✅ Valider Demande : `PUT /requests/{id}` → Statut changé

**Si ces 8 tests passent** → 🎉 Votre API fonctionne !

---

## 📋 Statistiques des Tests

### TEST_COMPLET.md contient :

- **🔐 5 Tests d'Authentification**
- **👥 8 Tests Utilisateurs**
- **📄 9 Tests Documents**
- **🌐 3 Tests WebSocket**
- **🧪 5 Tests d'Intégration**

**Total : 30 tests** couvrant toutes les fonctionnalités !

---

## 🎓 Recommandation d'Apprentissage

### Pour débuter :
1. ✅ Ouvrez `GUIDE_TEST_MANUEL.md`
2. ✅ Testez avec Swagger UI
3. ✅ Suivez les 8 tests minimum ci-dessus

### Pour approfondir :
1. ✅ Ouvrez `TEST_COMPLET.md`
2. ✅ Suivez les 30 tests détaillés
3. ✅ Comprenez chaque explication

### Pour valider rapidement :
1. ✅ Exécutez `./test_api.sh`
2. ✅ Vérifiez les résultats

---

## 🔧 Prérequis

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Initialiser la base de données
python init_db.py

# 3. Démarrer l'application
uvicorn main:app --reload
```

---

## 📞 Endpoints Principaux

### Authentification
- `POST /auth/register` - Inscription
- `POST /auth/login` - Connexion
- `GET /users/me` - Mon profil

### Utilisateurs (Admin)
- `GET /users` - Liste des utilisateurs
- `GET /users/pending` - Utilisateurs en attente
- `PUT /users/{id}` - Modifier un utilisateur

### Documents
- `POST /requests` - Créer une demande
- `GET /requests` - Liste des demandes
- `PUT /requests/{id}` - Modifier une demande
- `DELETE /requests/{id}` - Supprimer une demande

### WebSocket
- `WS /ws/{user_id}` - Connexion WebSocket

---

## 🔐 Identifiants de Test

### Administrateur par défaut
```
Email: admin@example.com
Password: admin123
Matricule: ADMIN001
```

### Étudiant à créer
```
Email: etudiant@example.com
Password: password123
Matricule: Auto-généré (STUXXXXXX)
```

---

## ⚡ Workflow de Test Rapide

```bash
# Terminal 1: Démarrer le serveur
uvicorn main:app --reload

# Terminal 2: Exécuter les tests
./test_api.sh

# Terminal 3: Connecter WebSocket (optionnel)
wscat -c ws://localhost:8000/ws/2
```

**Temps total : < 2 minutes** ⏱️

---

## 🐛 Résolution de Problèmes

### API ne démarre pas
```bash
# Vérifier les erreurs
python -c "from main import app"
python init_db.py
```

### Tests échouent
```bash
# Réinitialiser la base
python init_db.py

# Relancer les tests
./test_api.sh
```

### WebSocket ne fonctionne pas
```bash
# Vérifier wscat installé
npm install -g wscat

# Se connecter
wscat -c ws://localhost:8000/ws/2
```

---

## 📖 Documentation Complémentaire

- **README.md** - Guide principal du projet
- **comprehension.md** - Compréhension du projet
- **CORRECTIONS_APPLIQUEES.md** - Historique des corrections
- **ARBORESCENCE.md** - Structure du projet
- **POSTMAN_GUIDE.md** - Guide Postman spécifique

---

## ✅ Checklist Finale

Avant de considérer les tests comme complets :

### Fonctionnalités de Base
- [ ] Authentification fonctionne
- [ ] Les rôles sont respectés (admin/etudiant)
- [ ] Les comptes inactifs sont bloqués
- [ ] Création de demandes fonctionne
- [ ] Validation de demandes fonctionne

### Sécurité
- [ ] Accès sans token refusé
- [ ] Token invalide refusé
- [ ] Permissions respectées
- [ ] Validation des données

### WebSocket
- [ ] Connexion établie
- [ ] Notifications reçues
- [ ] Ping/Pong fonctionne

### Cas d'Usage Réels
- [ ] Workflow complet testé
- [ ] Erreurs gérées correctement
- [ ] Messages clairs

**Si tous ces tests passent** → 🎉 **API prête pour la production !**

---

## 🎯 Prochaines Étapes

Après avoir testé l'API :

1. ✅ Consulter la documentation Swagger
2. ✅ Tester avec un frontend (si disponible)
3. ✅ Configurer l'environnement de production
4. ✅ Mettre en place les tests unitaires
5. ✅ Ajouter des tests d'intégration continus

---

**Bon courage pour vos tests ! 🚀**

Pour toute question, consultez les fichiers de documentation détaillés listés ci-dessus.

