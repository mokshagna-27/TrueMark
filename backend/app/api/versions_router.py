
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.core.database import SessionLocal
from app.api.versions import ContentVersion


router = APIRouter(prefix="/versions", tags=["Version History"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class VersionCreate(BaseModel):
    id: UUID
    document_id: UUID
    document_title: str = Field(min_length=1, max_length=255)
    version_number: int = Field(ge=1)
    content: str = Field(min_length=1)
    note: str = "Content updated"
    created_at: datetime


class VersionResponse(BaseModel):
    id: str
    documentId: str
    documentTitle: str
    versionNumber: int
    content: str
    note: str
    createdAt: datetime


def to_response(version: ContentVersion) -> VersionResponse:
    return VersionResponse(
        id=version.id,
        documentId=version.document_id,
        documentTitle=version.document_title,
        versionNumber=version.version_number,
        content=version.content,
        note=version.note,
        createdAt=version.created_at,
    )


@router.get("", response_model=list[VersionResponse])
def list_versions(db: Session = Depends(get_db)):
    versions = (
        db.query(ContentVersion)
        .order_by(ContentVersion.created_at.desc())
        .all()
    )
    return [to_response(version) for version in versions]


@router.post("", response_model=VersionResponse, status_code=201)
def create_version(
    payload: VersionCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(ContentVersion)
        .filter(ContentVersion.id == str(payload.id))
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Version already exists.")

    version = ContentVersion(
        id=str(payload.id),
        document_id=str(payload.document_id),
        document_title=payload.document_title.strip(),
        version_number=payload.version_number,
        content=payload.content,
        note=payload.note,
        created_at=payload.created_at,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return to_response(version)


@router.delete("/{version_id}", status_code=204)
def delete_version(
    version_id: UUID,
    db: Session = Depends(get_db),
):
    version = (
        db.query(ContentVersion)
        .filter(ContentVersion.id == str(version_id))
        .first()
    )
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found.")

    db.delete(version)
    db.commit()
    return None
