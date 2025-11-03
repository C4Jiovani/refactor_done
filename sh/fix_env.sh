#!/bin/bash

# Script pour corriger le fichier .env

echo "🔧 Correction du fichier .env..."

# Sauvegarder l'ancien fichier
cp .env .env.backup 2>/dev/null

# Corriger la ligne DATABASE_URL en supprimant la duplication
sed -i 's/^DATABASE_URL=DATABASE_URL=/DATABASE_URL=/' .env

echo "✅ Fichier .env corrigé!"
echo ""
echo "📋 Vérification du contenu :"
echo ""
grep "^DATABASE_URL=" .env

echo ""
echo "💡 Si le mot de passe est tronqué (contient '...'), vous devrez le remplacer manuellement."

