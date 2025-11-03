from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, UserRole, Categori
from app.auth import get_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    """Crée les tables, un admin par défaut et les catégories de documents"""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Vérifier si un admin existe déjà
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if not existing_admin:
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            admin = User(
                matricule="ADMIN001",
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                nom="Administrateur",
                prenom="Système",
                is_active=True,
                type=UserRole.ADMIN.value,
                fonction="Administrateur Principal"
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin créé avec succès!")
            print(f"   Matricule: ADMIN001")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
        else:
            print("ℹ️  Un administrateur existe déjà")
        
        # Créer les catégories de documents
        categories = [
            {
                "designation": "RELEVER DE NOTE",
                "montant": 2000.0,
                "contenu_notif": "Votre relevé de notes est prêt et disponible."
            },
            {
                "designation": "ATTESTATION DE REUSSITE",
                "montant": 3000.0,
                "contenu_notif": "Votre attestation de réussite est prête et disponible."
            },
            {
                "designation": "CERTIFICAT DE FIN D'ETUDE",
                "montant": 3000.0,
                "contenu_notif": "Votre certificat de fin d'étude est prêt et disponible."
            }
        ]
        
        created_count = 0
        for cat_data in categories:
            existing_cat = db.query(Categori).filter(
                Categori.designation == cat_data["designation"]
            ).first()
            
            if not existing_cat:
                categorie = Categori(**cat_data)
                db.add(categorie)
                created_count += 1
        
        if created_count > 0:
            db.commit()
            print(f"✅ {created_count} catégorie(s) de document créée(s)")
        else:
            print("ℹ️  Les catégories de documents existent déjà")
        
        print("\n🎉 Initialisation de la base de données terminée!")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_db()


