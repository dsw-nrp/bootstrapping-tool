import io
import json
import uuid
import zipfile

import minio
from sqlalchemy.orm import Session

from . import models, schemas
from .config import Config

_TENANT_PLACEHOLDER = "<<|TENANT-ID|>>"


def _package2insert(package: models.Package) -> str:
    fields = {
        'id': f"'{package.id}'",
        'name': f"'{package.name}'",
        'organization_id': f"'{package.organization_id}'",
        'km_id': f"'{package.km_id}'",
        'version': f"'{package.version}'",
        'metamodel_version': f"{package.metamodel_version}",
        'description': f"'{package.description}'",
        'readme': f"'{package.readme}'",
        'license': f"'{package.license}'",
        'previous_package_id': f"'{package.previous_package_id}'" if package.previous_package_id else "NULL",
        'fork_of_package_id': f"'{package.fork_of_package_id}'" if package.fork_of_package_id else "NULL",
        'merge_checkpoint_package_id': f"'{package.merge_checkpoint_package_id}'" if package.merge_checkpoint_package_id else "NULL",
        'events': f"'{package.events}'",
        'created_at': f"'{package.created_at.isoformat()}'",
        'tenant_uuid': _TENANT_PLACEHOLDER,
        'phase': f"'{package.phase}'",
        'non_editable': 'TRUE' if package.non_editable else 'FALSE',
    }
    fields_sql = ", ".join(fields.keys())
    values_sql = ", ".join(fields.values())
    sql_script = f"""INSERT INTO package ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _dt2insert(document_template: models.DocumentTemplate) -> str:
    fields = {
        'id': f"'{document_template.id}'",
        'name': f"'{document_template.name}'",
        'organization_id': f"'{document_template.organization_id}'",
        'template_id': f"'{document_template.template_id}'",
        'version': f"'{document_template.version}'",
        'metamodel_version': f"'{document_template.metamodel_version}'",
        'description': f"'{document_template.description}'",
        'readme': f"'{document_template.readme}'",
        'license': f"'{document_template.license}'",
        'allowed_packages': f"'{document_template.allowed_packages}'",
        'created_at': f"'{document_template.created_at.isoformat()}'",
        'tenant_uuid': _TENANT_PLACEHOLDER,
        'updated_at': f"'{document_template.updated_at.isoformat()}'",
        'phase': f"'{document_template.phase}'",
        'non_editable': 'TRUE' if document_template.non_editable else 'FALSE',
    }
    fields_sql = ", ".join(fields.keys())
    values_sql = ", ".join(fields.values())
    sql_script = f"""INSERT INTO document_template ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _dt_assets2insert(assets: list[models.DocumentTemplateAsset]) -> str:
    sql_script = ""
    for asset in assets:
        fields = {
            'document_template_id': f"'{asset.document_template_id}'",
            'uuid': f"'{asset.uuid}'",
            'file_name': f"'{asset.file_name}'",
            'content_type': f"'{asset.content_type}'",
            'tenant_uuid': _TENANT_PLACEHOLDER,
            'file_size': f"{asset.file_size}",
            'created_at': f"'{asset.created_at.isoformat()}'",
            'updated_at': f"'{asset.updated_at.isoformat()}'",
        }
        fields_sql = ", ".join(fields.keys())
        values_sql = ", ".join(fields.values())
        sql_script += f"""INSERT INTO document_template_asset ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _dt_files2insert(files: list[models.DocumentTemplateFile]) -> str:
    sql_script = ""
    for file in files:
        # escape content as it may contain quotes
        econtent = file.content.replace("'", "''")
        fields = {
            'document_template_id': f"'{file.document_template_id}'",
            'uuid': f"'{file.uuid}'",
            'file_name': f"'{file.file_name}'",
            'content': f"'{econtent}'",
            'tenant_uuid': _TENANT_PLACEHOLDER,
            'created_at': f"'{file.created_at.isoformat()}'",
            'updated_at': f"'{file.updated_at.isoformat()}'",
        }
        fields_sql = ", ".join(fields.keys())
        values_sql = ", ".join(fields.values())
        sql_script += f"""INSERT INTO document_template_file ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _dt_formats2insert(formats: list[models.DocumentTemplateFormat]) -> str:
    sql_script = ""
    for fmt in formats:
        fields = {
            'document_template_id': f"'{fmt.document_template_id}'",
            'uuid': f"'{fmt.uuid}'",
            'name': f"'{fmt.name}'",
            'icon': f"'{fmt.icon}'",
            'tenant_uuid': _TENANT_PLACEHOLDER,
            'created_at': f"'{fmt.created_at.isoformat()}'",
            'updated_at': f"'{fmt.updated_at.isoformat()}'",
        }
        fields_sql = ", ".join(fields.keys())
        values_sql = ", ".join(fields.values())
        sql_script += f"""INSERT INTO document_template_format ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _dt_steps2insert(steps: list[models.DocumentTemplateFormatStep]) -> str:
    sql_script = ""
    for step in steps:
        # encode options from list of dicts to JSON string
        eoptions = json.dumps(step.options).replace("'", "''")
        fields = {
            'document_template_id': f"'{step.document_template_id}'",
            'format_uuid': f"'{step.format_uuid}'",
            'position': f"{step.position}",
            'name': f"'{step.name}'",
            'options': f"'{eoptions}'",
            'tenant_uuid': _TENANT_PLACEHOLDER,
            'created_at': f"'{step.created_at.isoformat()}'",
            'updated_at': f"'{step.updated_at.isoformat()}'",
        }
        fields_sql = ", ".join(fields.keys())
        values_sql = ", ".join(fields.values())
        sql_script += f"""INSERT INTO document_template_format_step ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _questionnaire2insert(questionnaire_uuid: str, questionnaire: models.Questionnaire) -> str:
    fields = {
        'uuid': f"'{questionnaire_uuid}'",
        'name': f"'{questionnaire.name}'",
        'visibility': f"'{questionnaire.visibility}'",
        'sharing': f"'{questionnaire.sharing}'",
        'package_id': f"'{questionnaire.package_id}'",
        'selected_question_tag_uuids': f"ARRAY{questionnaire.selected_question_tag_uuids}" if questionnaire.selected_question_tag_uuids else "NULL",
        'document_template_id': f"'{questionnaire.document_template_id}'" if questionnaire.document_template_id else "NULL",
        'format_uuid': f"'{questionnaire.format_uuid}'" if questionnaire.format_uuid else "NULL",
        'created_by': "NULL",
        'created_at': f"'{questionnaire.created_at.isoformat()}'",
        'updated_at': f"'{questionnaire.updated_at.isoformat()}'",
        'description': f"'{questionnaire.description}'",
        'is_template': 'TRUE' if questionnaire.is_template else 'FALSE',
        'squashed': 'TRUE' if questionnaire.squashed else 'FALSE',
        'tenant_uuid': _TENANT_PLACEHOLDER,
        'project_tags': f"ARRAY{questionnaire.project_tags}" if questionnaire.project_tags else "NULL",
    }
    fields_sql = ", ".join(fields.keys())
    values_sql = ", ".join(fields.values())
    sql_script = f"""INSERT INTO questionnaire ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _questionnaire_events2insert(questionnaire_uuid: str, events: list[models.QuestionnaireEvent]) -> str:
    sql_script = ""
    for event in events:
        fields = {
            'uuid': f"'{event.uuid}'",
            'event_type': f"'{event.event_type}'",
            'path': f"'{event.path}'" if event.path else "NULL",
            'created_at': f"'{event.created_at.isoformat()}'",
            'created_by': "NULL",
            'questionnaire_uuid': f"'{questionnaire_uuid}'",
            'tenant_uuid': _TENANT_PLACEHOLDER,
            'value_Type': f"'{event.value_type}'" if event.value_type else "NULL",
            'value': f"'{event.value}'" if event.value else "NULL",
            'value_id': f"'{event.value_id}'" if event.value_id else "NULL",
            'value_raw': f"'{json.dumps(event.value_raw).replace("'", "''")}'" if event.value_raw else "NULL",
        }
        fields_sql = ", ".join(fields.keys())
        values_sql = ", ".join(fields.values())
        sql_script += f"""INSERT INTO questionnaire_event ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _questionnaire_files2insert(questionnaire_uuid: str, files: list[models.QuestionnaireFile]) -> str:
    sql_script = ""
    for file in files:
        fields = {
            'uuid': f"'{file.uuid}'",
            'file_name': f"'{file.file_name}'",
            'content_type': f"'{file.content_type}'",
            'file_size': f"{file.file_size}",
            'questionnaire_uuid': f"'{questionnaire_uuid}'",
            'created_by': "NULL",
            'tenant_uuid': _TENANT_PLACEHOLDER,
            'created_at': f"'{file.created_at.isoformat()}'",
        }
        fields_sql = ", ".join(fields.keys())
        values_sql = ", ".join(fields.values())
        sql_script += f"""INSERT INTO questionnaire_file ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _questionnaire_versions2insert(questionnaire_uuid: str, versions: list[models.QuestionnaireVersion]) -> str:
    sql_script = ""
    for version in versions:
        fields = {
            'uuid': f"'{version.uuid}'",
            'name': f"'{version.name}'",
            'description': f"'{version.description}'",
            'event_uuid': f"'{version.event_uuid}'",
            'questionnaire_uuid': f"'{questionnaire_uuid}'",
            'tenant_uuid': _TENANT_PLACEHOLDER,
            'created_by': "NULL",
            'created_at': f"'{version.created_at.isoformat()}'",
            'updated_at': f"'{version.updated_at.isoformat()}'",
        }
        fields_sql = ", ".join(fields.keys())
        values_sql = ", ".join(fields.values())
        sql_script += f"""INSERT INTO questionnaire_version ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


