from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone # Importamos timezone para evitar el tachado en datetime.now

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # Usamos lambda para que genere la fecha exacta al insertar
    subscription_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    firstname: Mapped[str] = mapped_column(String(100), nullable=True) # Permitir vacíos
    lastname: Mapped[str] = mapped_column(String(100), nullable=True)
    
    fav_people: Mapped[list["Favorites_People"]] = relationship(back_populates="user_fav_people")
    fav_planet: Mapped[list["Favorites_Planets"]] = relationship(back_populates="user_fav_planet")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
        }

class Favorites_People(db.Model):
    __tablename__ = 'favorites_people'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    people_id: Mapped[int] = mapped_column(ForeignKey('people.id'), nullable=False)
    
    user_fav_people: Mapped["User"] = relationship(back_populates="fav_people")
    people: Mapped["People"] = relationship(back_populates="fav_people")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "people_id": self.people_id,
            "people_name": self.people.people_name if self.people else "Unknown",
            "user_username": self.user_fav_people.username if self.user_fav_people else "Unknown"
        }

class People(db.Model):
    __tablename__ = 'people'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    people_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    fav_people: Mapped[list["Favorites_People"]] = relationship(back_populates="people")

    def serialize(self):
        return {
            "id": self.id,
            "people_name": self.people_name,
        }

class Favorites_Planets(db.Model):
    __tablename__ = 'favorites_planets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    planet_id: Mapped[int] = mapped_column(ForeignKey('planets.id'), nullable=False)
    
    user_fav_planet: Mapped["User"] = relationship(back_populates="fav_planet")
    planet: Mapped["Planets"] = relationship(back_populates="fav_planet")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "planet_name": self.planet.planet_name if self.planet else "Unknown",
            "user_username": self.user_fav_planet.username if self.user_fav_planet else "Unknown"
        }

class Planets(db.Model):
    __tablename__ = 'planets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    planet_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    fav_planet: Mapped[list["Favorites_Planets"]] = relationship(back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "planet_name": self.planet_name,
        }
