import csv
from pathlib import Path

import pandas as pd
from pandas import DataFrame
from pandas.errors import EmptyDataError, ParserError

from app.config import settings
from app.schemas.dataset import DatasetSummaryResponse, DatasetUploadResponse


class DatasetServiceError(Exception):
    pass


def validate_csv_file(file_name: str, file_size_bytes: int) -> None:
    extension = Path(file_name).suffix.lower()
    if extension not in settings.allowed_dataset_extensions:
        raise DatasetServiceError("Only CSV files are supported.")

    max_size_bytes = settings.csv_max_file_size_mb * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        raise DatasetServiceError(
            f"CSV exceeds file size limit ({settings.csv_max_file_size_mb} MB)."
        )


def load_csv_with_checks(temp_path: str) -> DataFrame:
    try:
        with open(temp_path, encoding="utf-8", newline="") as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader, None)
    except OSError as exc:
        raise DatasetServiceError("CSV file could not be read.") from exc
    except UnicodeDecodeError as exc:
        raise DatasetServiceError("CSV encoding is not supported (use UTF-8).") from exc

    if not header:
        raise DatasetServiceError("CSV file is empty.")

    normalized_header = [column.strip() for column in header]
    if len(normalized_header) != len(set(normalized_header)):
        raise DatasetServiceError("CSV contains duplicate column names.")

    try:
        dataframe = pd.read_csv(temp_path)
    except EmptyDataError as exc:
        raise DatasetServiceError("CSV file is empty.") from exc
    except UnicodeDecodeError as exc:
        raise DatasetServiceError("CSV encoding is not supported (use UTF-8).") from exc
    except ParserError as exc:
        raise DatasetServiceError("CSV could not be parsed.") from exc
    except OSError as exc:
        raise DatasetServiceError("CSV file could not be read.") from exc

    if dataframe.empty:
        raise DatasetServiceError("CSV contains no data rows.")

    if dataframe.shape[0] > settings.csv_max_rows:
        raise DatasetServiceError(
            f"CSV row count exceeds limit ({settings.csv_max_rows})."
        )

    if dataframe.shape[1] > settings.csv_max_columns:
        raise DatasetServiceError(
            f"CSV column count exceeds limit ({settings.csv_max_columns})."
        )

    return dataframe


def build_upload_metadata(
    dataset_id: str,
    filename: str,
    dataframe: DataFrame,
) -> DatasetUploadResponse:
    return DatasetUploadResponse(
        dataset_id=dataset_id,
        filename=filename,
        rows=int(dataframe.shape[0]),
        columns=int(dataframe.shape[1]),
        status="uploaded",
    )


def build_dataset_summary(
    dataset_id: str,
    dataframe: DataFrame,
) -> DatasetSummaryResponse:
    missing_values = {
        column: int(count)
        for column, count in dataframe.isna().sum().to_dict().items()
    }
    numeric_columns = [
        str(column) for column in dataframe.select_dtypes(include=["number"]).columns
    ]
    categorical_columns = [
        str(column)
        for column in dataframe.select_dtypes(exclude=["number"]).columns
    ]

    return DatasetSummaryResponse(
        dataset_id=dataset_id,
        rows=int(dataframe.shape[0]),
        columns=int(dataframe.shape[1]),
        column_names=[str(column) for column in dataframe.columns],
        missing_values=missing_values,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )
