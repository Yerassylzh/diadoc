from sqlalchemy import Integer, String, Column, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class PhysicalHealth(Base):
    __tablename__ = "physical_health"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    calories = Column(Integer)
    createdAt = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<PhysicalHealth(id={self.id}')>"


class MentalHealth(Base):
    __tablename__ = "mental_health"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    rating = Column(Integer)
    note = Column(Text)
    createdAt = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<MentalHealth(id={self.id}')>"


class Glucose(Base):
    __tablename__ = "glucose"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    value = Column(String)
    createdAt = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Glucose(id={self.id}')>"


class Diet(Base):
    __tablename__ = "diet"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    calories = Column(Integer)
    createdAt = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Diet(id={self.id}')>"

