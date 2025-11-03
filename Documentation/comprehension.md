# Compréhension du Projet - Gestion de Documents Académiques

## 📋 Vue d'ensemble

Le projet consiste en un **système de gestion de documents académiques** pour une université. Il permet aux étudiants de demander des documents administratifs (relevés de notes, attestations, certificats) en ligne, avec un processus de validation par les administrateurs et un système de notifications en temps réel.

## 🎯 Objectif principal

Numériser et automatiser le processus de demande et de délivrance de documents académiques, en assurant :
- Le suivi des demandes
- La gestion des paiements
- La communication avec les utilisateurs via des notifications
- Le contrôle d'accès basé sur les rôles

## 🏗️ Architecture du système

### 1. **Gestion des Utilisateurs (USER)**
- **Types d'utilisateurs** : `admin`, `etudiant`, `sco` (personnel de scolarité)
- **Identification** : `matricule` unique + informations personnelles
- **État** : `is_active` (compte validé), `is_deleted` (soft delete)
- **Association** : Lié à un `Niveau` et une `Annee_univ`
- **Rôle** : Gestion des droits d'accès et des permissions

### 2. **Gestion des Niveaux d'Études (Niveau)**
- Définit les différents niveaux académiques (Licence 1, Master, etc.)
- **Attribut** : `designation` (nom du niveau)
- **Clé primaire** : `matricule` (à corriger → devrait être `id` ou `code`)

### 3. **Gestion des Années Universitaires (Annee_univ)**
- Représente les années académiques (ex: "2024-2025")
- **Attribut** : `annee` (identifiant unique)

### 4. **Gestion des Catégories de Documents (Categori)**
- Définit les types de documents disponibles avec leurs coûts
- **Types disponibles** :
  - RELEVER DE NOTE (2000AR)
  - ATTESTATION DE REUSSITE (3000AR)
  - CERTIFICAT DE FIN D'ETUDE (3000AR)
- **Attributs** :
  - `designation` : Nom du document
  - `montant` : Coût associé
  - `contenu_notif` : Modèle de notification pour cette catégorie

### 5. **Processus de Demande de Documents (Document)**
- Les utilisateurs créent des demandes de documents
- **États** : `pending` → `validate` / `refused`
- **Attributs** :
  - `numero` : Numéro unique du document
  - `date_de_demande` : Date de création
  - `date_de_validation` : Date d'approbation
  - `status` : État actuel
  - `est_paye` : Indicateur de paiement
- **Associations** : 
  - Utilisateur demandeur
  - Niveau d'études
  - Année universitaire
  - Catégorie de document

### 6. **Système de Notifications (Notification)**
- Alertes temps réel pour informer les utilisateurs
- **Déclencheurs** :
  - Validation de compte
  - Changement de statut d'une demande
  - Nouveau document disponible
- **Attributs** :
  - `date_de_notification` : Horodatage
  - `vue` : Lecture ou non
  - `contenu` : Message de la notification

## 🔄 Workflow du système

### Pour un Étudiant
1. **Inscription** → Création de compte (inactif par défaut)
2. **Attente de validation** → Admin valide le compte
3. **Connexion** → Authentification JWT
4. **Demande de document** → Sélection du type de document
5. **Paiement** → Vérification du paiement
6. **Suivi** → Notifications de changement de statut
7. **Réception** → Document validé et prêt

### Pour un Admin
1. **Validation des comptes** → Activer les nouveaux utilisateurs
2. **Consultation des demandes** → Vue d'ensemble des demandes
3. **Traitement** → Validation ou refus des demandes
4. **Gestion** → Modification des statuts et notifications

## 📊 Flux de données

```
[Étudiant] → Demande → [Document] → Validation [Admin]
     ↓                           ↓
[Notification WebSocket] ← [Status Change]
```

## 🔍 Problèmes identifiés dans le code actuel

### ❌ Erreurs d'importation
- `DocumentRequest` n'existe pas dans `models.py` mais est importé dans `main.py`
- Le modèle s'appelle `Document` dans `models.py`

### ⚠️ Incohérences avec le schéma fourni
1. **Modèle USER** :
   - ❌ Manque `matricule` (utilise `id` à la place)
   - ❌ Manque `type` (admin/etudiant/sco)
   - ❌ Manque `fonction`
   - ✅ `is_active` présent
   - ❌ Manque `is_deleted`

2. **Modèle Niveau** :
   - ❌ Clé primaire `matricule` au lieu de `id` ou `code`
   - ✅ `designation` présent

3. **Modèle Document** :
   - ✅ Bonne structure de base
   - ❌ Attributs `pere` et `mere` semblent étranges (peut-être pour stocker info des parents ?)
   - ✅ `status`, `est_paye` présents
   - ⚠️ Relations correctes mais à vérifier

4. **Modèle Notification** :
   - ✅ Structure conforme
   - ✅ Relations correctes

5. **Modèle Categori** :
   - ✅ Structure conforme
   - ✅ `contenu_notif` présent

6. **CRUD** :
   - ❌ Utilise `DocumentRequest` au lieu de `Document`
   - ❌ Utilise `RequestStatus` qui n'existe pas

## 🎯 Solution proposée

### Corrections à apporter
1. **Renommer/Adapter** : `Document` doit remplacer `DocumentRequest` partout
2. **Créer les énumérations manquantes** : `RequestStatus`, adapter `UserRole`
3. **Ajouter les champs manquants** : `matricule`, `type`, `fonction`, `is_deleted` dans `User`
4. **Corriger la PK de Niveau** : Utiliser `id` au lieu de `matricule`
5. **Clarifier** les attributs `pere` et `mere` dans `Document`
6. **Standardiser les schémas Pydantic** pour correspondre aux modèles
7. **Mettre à jour les CRUD** pour utiliser les bons modèles

## 📝 Points d'attention

### Design Decisions
- **Soft Delete** : `is_deleted` permet de garder l'historique
- **Double validation** : Inscription + Activation par admin pour sécurité
- **WebSocket** : Notifications temps réel pour meilleure UX
- **JWT** : Authentification stateless et scalable
- **Paiement** : `est_paye` pour tracking, peut être étendu avec intégration système de paiement

### Sécurité
- ✅ Comptes inactifs par défaut
- ✅ Validation admin obligatoire
- ✅ JWT avec expiration
- ✅ Hash des mots de passe
- ⚠️ À améliorer : Rate limiting, validation côté serveur renforcée

### Évolutivité
- Architecture modulaire
- Séparation des responsabilités (models, schemas, crud)
- WebSocket pour notifications push
- PostgreSQL pour robustesse

## 🚀 Prochaines étapes

1. ✅ Créer ce document de compréhension
2. ⏳ Corriger tous les imports et modèles
3. ⏳ Ajouter les champs manquants
4. ⏳ Adapter les schémas Pydantic
5. ⏳ Mettre à jour les opérations CRUD
6. ⏳ Tester toutes les routes
7. ⏳ Documenter les changements

