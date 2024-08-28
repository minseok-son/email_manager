from config.database import Base, engine

def create_tables():
    """
    Creates all database tables defined in the application.
    """
    Base.metadata.create_all(bind=engine)