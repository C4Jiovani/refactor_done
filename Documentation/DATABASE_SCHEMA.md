# 📊 Schéma de Base de Données

## 📋 Résumé

**Nombre total de tables :** `2`

- `users` - Table des utilisateurs (étudiants et administrateurs)
- `document_requests` - Table des demandes de documents

---

## 🗂️ Structure des Tables

### 📌 Table 1 : `users`

**Description :** Stocke les informations des utilisateurs du système (étudiants et administrateurs).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | `Integer` | PRIMARY KEY, INDEX | Identifiant unique de l'utilisateur |
| `email` | `String` | UNIQUE, INDEX, NOT NULL | Adresse email de l'utilisateur (utilisée pour la connexion) |
| `hashed_password` | `String` | NOT NULL | Mot de passe hashé (bcrypt) |
| `full_name` | `String` | NOT NULL | Nom complet de l'utilisateur |
| `is_active` | `Boolean` | NOT NULL, DEFAULT: `false` | Statut d'activation du compte (désactivé par défaut) |
| `role` | `String` | NOT NULL, DEFAULT: `"user"` | Rôle de l'utilisateur : `"user"` ou `"admin"` |
| `created_at` | `DateTime(timezone=True)` | DEFAULT: `now()` | Date et heure de création du compte |

**Index :**
- Index sur `id` (clé primaire)
- Index unique sur `email`

**Valeurs par défaut :**
- `is_active` : `false` (les comptes doivent être validés par un admin)
- `role` : `"user"`
- `created_at` : Date/heure actuelle lors de la création

---

### 📌 Table 2 : `document_requests`

**Description :** Stocke les demandes de documents administratifs créées par les utilisateurs.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | `Integer` | PRIMARY KEY, INDEX | Identifiant unique de la demande |
| `user_id` | `Integer` | FOREIGN KEY → `users.id`, NOT NULL | Référence à l'utilisateur qui a créé la demande |
| `document_type` | `String` | NOT NULL | Type de document demandé (ex: "certificat de scolarité") |
| `status` | `String` | NOT NULL, DEFAULT: `"en attente"` | Statut de la demande |
| `created_at` | `DateTime(timezone=True)` | DEFAULT: `now()` | Date et heure de création de la demande |
| `updated_at` | `DateTime(timezone=True)` | ON UPDATE: `now()` | Date et heure de dernière mise à jour |

**Index :**
- Index sur `id` (clé primaire)

**Clé étrangère :**
- `user_id` → `users.id` (relation Many-to-One)

**Statuts possibles :**
- `"en attente"` (par défaut)
- `"en cours"`
- `"validée"`
- `"refusée"`

**Types de documents possibles :**
- `"certificat de scolarité"`
- `"relevé de notes"`
- `"attestation d'inscription"`
- `"autre"`

---

## 🔗 Relations entre les Tables

### Relation : `users` ↔ `document_requests`

```
┌─────────────────┐                    ┌──────────────────────┐
│     users       │                    │  document_requests    │
├─────────────────┤                    ├──────────────────────┤
│ id (PK)         │◄───────────────────┤ user_id (FK)         │
│ email           │    1:N              │ id (PK)              │
│ hashed_password │   (One-to-Many)    │ document_type         │
│ full_name       │                    │ status                │
│ is_active       │                    │ created_at            │
│ role            │                    │ updated_at            │
│ created_at     │                    │                       │
└─────────────────┘                    └──────────────────────┘
```

**Description de la relation :**
- **Type** : One-to-Many (Un-à-plusieurs)
- **Côté `users`** : Un utilisateur peut avoir plusieurs demandes de documents
- **Côté `document_requests`** : Chaque demande appartient à un seul utilisateur

**Implémentation SQLAlchemy :**
- Dans `User` : `document_requests = relationship("DocumentRequest", back_populates="user")`
- Dans `DocumentRequest` : 
  - `user_id = Column(Integer, ForeignKey("users.id"))`
  - `user = relationship("User", back_populates="document_requests")`

---

## 📐 Diagramme Entité-Relation (ER) Complet

