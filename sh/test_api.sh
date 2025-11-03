#!/bin/bash

# Script de Test Automatisé pour l'API Gestion Documents Académiques
# Usage: ./test_api.sh

BASE_URL="http://localhost:8000"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="admin123"
STUDENT_EMAIL="etudiant.test@example.com"
STUDENT_PASSWORD="password123"

echo "🧪 Script de Test Automatisé pour l'API"
echo "========================================"
echo ""

# Couleurs pour les résultats
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Test 1: Vérifier que l'API est accessible
echo "Test 1: Vérification que l'API est accessible..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ $RESPONSE -eq 200 ]; then
    test_result 0 "API accessible"
else
    test_result 1 "API non accessible (HTTP $RESPONSE)"
    echo "⚠️  Assurez-vous que le serveur est démarré avec: uvicorn app.main:app --reload"
    exit 1
fi
echo ""

# Test 2: Connexion Admin
echo "Test 2: Connexion en tant qu'administrateur..."
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$ADMIN_TOKEN" ] || [ "$ADMIN_TOKEN" == "None" ]; then
    test_result 1 "Échec de la connexion admin"
    echo "⚠️  Vérifiez que la base de données est initialisée avec: python init_db.py"
    exit 1
else
    test_result 0 "Connexion admin réussie"
    echo "   Token obtenu: ${ADMIN_TOKEN:0:50}..."
fi
echo ""

# Test 3: Inscription d'un étudiant
echo "Test 3: Inscription d'un nouvel étudiant..."
REGISTER_RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\":\"$STUDENT_EMAIL\",
    \"password\":\"$STUDENT_PASSWORD\",
    \"full_name\":\"Test Étudiant\",
    \"matricule\":\"ETU_TEST001\"
  }")

HTTP_CODE="${REGISTER_RESPONSE: -3}"
if [ $HTTP_CODE -eq 201 ]; then
    test_result 0 "Inscription réussie"
    STUDENT_ID=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
    echo "   ID étudiant: $STUDENT_ID"
else
    test_result 1 "Échec de l'inscription (HTTP $HTTP_CODE)"
    echo "$REGISTER_RESPONSE"
fi
echo ""

# Test 4: Connexion impossible avec compte inactif
echo "Test 4: Tentative de connexion avec compte inactif..."
INACTIVE_LOGIN=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$STUDENT_EMAIL\",\"password\":\"$STUDENT_PASSWORD\"}")

HTTP_CODE="${INACTIVE_LOGIN: -3}"
if [ $HTTP_CODE -eq 403 ]; then
    test_result 0 "Compte inactif correctement bloqué (HTTP 403)"
else
    test_result 1 "Le compte inactif devrait être bloqué (HTTP $HTTP_CODE)"
fi
echo ""

# Test 5: Activation du compte
echo "Test 5: Activation du compte étudiant..."
ACTIVATE_RESPONSE=$(curl -s -w "%{http_code}" -X PUT "$BASE_URL/users/$STUDENT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active":true}')

HTTP_CODE="${ACTIVATE_RESPONSE: -3}"
if [ $HTTP_CODE -eq 200 ]; then
    test_result 0 "Compte activé avec succès"
else
    test_result 1 "Échec de l'activation (HTTP $HTTP_CODE)"
fi
echo ""

# Test 6: Connexion maintenant possible
echo "Test 6: Connexion avec le compte maintenant actif..."
STUDENT_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$STUDENT_EMAIL\",\"password\":\"$STUDENT_PASSWORD\"}" | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$STUDENT_TOKEN" ] || [ "$STUDENT_TOKEN" == "None" ]; then
    test_result 1 "Échec de la connexion étudiant"
else
    test_result 0 "Connexion étudiant réussie"
fi
echo ""

# Test 7: Créer une demande de document
echo "Test 7: Création d'une demande de document..."
REQUEST_RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/requests" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_types":["RELEVER DE NOTE"]}')

HTTP_CODE="${REQUEST_RESPONSE: -3}"
if [ $HTTP_CODE -eq 201 ]; then
    test_result 0 "Demande créée avec succès"
    REQUEST_ID=$(echo "$REQUEST_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if isinstance(data, list) else data.get('id', ''))")
    echo "   ID demande: $REQUEST_ID"
else
    test_result 1 "Échec de la création (HTTP $HTTP_CODE)"
    echo "$REQUEST_RESPONSE"
fi
echo ""

# Test 8: Récupérer les demandes
echo "Test 8: Récupération des demandes de l'étudiant..."
REQUESTS_RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/requests" \
  -H "Authorization: Bearer $STUDENT_TOKEN")

