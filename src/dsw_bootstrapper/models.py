from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Integer, JSON, DateTime, Uuid, Boolean, ARRAY, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class Tenant(Base):
    __tablename__ = "tenant"

    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)


class Package(Base):
    __tablename__ = "package"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    organization_id: Mapped[str] = mapped_column(String)
    km_id: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    metamodel_version: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String)
    readme: Mapped[str] = mapped_column(String)
    license: Mapped[str] = mapped_column(String)
    previous_package_id: Mapped[str | None] = mapped_column(String, nullable=True)
    fork_of_package_id: Mapped[str | None] = mapped_column(String, nullable=True)
    merge_checkpoint_package_id: Mapped[str | None] = mapped_column(String, nullable=True)
    events: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid)
    phase: Mapped[str] = mapped_column(String)
    non_editable: Mapped[bool] = mapped_column(Boolean)


class DocumentTemplate(Base):
    __tablename__ = "document_template"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    organization_id: Mapped[str] = mapped_column(String)
    template_id: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    metamodel_version: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    readme: Mapped[str] = mapped_column(String)
    license: Mapped[str] = mapped_column(String)
    allowed_packages: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    phase: Mapped[str] = mapped_column(String)
    non_editable: Mapped[bool] = mapped_column(Boolean)


class DocumentTemplateAsset(Base):
    __tablename__ = "document_template_asset"

    document_template_id: Mapped[str] = mapped_column(String)
    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    file_name: Mapped[str] = mapped_column(String)
    content_type: Mapped[str] = mapped_column(String)
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    file_size: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DocumentTemplateFile(Base):
    __tablename__ = "document_template_file"

    document_template_id: Mapped[str] = mapped_column(String)
    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    file_name: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DocumentTemplateFormat(Base):
    __tablename__ = "document_template_format"

    document_template_id: Mapped[str] = mapped_column(String)
    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    icon: Mapped[str] = mapped_column(String)
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DocumentTemplateFormatStep(Base):
    __tablename__ = "document_template_format_step"

    document_template_id: Mapped[str] = mapped_column(String, primary_key=True)
    format_uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    options: Mapped[dict] = mapped_column(JSON)
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Questionnaire(Base):
    __tablename__ = "questionnaire"

    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    visibility: Mapped[str] = mapped_column(String)
    sharing: Mapped[str] = mapped_column(String)
    package_id: Mapped[str] = mapped_column(String)
    selected_question_tag_uuids: Mapped[list[UUID]] = mapped_column(ARRAY(Uuid))
    document_template_id: Mapped[str] = mapped_column(String)
    format_uuid: Mapped[UUID] = mapped_column(Uuid)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_template: Mapped[bool] = mapped_column(Boolean)
    squashed: Mapped[bool] = mapped_column(Boolean)
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    project_tags: Mapped[list[str]] = mapped_column(ARRAY(String))


class QuestionnaireEvent(Base):
    __tablename__ = "questionnaire_event"

    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    event_type: Mapped[str] = mapped_column(String)
    path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    questionnaire_uuid: Mapped[UUID] = mapped_column(Uuid)
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid)
    value_type: Mapped[str | None] = mapped_column(String, nullable=True)
    value: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    value_id: Mapped[str | None] = mapped_column(String, nullable=True)
    value_raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class QuestionnaireFile(Base):
    __tablename__ = "questionnaire_file"

    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    file_name: Mapped[str] = mapped_column(String)
    content_type: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column(BigInteger)
    questionnaire_uuid: Mapped[UUID] = mapped_column(Uuid)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class QuestionnaireVersion(Base):
    __tablename__ = "questionnaire_version"

    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    event_uuid: Mapped[UUID] = mapped_column(Uuid)
    questionnaire_uuid: Mapped[UUID] = mapped_column(Uuid)
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Document(Base):
    __tablename__ = "document"

    uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String)
    durability: Mapped[str] = mapped_column(String)
    questionnaire_uuid: Mapped[UUID] = mapped_column(Uuid)
    questionnaire_event_uuid: Mapped[UUID] = mapped_column(Uuid)
    questionnaire_replies_hash: Mapped[int] = mapped_column(BigInteger)
    document_template_id: Mapped[str] = mapped_column(String)
    format_uuid: Mapped[UUID] = mapped_column(Uuid)
    created_by: Mapped[UUID] = mapped_column(Uuid, nullable=True)
    file_name: Mapped[str | None] = mapped_column(String, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String, nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    worker_log: Mapped[str | None] = mapped_column(String, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    tenant_uuid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
