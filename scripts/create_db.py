from sqlalchemy import create_engine
from db.models import Base

if __name__ == "__main__":
    engine = create_engine("sqlite:///db.sqlite3")
    Base.metadata.create_all(engine)