HTTP_CODE="${REQUESTS_RESPONSE: -3}"
if [ $HTTP_CODE -eq 200 ]; then
    test_result 0 "Récupération des demandes réussie"
    REQUEST_COUNT=$(echo "$REQUESTS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)) if isinstance(json.load(sys.stdin), list) else 0)")
    echo "   Nombre de demandes: $REQUEST_COUNT"
else
    test_result 1 "Échec de la récupération (HTTP $HTTP_CODE)"
fi
echo ""

# Test 9: Validation de la demande par admin
echo "Test 9: Validation de la demande par l'admin..."
VALIDATE_RESPONSE=$(curl -s -w "%{http_code}" -X PUT "$BASE_URL/requests/$REQUEST_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"validate"}')

HTTP_CODE="${VALIDATE_RESPONSE: -3}"
if [ $HTTP_CODE -eq 200 ]; then
    test_result 0 "Demande validée avec succès"
else
    test_result 1 "Échec de la validation (HTTP $HTTP_CODE)"
fi
echo ""

# Test 10: Accès refusé pour étudiant
echo "Test 10: Tentative de modification par un étudiant (non autorisée)..."
FORBIDDEN_RESPONSE=$(curl -s -w "%{http_code}" -X PUT "$BASE_URL/requests/$REQUEST_ID" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"validate"}')

HTTP_CODE="${FORBIDDEN_RESPONSE: -3}"
if [ $HTTP_CODE -eq 403 ]; then
    test_result 0 "Accès refusé correctement (HTTP 403)"
else
    test_result 1 "L'accès devrait être refusé (HTTP $HTTP_CODE)"
fi
echo ""

# Test 11: Récupérer tous les utilisateurs (admin)
echo "Test 11: Récupération de tous les utilisateurs par l'admin..."
ALL_USERS_RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

HTTP_CODE="${ALL_USERS_RESPONSE: -3}"
if [ $HTTP_CODE -eq 200 ]; then
    test_result 0 "Récupération réussie"
    USER_COUNT=$(echo "$ALL_USERS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)) if isinstance(json.load(sys.stdin), list) else 0)")
    echo "   Nombre d'utilisateurs: $USER_COUNT"
else
    test_result 1 "Échec de la récupération (HTTP $HTTP_CODE)"
fi
echo ""

# Test 12: Accès refusé pour étudiant
echo "Test 12: Tentative d'accès aux utilisateurs par un étudiant..."
FORBIDDEN_USERS=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/users" \
  -H "Authorization: Bearer $STUDENT_TOKEN")

HTTP_CODE="${FORBIDDEN_USERS: -3}"
if [ $HTTP_CODE -eq 403 ]; then
    test_result 0 "Accès refusé correctement (HTTP 403)"
else
    test_result 1 "L'accès devrait être refusé (HTTP $HTTP_CODE)"
fi
echo ""

# Test 13: Vérifier le profil utilisateur
echo "Test 13: Récupération du profil utilisateur..."
PROFILE_RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/users/me" \
  -H "Authorization: Bearer $STUDENT_TOKEN")

HTTP_CODE="${PROFILE_RESPONSE: -3}"
if [ $HTTP_CODE -eq 200 ]; then
    test_result 0 "Profil récupéré avec succès"
    EMAIL=$(echo "$PROFILE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('email', ''))")
    echo "   Email: $EMAIL"
else
    test_result 1 "Échec de la récupération (HTTP $HTTP_CODE)"
fi
echo ""

# Test 14: Vérifier l'accès sans token
echo "Test 14: Tentative d'accès sans token..."
NO_TOKEN_RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/users/me")

HTTP_CODE="${NO_TOKEN_RESPONSE: -3}"
if [ $HTTP_CODE -eq 401 ]; then
    test_result 0 "Accès sans token correctement refusé (HTTP 401)"
else
    test_result 1 "L'accès devrait être refusé (HTTP $HTTP_CODE)"
fi
echo ""

# Résumé
echo "========================================"
echo "📊 Résumé des Tests"
echo "========================================"
echo ""
echo "✅ Tests réussis"
echo "❌ Tests échoués"
echo "⚠️  Vérifiez les logs ci-dessus pour les détails"
echo ""
echo "📝 Pour plus de détails, consultez TEST_COMPLET.md"
echo ""

# Nettoyage optionnel (décommentez pour nettoyer)
# echo "Nettoyage des données de test..."
# curl -s -X DELETE "$BASE_URL/users/$STUDENT_ID" \
#   -H "Authorization: Bearer $ADMIN_TOKEN"

