import stat
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest

from Exercise_1.data_ingestion import (
    check_valid_url,
    download_file,
    file_unzip,
    is_valid_member,
)


def test_check_valid_url() -> None:
    """Verify that a known valid URL is recognized as valid."""
    test_uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip"
    assert check_valid_url(test_uri) is True  # noqa: S101


def test_check_invalid_url() -> None:
    """Verify that a known invalid URL is recognized as invalid."""
    test_uri = "Divvy_Trips_2018_Q4.zip"
    assert check_valid_url(test_uri) is False  # noqa: S101

def test_download_file(tmp_path: Path) -> None:
    """Placeholder for download_file tests."""
    download_uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip"
    save_path = tmp_path / "downloads"
    downloaded_file_path = download_file(download_uri, save_path)
    assert downloaded_file_path is not None  # noqa: S101
    assert downloaded_file_path.exists()  # noqa: S101

def test_download_file_invalid_url(tmp_path: Path) -> None:
    """Test download_file with an invalid URL."""
    invalid_uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip_invalid"
    save_path = tmp_path / "downloads"
    downloaded_file_path = download_file(invalid_uri, save_path)
    assert downloaded_file_path is None  # noqa: S101

def test_download_file_existing_file(tmp_path: Path) -> None:
    """Test download_file with an existing file."""
    download_uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip"
    save_path = tmp_path / "downloads"
    # First download to ensure the file exists
    downloaded_file_path = download_file(download_uri, save_path)
    assert downloaded_file_path is not None  # noqa: S101

    # Attempt to download again, should return the same path
    downloaded_file_path_again = download_file(download_uri, save_path)
    assert downloaded_file_path_again == downloaded_file_path  # noqa: S101

def test_download_file_permission_error(tmp_path: Path) -> None:
    """Test download_file with a permission error."""
    download_uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip"
    save_path = tmp_path / "downloads"
    save_path.mkdir(parents=True, exist_ok=True)

    # Remove write permissions from the directory
    save_path.chmod(stat.S_IREAD)

    downloaded_file_path = download_file(download_uri, save_path)
    assert downloaded_file_path is None  # noqa: S101

    # Restore permissions for cleanup
    save_path.chmod(stat.S_IWRITE | stat.S_IREAD)

def test_file_unzip(tmp_path: Path) -> None:
    """Placeholder for file_unzip tests."""
    file_path = tmp_path / "downloads" / "Divvy_Trips_2018_Q4.zip"
    extract_path = tmp_path / "downloads" / "extracted"

    # creating a dummy zip file for testing
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(file_path, "w") as zip_file:
        zip_file.writestr("data.csv", "id,name\n1,NSK\n")

    # Assuming the file exists and is a valid zip file
    result = file_unzip(file_path, extract_path)
    assert result is True  # noqa: S101

def test_file_unzip_invalid_file(tmp_path: Path) -> None:
    """Test file_unzip with an invalid file path."""
    invalid_file_path = tmp_path / "downloads"
    extract_path = tmp_path / "downloads" / "extracted"
    result = file_unzip(invalid_file_path, extract_path)
    assert result is False  # noqa: S101

def test_is_valid_member() -> None:
    """Placeholder for is_valid_member tests."""
    members = ["data.csv", "info.txt", ".hidden.csv", "folder/data.csv"]
    valid_members = is_valid_member(members)

    expected_valid_members = 2  # Only "data.csv" and "folder/data.csv" are valid

    assert len(valid_members) == expected_valid_members  # noqa: S101

@pytest.mark.parametrize("edge_cases", [
    None,           # Testing None
    "data.csv",     # Testing a string instead of a list
    {"file": "1"},  # Testing a dictionary instead of a list
    [],             # Testing an empty list
    ])
def test_is_valid_member_edge_case(edge_cases: Any) -> None:  # noqa: ANN401
    """Verify that various member names are correctly identified as valid or invalid."""
    # checking the edge cases for member validation
    result = is_valid_member(edge_cases)

    #asserting that the result is an empty list for invalid cases
    assert result == []  # noqa: S101
