#!/bin/bash

# Script pour configurer PostgreSQL automatiquement

echo "🔧 Configuration PostgreSQL pour le projet"
echo "=========================================="
echo ""

# Vérifier si la base existe déjà
DB_EXISTS=$(sudo -u postgres psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw student_documents_db && echo "yes" || echo "no")

if [ "$DB_EXISTS" = "yes" ]; then
    echo "✅ La base de données 'student_documents_db' existe déjà"
else
    echo "📦 Création de la base de données..."
    sudo -u postgres psql -c "CREATE DATABASE student_documents_db;" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Base de données créée avec succès"
    else
        echo "❌ Erreur lors de la création de la base de données"
        echo "💡 Vous devrez peut-être créer la base manuellement :"
        echo "   sudo -u postgres psql"
        echo "   CREATE DATABASE student_documents_db;"
        exit 1
    fi
fi

echo ""
echo "📝 Maintenant, configurez votre fichier .env avec les informations suivantes :"
echo ""
echo "1. DATABASE_URL : postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/student_documents_db"
echo "2. SECRET_KEY : Utilisez la clé générée précédemment"
echo ""
echo "Pour obtenir le mot de passe PostgreSQL de l'utilisateur postgres,"
echo "vous pouvez le réinitialiser avec :"
echo "   sudo -u postgres psql -c \"ALTER USER postgres WITH PASSWORD 'nouveau_mot_de_passe';\""
echo ""

