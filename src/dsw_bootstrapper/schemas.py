from uuid import UUID

from pydantic import BaseModel, Field


class TenantOut(BaseModel):
    uuid: UUID
    tenant_id: str = Field(alias="tenantId")
    name: str

    class Config:
        from_attributes = True  # for SQLAlchemy ORM compatibility


class PackageOut(BaseModel):
    id: str
    name: str
    previous_package_id: str | None = Field(alias="previousPackageId", default=None)
    fork_of_package_id: str | None = Field(alias="forkOfPackageId", default=None)
    merge_checkpoint_package_id: str | None = Field(alias="mergeCheckpointPackageId", default=None)

    class Config:
        from_attributes = True  # for SQLAlchemy ORM compatibility


class DocumentTemplateOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True  # for SQLAlchemy ORM compatibility


class QuestionnaireOut(BaseModel):
    uuid: UUID
    name: str
    package_id: str = Field(alias="packageId")
    document_template_id: str | None = Field(alias="documentTemplateId")
    format_uuid: UUID | None = Field(alias="formatUuid")


class DocumentOut(BaseModel):
    uuid: UUID
    name: str
    questionnaire_uuid: UUID = Field(alias="questionnaireUuid")
    document_template_id: str = Field(alias="documentTemplateId")
    format_uuid: UUID = Field(alias="formatUuid")
    file_name: str = Field(alias="fileName")


class TenantContents(BaseModel):
    packages: list[PackageOut] = Field(default_factory=list)
    document_templates: list[DocumentTemplateOut] = Field(default_factory=list, alias="documentTemplates")
    questionnaires: list[QuestionnaireOut] = Field(default_factory=list)
    documents: list[DocumentOut] = Field(default_factory=list)


class PackageIn(BaseModel):
    id: str
    include_dependencies: bool = Field(alias='includeDependencies')


class DocumentTemplateIn(BaseModel):
    id: str


class QuestionnaireIn(BaseModel):
    uuid: UUID
    new_uuid: bool = Field(alias="newUuid")
    anonymize: bool
    include_dependencies: bool = Field(alias="includeDependencies")
    include_versions: bool = Field(alias="includeVersions")


class DocumentIn(BaseModel):
    uuid: UUID
    new_uuid: bool = Field(alias="newUuid")
    anonymize: bool
    include_dependencies: bool = Field(alias="includeDependencies")


class RecipeInstruction(BaseModel):
    name: str
    description: str | None = None
    tenant_uuid: UUID = Field(alias="tenantUuid")
    packages: list[PackageIn] = Field(default_factory=list)
    document_templates: list[DocumentTemplateIn] = Field(default_factory=list, alias="documentTemplates")
    questionnaires: list[QuestionnaireIn] = Field(default_factory=list)
    documents: list[DocumentIn] = Field(default_factory=list)
