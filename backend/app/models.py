from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    boreholes = relationship("Borehole", back_populates="project", cascade="all, delete-orphan")
    samples = relationship("Sample", back_populates="project", cascade="all, delete-orphan")

class Borehole(Base):
    __tablename__ = "boreholes"
    __table_args__ = (UniqueConstraint("project_id", "hole_id", name="uq_project_hole"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    hole_id: Mapped[str] = mapped_column(String(100), nullable=False)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    z: Mapped[float] = mapped_column(Float, nullable=False)
    project = relationship("Project", back_populates="boreholes")
    samples = relationship("Sample", back_populates="borehole", cascade="all, delete-orphan")

class Sample(Base):
    __tablename__ = "samples"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    borehole_id: Mapped[int] = mapped_column(ForeignKey("boreholes.id", ondelete="CASCADE"), nullable=False)
    depth_from: Mapped[float] = mapped_column(Float, nullable=False)
    depth_to: Mapped[float] = mapped_column(Float, nullable=False)
    cu: Mapped[float | None] = mapped_column(Float)
    au: Mapped[float | None] = mapped_column(Float)
    project = relationship("Project", back_populates="samples")
    borehole = relationship("Borehole", back_populates="samples")