def _document2insert(document_uuid: str, questionnaire_uuid: str, document: models.Document) -> str:
    fields = {
        'uuid': f"'{document_uuid}'",
        'name': f"'{document.name}'",
        'state': f"'{document.state}'",
        'durability': f"'{document.durability}'",
        'questionnaire_uuid': f"'{questionnaire_uuid}'",
        'questionnaire_event_uuid': f"'{document.questionnaire_event_uuid}'",
        'questionnaire_replies_hash': f"{document.questionnaire_replies_hash}",
        'document_template_id': f"'{document.document_template_id}'",
        'format_uuid': f"'{document.format_uuid}'",
        'created_by': "NULL",
        'retrieved_at': f"'{document.created_at.isoformat()}'" if document.retrieved_at else "NULL",
        'finished_at': f"'{document.finished_at.isoformat()}'" if document.finished_at else "NULL",
        'created_at': f"'{document.created_at.isoformat()}'",
        'file_name': f"'{document.file_name}'" if document.file_name else "NULL",
        'content_type': f"'{document.content_type}'" if document.content_type else "NULL",
        'worker_log': f"'{document.worker_log}'" if document.worker_log else "NULL",
        'tenant_uuid': _TENANT_PLACEHOLDER,
        'file_size': f"{document.file_size}" if document.file_size else "NULL",
    }
    fields_sql = ", ".join(fields.keys())
    values_sql = ", ".join(fields.values())
    sql_script = f"""INSERT INTO document ({fields_sql}) VALUES ({values_sql});\n"""
    return sql_script


