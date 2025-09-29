from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import init_db, get_db
from . import schemas, models, logic


ROOT_DIR = Path(__file__).parent
TEMPLATES_DIR = ROOT_DIR / "templates"
STATIC_DIR = ROOT_DIR / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="DSW Seeder Recipe Builder")

    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    init_db()

    @app.get("/")
    async def index(request: Request):
        return templates.TemplateResponse("index.html.j2", {"request": request})

    @app.get("/api/tenants", response_model=list[schemas.TenantOut])
    async def list_tenants(db: Session = Depends(get_db)):
        return [
            schemas.TenantOut.model_validate(tenant, from_attributes=True, by_alias=False, by_name=True)
            for tenant in db.query(models.Tenant).all()
        ]

    @app.get("/api/tenants/{uuid}/contents", response_model=schemas.TenantContents)
    async def tenant_contents(uuid: UUID, db: Session = Depends(get_db)):
        packages = db.query(models.Package).filter(
            models.Package.tenant_uuid == uuid,
        ).all()
        document_templates = db.query(models.DocumentTemplate).filter(
            models.DocumentTemplate.tenant_uuid == uuid,
            models.DocumentTemplate.phase == 'ReleasedDocumentTemplatePhase',
        ).all()
        questionnaires = db.query(models.Questionnaire).filter(
            models.Questionnaire.tenant_uuid == uuid,
        ).all()
        documents = db.query(models.Document).filter(
            models.Document.tenant_uuid == uuid,
            models.Document.state == 'DoneDocumentState',
            models.Document.durability == 'PersistentDocumentDurability',
        ).all()
        contents = schemas.TenantContents(
            packages=[
                schemas.PackageOut.model_validate(pkg, from_attributes=True, by_alias=False, by_name=True)
                for pkg in packages
            ],
            documentTemplates=[
                schemas.DocumentTemplateOut.model_validate(dt, from_attributes=True, by_alias=False, by_name=True)
                for dt in document_templates
            ],
            questionnaires=[
                schemas.QuestionnaireOut.model_validate(qtn, from_attributes=True, by_alias=False, by_name=True)
                for qtn in questionnaires
            ],
            documents=[
                schemas.DocumentOut.model_validate(doc, from_attributes=True, by_alias=False, by_name=True)
                for doc in documents
            ],
        )
        if not contents:
            raise HTTPException(status_code=404, detail="Tenant not found or no contents")
        return contents

    @app.post("/api/recipe")
    async def build_recipe(instr: schemas.RecipeInstruction, db: Session = Depends(get_db)):
        data = logic.build_recipe(instr, db)

        filename = f"seed-{instr.name.replace(' ', '-').lower() or 'recipe'}.zip"
        headers = {"Content-Disposition": f"attachment; filename={filename}"}
        return StreamingResponse(iter([data]), media_type="application/zip", headers=headers)

    # Friendly health endpoint
    @app.get("/health")
    async def health():
        return JSONResponse({"ok": True})

    return app