```
┌─────────────────────────────────────────────────────────────┐
│                         BASE DE DONNÉES                     │
│                   student_documents_db                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────┐
│           TABLE: users              │
├──────────────────────────────────────┤
│                                      │
│  ┌────────────┐                     │
│  │ id (PK)    │                     │
│  └────────────┘                     │
│                                      │
│  ┌────────────┐                     │
│  │ email      │ UNIQUE, INDEX      │
│  └────────────┘                     │
│                                      │
│  ┌──────────────────┐               │
│  │ hashed_password  │               │
│  └──────────────────┘               │
│                                      │
│  ┌──────────────┐                   │
│  │ full_name    │                   │
│  └──────────────┘                   │
│                                      │
│  ┌──────────────┐                   │
│  │ is_active    │ DEFAULT: false    │
│  └──────────────┘                   │
│                                      │
│  ┌──────────────┐                   │
│  │ role         │ DEFAULT: "user"   │
│  └──────────────┘                   │
│                                      │
│  ┌──────────────┐                   │
│  │ created_at   │ DEFAULT: now()    │
│  └──────────────┘                   │
│                                      │
│          │                           │
│          │ 1                         │
│          │                           │
│          │                           │
│          ▼                           │
│                                      │
└──────────────────────────────────────┘
                │
                │ One-to-Many
                │ (1 utilisateur → N demandes)
                │
                │
                ▼
┌──────────────────────────────────────┐
│      TABLE: document_requests        │
├──────────────────────────────────────┤
│                                      │
│  ┌────────────┐                     │
│  │ id (PK)    │                     │
│  └────────────┘                     │
│                                      │
│  ┌────────────┐                     │
│  │ user_id    │ ────► FK ────► users│
│  └────────────┘                     │
│                                      │
│  ┌──────────────────┐               │
│  │ document_type    │               │
│  └──────────────────┘               │
│                                      │
│  ┌──────────────┐                   │
│  │ status       │ DEFAULT: "en      │
│  │              │          attente" │
│  └──────────────┘                   │
│                                      │
│  ┌──────────────┐                   │
│  │ created_at   │ DEFAULT: now()    │
│  └──────────────┘                   │
│                                      │
│  ┌──────────────┐                   │
│  │ updated_at   │ ON UPDATE: now()  │
│  └──────────────┘                   │
│                                      │
└──────────────────────────────────────┘
```

---

## 🔍 Exemples de Données

### Exemple 1 : Utilisateur (Admin)

```sql
INSERT INTO users (id, email, hashed_password, full_name, is_active, role, created_at)
VALUES (
    1,
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Gy1rKWyXzO9m',  -- hash de "admin123"
    'Administrateur',
    true,
    'admin',
    '2024-01-15 10:00:00+00'
);
```

### Exemple 2 : Utilisateur (Étudiant)

```sql
INSERT INTO users (id, email, hashed_password, full_name, is_active, role, created_at)
VALUES (
    2,
    'etudiant@example.com',
    '$2b$12$abcdefghijklmnopqrstuvwxyz123456789',  -- hash du mot de passe
    'Jean Dupont',
    true,  -- Validé par un admin
    'user',
    '2024-01-15 11:00:00+00'
);
```

### Exemple 3 : Demande de Document

```sql
INSERT INTO document_requests (id, user_id, document_type, status, created_at, updated_at)
VALUES (
    1,
    2,  -- Référence à l'utilisateur avec id=2
    'certificat de scolarité',
    'en attente',
    '2024-01-15 12:00:00+00',
    NULL
);
```

### Exemple 4 : Demande Validée

```sql
INSERT INTO document_requests (id, user_id, document_type, status, created_at, updated_at)
VALUES (
    2,
    2,  -- Même utilisateur
    'relevé de notes',
    'validée',
    '2024-01-15 12:30:00+00',
    '2024-01-15 14:00:00+00'  -- Mis à jour lors de la validation
);
```

---

## 📊 Statistiques et Contraintes

### Contraintes d'intégrité

1. **Clé primaire** :
   - `users.id` : Identifiant unique pour chaque utilisateur
   - `document_requests.id` : Identifiant unique pour chaque demande

2. **Clé étrangère** :
   - `document_requests.user_id` → `users.id`
   - Contrainte : `ON DELETE` (comportement par défaut SQLAlchemy)

3. **Contraintes d'unicité** :
   - `users.email` : Un seul compte par adresse email

4. **Contraintes NOT NULL** :
   - Tous les champs sont obligatoires sauf `updated_at` dans `document_requests`

### Index

- `users.id` : Index automatique (clé primaire)
- `users.email` : Index unique (recherche rapide par email)
- `document_requests.id` : Index automatique (clé primaire)

---

## 🔄 Flux de Données Typique

```
1. Création d'un utilisateur (user)
   └─► is_active = false (compte inactif)

2. Validation par un admin
   └─► is_active = true (compte activé)

3. L'utilisateur crée des demandes (document_requests)
   └─► user_id référence l'utilisateur
   └─► status = "en attente"

4. L'admin modifie le statut
   └─► status = "en cours" ou "validée" ou "refusée"
   └─► updated_at est mis à jour automatiquement
```

---

## 📝 Notes Importantes

1. **Sécurité** : Les mots de passe sont stockés sous forme de hash (bcrypt), jamais en clair
2. **Validation** : Les nouveaux comptes sont inactifs par défaut et doivent être validés par un admin
3. **Cascade** : Si un utilisateur est supprimé, ses demandes peuvent être supprimées aussi (selon la configuration)
4. **Timezones** : Toutes les dates sont stockées avec timezone pour éviter les problèmes de fuseaux horaires
5. **Soft Delete** : Actuellement, la suppression est physique. Pour un environnement de production, envisager un soft delete avec un champ `deleted_at`

---

**Total : 2 tables principales avec 1 relation One-to-Many**

