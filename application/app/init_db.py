from app.database import Base, engine
from app.models import Order


def initialize_database():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    initialize_database()
    print("Database tables initialized.")