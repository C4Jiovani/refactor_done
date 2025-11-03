"""
Script pour réinitialiser complètement la base de données
Supprime toutes les tables et les recrée avec les nouveaux modèles
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/student_documents_db")

def reset_database():
    """Supprime toutes les tables et les recrée"""
    print("🔄 Réinitialisation de la base de données...")
    
    # Créer un moteur sans créer les tables automatiquement
    engine = create_engine(DATABASE_URL)
    
    try:
        # Supprimer toutes les tables existantes
        print("🗑️  Suppression des anciennes tables...")
        
        # Se connecter à la base de données
        with engine.connect() as conn:
            # Commencer une transaction
            trans = conn.begin()
            
            try:
                # Désactiver temporairement les vérifications de contraintes
                conn.execute(text("SET session_replication_role = 'replica';"))
                
                # Supprimer toutes les tables avec CASCADE pour gérer les dépendances
                Base.metadata.drop_all(bind=engine, checkfirst=True)
                
                # Réactiver les vérifications
                conn.execute(text("SET session_replication_role = 'origin';"))
                
                # Commit la transaction
                trans.commit()
                
            except Exception as drop_error:
                trans.rollback()
                # Si drop_all échoue, essayer une approche manuelle
                print("⚠️  Méthode automatique échouée, tentative manuelle...")
                with conn.begin() as trans2:
                    conn.execute(text("DROP SCHEMA public CASCADE;"))
                    conn.execute(text("CREATE SCHEMA public;"))
                    conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
                    trans2.commit()
        
        print("✅ Anciennes tables supprimées")
        
        # Créer les nouvelles tables avec la nouvelle structure
        print("🔨 Création des nouvelles tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Nouvelles tables créées")
        
        print("\n🎉 Base de données réinitialisée avec succès!")
        print("⚠️  Toutes les données ont été supprimées.")
        print("\n👉 Exécutez maintenant: python scripts/init_db.py")
        
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {e}")
        print("\n💡 Vérifiez:")
        print("   1. PostgreSQL est démarré")
        print("   2. La base de données existe")
        print("   3. Les identifiants dans .env sont corrects")

if __name__ == "__main__":
    response = input("⚠️  ATTENTION: Ce script va supprimer TOUTES les données!\nÊtes-vous sûr? (oui/non): ")
    if response.lower() in ['oui', 'yes', 'o', 'y']:
        reset_database()
    else:
        print("❌ Opération annulée")


