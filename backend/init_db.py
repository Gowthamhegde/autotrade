"""Initialize SQLite database with schema and demo user"""
from sqlalchemy import create_engine
from app.core.database import Base
from app.models import User, Wallet, Strategy, Model
from app.models.user import UserRole

# Create engine
engine = create_engine("sqlite:///./autotrader.db")

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Check if demo user exists
existing_user = db.query(User).filter(User.email == "admin@example.com").first()

if not existing_user:
    # Create demo user with bcrypt hashed password
    import bcrypt
    hashed_password = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8')
    demo_user = User(
        email="admin@example.com",
        name="Admin User",
        hashed_password=hashed_password,
        role=UserRole.ADMIN
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    # Create wallet for demo user
    wallet = Wallet(
        user_id=demo_user.id,
        total_balance=100000.0,
        reserved_balance=0.0,
        available_balance=100000.0
    )
    db.add(wallet)
    db.commit()
    
    print("✓ Database initialized with demo user")
    print("  Email: admin@example.com")
    print("  Password: admin123")
else:
    print("✓ Database already initialized")

db.close()
