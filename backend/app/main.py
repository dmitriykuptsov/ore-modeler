import io
import os
from pathlib import Path
import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Borehole, Project, Sample
from .schemas import BoreholeResponse, ProjectCreate, ProjectResponse

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Ore Modeler API", version="0.1.0")
STORAGE = Path(os.getenv("STORAGE_PATH", "/storage"))
REQUIRED = {"hole_id", "x", "y", "z", "from", "to"}

def project_or_404(db, project_id):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/projects", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=payload.name, description=payload.description)
    db.add(project); db.commit(); db.refresh(project)
    (STORAGE / "projects" / str(project.id) / "uploads").mkdir(parents=True, exist_ok=True)
    (STORAGE / "projects" / str(project.id) / "models").mkdir(parents=True, exist_ok=True)
    (STORAGE / "projects" / str(project.id) / "exports").mkdir(parents=True, exist_ok=True)
    return project

@app.get("/api/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.scalars(select(Project).order_by(Project.id.desc())).all()

@app.post("/api/projects/{project_id}/upload")
async def upload_csv(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    project = project_or_404(db, project_id)
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported")
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(400, f"Invalid CSV: {exc}")
    missing = REQUIRED - set(df.columns)
    if missing:
        raise HTTPException(400, f"Missing columns: {', '.join(sorted(missing))}")
    for col in ["x", "y", "z", "from", "to"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["hole_id", "x", "y", "z", "from", "to"])
    df = df[df["to"] > df["from"]]
    project_dir = STORAGE / "projects" / str(project.id) / "uploads"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / file.filename).write_bytes(content)

    holes = {}
    for row in df.itertuples(index=False):
        key = str(row.hole_id)
        if key not in holes:
            holes[key] = Borehole(project_id=project.id, hole_id=key, x=float(row.x), y=float(row.y), z=float(row.z))
            db.add(holes[key])
    db.flush()
    for row in df.itertuples(index=False):
        hole = holes[str(row.hole_id)]
        cu = getattr(row, "cu", None)
        au = getattr(row, "au", None)
        db.add(Sample(project_id=project.id, borehole_id=hole.id, depth_from=float(row._asdict()["from"]), depth_to=float(row._asdict()["to"]), cu=None if pd.isna(cu) else float(cu), au=None if pd.isna(au) else float(au)))
    db.commit()
    return {"project_id": project.id, "filename": file.filename, "boreholes": len(holes), "samples": len(df), "min_depth": float(df["from"].min()), "max_depth": float(df["to"].max())}

@app.get("/api/projects/{project_id}/boreholes", response_model=list[BoreholeResponse])
def list_boreholes(project_id: int, db: Session = Depends(get_db)):
    project_or_404(db, project_id)
    return db.scalars(select(Borehole).where(Borehole.project_id == project_id).order_by(Borehole.hole_id)).all()
