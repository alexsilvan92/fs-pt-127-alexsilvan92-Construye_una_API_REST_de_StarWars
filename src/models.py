from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    """
    Representa a los usuarios de la aplicación.
    Un usuario puede tener MUCHOS favoritos.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)

    first_name: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    last_name: Mapped[str] = mapped_column(String(100), nullable=True, default="")

    # RELACIÓN 1 a MUCHOS con Favorite
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name
        }

class Character(db.Model):
    """
    Representa personajes del universo Star Wars.
    """

    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    height: Mapped[str] = mapped_column(String(20), nullable=True)
    mass: Mapped[int] = mapped_column(Integer(), nullable=True)

    # RELACIÓN INVERSA con Favorite
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="character",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Character {self.id}: {self.name}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "mass": self.mass
        }

class Planet(db.Model):
    """
    Un planeta puede ser favorito de muchos usuarios.
    """

    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    climate: Mapped[str] = mapped_column(String(100), nullable=True)
    terrain: Mapped[str] = mapped_column(String(100), nullable=True)
    population: Mapped[int] = mapped_column(BigInteger(), nullable=True)

    # RELACIÓN INVERSA con Favorite
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="planet",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Planet {self.id}: {self.name}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }

class Vehicle(db.Model):
    """
    Representa naves o vehículos del universo Star Wars.
    """

    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cargo_capacity: Mapped[str] = mapped_column(String(50), nullable=True)
    length: Mapped[str] = mapped_column(String(50), nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=True)

    # RELACIÓN INVERSA con Favorite
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="vehicle",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Vehicle {self.id}: {self.name}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "cargo_capacity": self.cargo_capacity,
            "length": self.length,
            "model": self.model
        }

class Favorite(db.Model):
    """
    Conecta un usuario con:
    - Un planeta
    - Un personaje
    - Un vehículo

    SOLO uno de estos puede tener valor por fila.
    """

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)

    # FK al usuario
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    # FK opcionales (solo uno debe usarse)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("planets.id"),
        nullable=True
    )

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"),
        nullable=True
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=datetime.now(timezone.utc)
    )

    # RELACIONES
    # -------------------------------------------------------------------------
    user: Mapped["User"] = relationship(
        "User",
        back_populates="favorites"
    )

    planet: Mapped["Planet"] = relationship(
        "Planet",
        back_populates="favorites"
    )

    character: Mapped["Character"] = relationship(
        "Character",
        back_populates="favorites"
    )

    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle",
        back_populates="favorites"
    )
    # -------------------------------------------------------------------------

    def __repr__(self):
        return f"<Favorite {self.id}: User {self.user_id}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "character_id": self.character_id,
            "vehicle_id": self.vehicle_id,
            "created_at": self.created_at.isoformat()
        }