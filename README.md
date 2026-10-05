# Ore Modeler MVP

Initial stack: Vue 3, FastAPI, MySQL 8.4, Redis, Celery, local file storage.

## Run

```bash
docker compose up --build
```

Frontend: http://localhost:8080
API docs: http://localhost:8000/docs
Health: http://localhost:8000/health

## Initial CSV format

Required columns:

`hole_id,x,y,z,from,to`

Optional assay columns:

`cu,au`

Example:

```csv
hole_id,x,y,z,from,to,cu,au
BH001,500100,450200,1250,0,5,0.02,0.01
BH001,500100,450200,1250,5,10,0.35,0.12
BH001,500100,450200,1250,10,15,1.25,0.45
```
