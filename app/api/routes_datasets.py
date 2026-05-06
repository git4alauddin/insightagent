from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.schemas.dataset import DatasetAskRequest, DatasetAskResponse, DatasetSummaryResponse, DatasetUploadResponse
from app.services.dataset_analysis_router import build_route_decision
from app.services.dataset_answer_service import build_dataset_ask_response
from app.services.dataset_execution_service import DatasetExecutionError, execute_analysis_tool
from app.services.dataset_registry_service import (
    DatasetRegistryError,
    get_dataset_metadata,
    register_dataset_metadata,
)
from app.services.dataset_service import (
    DatasetServiceError,
    build_dataset_summary,
    build_upload_metadata,
    load_csv_with_checks,
    validate_csv_file,
)


router = APIRouter(tags=["datasets"])


def _resolve_dataset_storage_path(dataset_id: str) -> Path:
    try:
        metadata = get_dataset_metadata(dataset_id)
    except DatasetRegistryError as exc:
        if "Dataset not found" in str(exc):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "DATASET_NOT_FOUND",
                        "message": str(exc),
                    }
                },
            ) from exc

        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DATASET_DB_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

    storage_path = Path(str(metadata["storage_path"]))
    if not storage_path.exists():
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DATASET_STORAGE_ERROR",
                    "message": f"Dataset file is missing: {storage_path}",
                }
            },
        )

    return storage_path


@router.post("/datasets/upload", response_model=DatasetUploadResponse)
def upload_dataset(
    file: UploadFile = File(...),
    session_id: str | None = Form(default=None),
) -> DatasetUploadResponse:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "DATASET_VALIDATION_ERROR",
                    "message": "File name is required.",
                }
            },
        )

    file_bytes = file.file.read()

    try:
        validate_csv_file(file.filename, len(file_bytes))
    except DatasetServiceError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "DATASET_VALIDATION_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

    dataset_id = f"ds_{uuid4().hex}"
    base_upload_dir = Path(settings.upload_dir)
    target_folder = base_upload_dir / (session_id or "standalone")
    target_folder.mkdir(parents=True, exist_ok=True)
    target_path = target_folder / f"{dataset_id}.csv"

    try:
        target_path.write_bytes(file_bytes)
        dataframe = load_csv_with_checks(str(target_path))
        register_dataset_metadata(
            dataset_id=dataset_id,
            session_id=session_id,
            filename=file.filename,
            storage_path=str(target_path),
            row_count=int(dataframe.shape[0]),
            column_count=int(dataframe.shape[1]),
        )
        return build_upload_metadata(dataset_id, file.filename, dataframe)
    except DatasetServiceError as exc:
        target_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "DATASET_VALIDATION_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc
    except DatasetRegistryError as exc:
        target_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DATASET_DB_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc
    except OSError as exc:
        target_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DATASET_STORAGE_ERROR",
                    "message": f"Dataset could not be stored: {exc}",
                }
            },
        ) from exc


@router.get("/datasets/{dataset_id}/summary", response_model=DatasetSummaryResponse)
def get_dataset_summary(dataset_id: str) -> DatasetSummaryResponse:
    storage_path = _resolve_dataset_storage_path(dataset_id)

    try:
        dataframe = load_csv_with_checks(str(storage_path))
    except DatasetServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DATASET_STORAGE_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

    return build_dataset_summary(dataset_id, dataframe)


@router.post("/datasets/{dataset_id}/ask", response_model=DatasetAskResponse)
def ask_dataset_question(dataset_id: str, request: DatasetAskRequest) -> DatasetAskResponse:
    storage_path = _resolve_dataset_storage_path(dataset_id)

    try:
        dataframe = load_csv_with_checks(str(storage_path))
    except DatasetServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DATASET_STORAGE_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

    decision = build_route_decision(
        question=request.question,
        df_columns=[str(column) for column in dataframe.columns],
    )

    if decision.tool_name == "none":
        return DatasetAskResponse(
            answer="The question is unsupported or ambiguous for safe dataset analysis.",
            confidence="low",
            dataset_id=dataset_id,
            tool_used="none",
            tool_output_summary="No safe analysis tool matched this question.",
            analysis_trace={
                "intent": decision.intent,
                "tool_used": "none",
                "columns_used": decision.columns_used,
                "operation": decision.operation,
            },
            status="failed",
        )

    try:
        execution_result = execute_analysis_tool(dataframe, decision)
    except DatasetExecutionError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "DATASET_ANALYSIS_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

    return build_dataset_ask_response(
        question=request.question,
        decision=decision,
        execution_result=execution_result,
        dataset_id=dataset_id,
    )
