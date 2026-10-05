from pydantic import BaseModel

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None

class ProjectResponse(ProjectCreate):
    id: int
    class Config:
        from_attributes = True

class BoreholeResponse(BaseModel):
    id: int
    hole_id: str
    x: float
    y: float
    z: float
    class Config:
        from_attributes = True
