from typing import Literal

from pydantic import BaseModel


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    status: Literal["uploaded"]


class DatasetSummaryResponse(BaseModel):
    dataset_id: str
    rows: int
    columns: int
    column_names: list[str]
    missing_values: dict[str, int]
    numeric_columns: list[str]
    categorical_columns: list[str]