class S3Storage:

    @staticmethod
    def _get_endpoint(url: str):
        parts = url.split('://', maxsplit=1)
        return parts[0] if len(parts) == 1 else parts[1]

    def __init__(self, tenant_uuid: str):
        self.client = minio.Minio(
            endpoint=self._get_endpoint(Config.S3_URL),
            access_key=Config.S3_ACCESS_KEY,
            secret_key=Config.S3_SECRET_KEY,
            secure=Config.S3_URL.startswith('https://'),
            region=Config.S3_REGION,
        )
        self.tenant_uuid = tenant_uuid
        self.bucket = Config.S3_BUCKET

    def _path(self, path: str) -> str:
        if self.tenant_uuid == "00000000-0000-0000-0000-000000000000":
            return path
        return f"{self.tenant_uuid}/{path}"

    def download_object(self, path: str) -> bytes:
        response = self.client.get_object(
            bucket_name=self.bucket,
            object_name=self._path(path),
        )
        data = response.read()
        response.close()
        response.release_conn()
        return data


class RecipeBuilder:

    def __init__(self, tenant_uuid: uuid.UUID, zip_file: zipfile.ZipFile, db: Session):
        self.tenant_uuid = tenant_uuid
        self.zip_file = zip_file
        self.db = db
        self.s3 = S3Storage(str(tenant_uuid))
        self._next_package_n = 1
        self._next_gen_uuid = 0
        self._questionnaire_uuids = {}  # type: dict[uuid.UUID, str]
        self._document_uuids = {}  # type: dict[uuid.UUID, str]
        self._added_package_ids = set()  # type: set[str]
        self._added_document_template_ids = set()  # type: set[str]
        self._added_questionnaire_uuids = set()  # type: set[uuid.UUID]
        self._added_document_uuids = set()  # type: set[uuid.UUID]
        self.db_scripts = []  # type: list[str]

    def _next_uuid_placeholder(self) -> str:
        placeholder = "{{-UUID[" + str(self._next_gen_uuid) + "]-}}"
        self._next_gen_uuid += 1
        return placeholder

    def run(self, instruction: schemas.RecipeInstruction):
        for package in instruction.packages:
            self._add_package(package)
        for document_template in instruction.document_templates:
            self._add_document_template(document_template)
        for questionnaire in instruction.questionnaires:
            self._add_questionnaire(questionnaire)
        for document in instruction.documents:
            self._add_document(document)
        self._add_json_descriptor(instruction)

    def _add_db_script(self, path: str, data: str):
        self.db_scripts.append(path)
        self.zip_file.writestr(
            zinfo_or_arcname=path,
            data=data,
        )

    def _add_s3_object(self, path: str, data: bytes | str):
        self.zip_file.writestr(
            zinfo_or_arcname=f"files/{path}",
            data=data,
        )

    def _add_package(self, package: schemas.PackageIn):
        if package.id in self._added_package_ids:
            return
        self._added_package_ids.add(package.id)
        result = self.db.query(models.Package).filter(
            models.Package.id == package.id,
            models.Package.tenant_uuid == self.tenant_uuid
        ).first()  # type: models.Package | None
        if result is None:
            raise ValueError("Package not found")
        if result.previous_package_id and package.include_dependencies:
            self._add_package(schemas.PackageIn(
                id=result.previous_package_id,
                includeDependencies=package.include_dependencies,
            ))
        if result.fork_of_package_id and package.include_dependencies:
            self._add_package(schemas.PackageIn(
                id=result.fork_of_package_id,
                includeDependencies=package.include_dependencies,
            ))
        if result.merge_checkpoint_package_id and package.include_dependencies:
            self._add_package(schemas.PackageIn(
                id=result.merge_checkpoint_package_id,
                includeDependencies=package.include_dependencies,
            ))

        sql_script = _package2insert(result)
        name = package.id.replace(":", "_")
        self._add_db_script(
            path=f"packages/{self._next_package_n}__{name}.sql",
            data=sql_script,
        )
        self._next_package_n += 1

    def _add_document_template(self, document_template: schemas.DocumentTemplateIn):
        if document_template.id in self._added_document_template_ids:
            return
        self._added_document_template_ids.add(document_template.id)
        result = self.db.query(models.DocumentTemplate).filter(
            models.DocumentTemplate.id == document_template.id,
            models.DocumentTemplate.tenant_uuid == self.tenant_uuid
        ).first()  # type: models.DocumentTemplate | None
        if result is None:
            raise ValueError("Document Template not found")

        assets = self.db.query(models.DocumentTemplateAsset).filter(
            models.DocumentTemplateAsset.document_template_id == document_template.id,
            models.DocumentTemplateAsset.tenant_uuid == self.tenant_uuid
        ).all()
        files = self.db.query(models.DocumentTemplateFile).filter(
            models.DocumentTemplateFile.document_template_id == document_template.id,
            models.DocumentTemplateFile.tenant_uuid == self.tenant_uuid
        ).all()
        formats = self.db.query(models.DocumentTemplateFormat).filter(
            models.DocumentTemplateFormat.document_template_id == document_template.id,
            models.DocumentTemplateFormat.tenant_uuid == self.tenant_uuid
        ).all()
        steps = self.db.query(models.DocumentTemplateFormatStep).filter(
            models.DocumentTemplateFormatStep.document_template_id == document_template.id,
            models.DocumentTemplateFormatStep.tenant_uuid == self.tenant_uuid
        ).all()

        name = document_template.id.replace(":", "_")
        self._add_db_script(
            path=f"document-template/{name}/01__document-template.sql",
            data=_dt2insert(result),
        )
        for asset in assets:
            data = self.s3.download_object(f"templates/{document_template.id}/{str(asset.uuid)}")
            self._add_s3_object(
                path=f"templates/{name}/{str(asset.uuid)}",
                data=data,
            )
        self._add_db_script(
            path=f"document-template/{name}/02__assets.sql",
            data=_dt_assets2insert(assets),
        )
        self._add_db_script(
            path=f"document-template/{name}/03__files.sql",
            data=_dt_files2insert(files),
        )
        self._add_db_script(
            path=f"document-template/{name}/04__formats.sql",
            data=_dt_formats2insert(formats),
        )
        self._add_db_script(
            path=f"document-template/{name}/05__steps.sql",
            data=_dt_steps2insert(steps),
        )

    def _add_questionnaire(self, questionnaire: schemas.QuestionnaireIn):
        if questionnaire.uuid in self._added_questionnaire_uuids:
            return
        self._added_questionnaire_uuids.add(questionnaire.uuid)
        result = self.db.query(models.Questionnaire).filter(
            models.Questionnaire.uuid == questionnaire.uuid,
            models.Questionnaire.tenant_uuid == self.tenant_uuid
        ).first()  # type: models.Questionnaire | None
        if result is None:
            raise ValueError("Questionnaire not found")
        if result.package_id and questionnaire.include_dependencies:
            self._add_package(schemas.PackageIn(
                id=result.package_id,
                includeDependencies=True,
            ))
        if result.document_template_id and questionnaire.include_dependencies:
            self._add_document_template(schemas.DocumentTemplateIn(
                id=result.document_template_id,
            ))
        events = self.db.query(models.QuestionnaireEvent).filter(
            models.QuestionnaireEvent.questionnaire_uuid == questionnaire.uuid,
            models.QuestionnaireEvent.tenant_uuid == self.tenant_uuid
        ).all()
        files = self.db.query(models.QuestionnaireFile).filter(
            models.QuestionnaireFile.questionnaire_uuid == questionnaire.uuid,
            models.QuestionnaireFile.tenant_uuid == self.tenant_uuid
        ).all()
        versions = self.db.query(models.QuestionnaireVersion).filter(
            models.QuestionnaireVersion.questionnaire_uuid == questionnaire.uuid,
            models.QuestionnaireVersion.tenant_uuid == self.tenant_uuid
        ).all()

        questionnaire_uuid = str(questionnaire.uuid)
        if questionnaire.new_uuid:
            questionnaire_uuid = self._next_uuid_placeholder()
            self._questionnaire_uuids[questionnaire.uuid] = str(questionnaire_uuid)

        name = result.name.replace(" ", "_").lower()
        self._add_db_script(
            path=f"questionnaires/{name}/01__questionnaire.sql",
            data=_questionnaire2insert(questionnaire_uuid, result),
        )
        self._add_db_script(
            path=f"questionnaires/{name}/02__events.sql",
            data=_questionnaire_events2insert(questionnaire_uuid, events),
        )
        self._add_db_script(
            path=f"questionnaires/{name}/03__files.sql",
            data=_questionnaire_files2insert(questionnaire_uuid, files),
        )
        for file in files:
            data = self.s3.download_object(
                path=f"questionnaire-files/{str(questionnaire.uuid)}/{str(file.uuid)}"
            )
            self._add_s3_object(
                path=f"questionnaires-files/{questionnaire_uuid}/{file.uuid}",
                data=data,
            )
        if questionnaire.include_versions:
            self._add_db_script(
                path=f"questionnaires/{name}/04__versions.sql",
                data=_questionnaire_versions2insert(questionnaire_uuid, versions),
            )

    def _add_document(self, document: schemas.DocumentIn):
        if document.uuid in self._added_document_uuids:
            return
        self._added_document_uuids.add(document.uuid)
        result = self.db.query(models.Document).filter(
            models.Document.uuid == document.uuid,
            models.Document.tenant_uuid == self.tenant_uuid
        ).first()  # type: models.Document | None
        if result is None:
            raise ValueError("Document not found")
        if result.document_template_id and document.include_dependencies:
            self._add_document_template(schemas.DocumentTemplateIn(
                id=result.document_template_id,
            ))
        if result.questionnaire_uuid and document.include_dependencies:
            self._add_questionnaire(schemas.QuestionnaireIn(
                uuid=result.questionnaire_uuid,
                newUuid=document.new_uuid,
                anonymize=document.anonymize,
                includeDependencies=document.include_dependencies,
                includeVersions=document.include_dependencies,
            ))
        questionnaire_uuid = str(result.questionnaire_uuid)
        if result.questionnaire_uuid in self._questionnaire_uuids:
            questionnaire_uuid = self._questionnaire_uuids[result.questionnaire_uuid]
        document_uuid = str(document.uuid)
        if document.new_uuid:
            document_uuid = self._next_uuid_placeholder()
            self._document_uuids[document.uuid] = str(document_uuid)
        name = result.name.replace(" ", "_").lower()
        self._add_db_script(
            path=f"documents/{name}_{str(document.uuid)}.sql",
            data=_document2insert(document_uuid, questionnaire_uuid, result)
        )
        data = self.s3.download_object(f"documents/{str(document.uuid)}")
        self._add_s3_object(
            path=f"documents/{document_uuid}",
            data=data,
        )

    def _add_json_descriptor(self, instruction: schemas.RecipeInstruction):
        scripts = [{"path": sql_script} for sql_script in self.db_scripts]
        data = {
            "name": instruction.name,
            "description": instruction.description,
            "db": {
                "scripts": scripts,
                "tenantIdPlaceholder": _TENANT_PLACEHOLDER
            },
            "s3": {
                "dir": "app",
                "copy": [
                    {
                        "path": "files"
                    },
                ],
                "filenameReplace": {
                    ":": "_"
                }
            },
            "uuids": {
                "count": self._next_gen_uuid,
                "placeholder": "{{-UUID[n]-}}"
            },
            "initWait": 20.0
        }
        self.zip_file.writestr(
            zinfo_or_arcname=f"{instruction.name}.seed.json",
            data=json.dumps(data, indent=4),
        )


def build_recipe(instruction: schemas.RecipeInstruction, db: Session) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        builder = RecipeBuilder(
            tenant_uuid=instruction.tenant_uuid,
            zip_file=z,
            db=db,
        )
        builder.run(instruction)
    return buf.getvalue()
