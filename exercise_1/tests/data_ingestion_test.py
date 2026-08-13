"""Data ingestion tests.

This module contains test cases for the data_ingestion
and async_data_ingestion module,  including tests for URL validation,
file downloading, file extraction, and member validation.
Tests exercise real network calls against the source URLs.
"""
import os
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest
from src import (
    check_valid_url,
    download_all_async,
    download_file,
    file_unzip,
    is_valid_member,
)


def test_check_valid_url() -> None:
    """Verify that a known valid URL is recognized as valid."""
    test_uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip"

    # asserting that the URL is valid
    assert check_valid_url(test_uri) is True  # noqa: S101


def test_check_invalid_url() -> None:
    """Verify that a known invalid URL is recognized as invalid."""
    test_uri = "Divvy_Trips_2018_Q4.zip"

    # asserting that the URL is invalid
    assert check_valid_url(test_uri) is False  # noqa: S101

def test_download_file(tmp_path: Path) -> None:
    """Placeholder for download_file tests."""
    download_uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip"

    # creating a temporary directory for downloads
    save_path = tmp_path / "downloads"

    # downloading the file and checking if it exists
    downloaded_file_path = download_file(download_uri, save_path)

    # asserting that the downloaded file path is not None and exists
    assert downloaded_file_path is not None  # noqa: S101
    assert downloaded_file_path.exists()  # noqa: S101

def test_download_file_invalid_url(tmp_path: Path) -> None:
    """Test download_file with an invalid URL."""
    invalid_uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip_invalid"

    # creating a temporary directory for downloads
    save_path = tmp_path / "downloads"

    # attempting to download the file with an invalid URL
    downloaded_file_path = download_file(invalid_uri, save_path)

    # asserting that the downloaded file path is None due to invalid URL
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
    download_uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip"

    # using a system directory to simulate permission error
    # (e.g., C:/Windows/System32 on Windows)
    save_path = Path("C:/Windows/System32/mock_downloads_test")
    if os.name != "nt":  # If not Windows, use a common restricted directory
        save_path = tmp_path / "mock_downloads_test"
        save_path.mkdir(parents=True, exist_ok=True)
        save_path.chmod(0o500)  # Read-only permission to simulate permission error

    # attempting to download the file, expecting a permission error
    downloaded_file_path = download_file(download_uri, save_path)

    # asserting that the downloaded file path is None due to permission error
    assert downloaded_file_path is None  # noqa: S101

    if os.name != "nt":
        save_path.chmod(0o700)  # Restore permissions for cleanup

def test_file_unzip(tmp_path: Path) -> None:
    """Test file_unzip with a valid zip file."""
    # creating a temporary directory for downloads and extraction
    file_path = tmp_path / "downloads" / "Divvy_Trips_2018_Q4.zip"
    extract_path = tmp_path / "downloads" / "extracted"

    # creating a dummy zip file for testing
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # creating a zip file with a dummy CSV file inside
    with ZipFile(file_path, "w") as zip_file:
        zip_file.writestr("data.csv", "id,name\n1,NSK\n")

    # Assuming the file exists and is a valid zip file
    result = file_unzip(file_path, extract_path)

    # asserting that the extraction was successful
    assert result is True  # noqa: S101

def test_file_unzip_invalid_file(tmp_path: Path) -> None:
    """Test file_unzip with an invalid file path."""
    # creating a temporary directory for downloads and extraction
    invalid_file_path = tmp_path / "downloads"
    extract_path = tmp_path / "downloads" / "extracted"

    # attempting to unzip a non-existent file
    result = file_unzip(invalid_file_path, extract_path)

    # asserting that the extraction failed due to invalid file path
    assert result is False  # noqa: S101

def test_is_valid_member() -> None:
    """Test is_valid_member with valid member names."""
    members = ["data.csv", "info.txt", ".hidden.csv", "folder/data.csv"]

    # filtering valid members from the list
    valid_members = is_valid_member(members)

    expected_valid_members = 2  # Only "data.csv" and "folder/data.csv" are valid

    # asserting that the number of valid members matches the expected count
    assert len(valid_members) == expected_valid_members  # noqa: S101
    assert valid_members == ["data.csv","folder/data.csv"]

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

    # asserting that the result is an empty list for invalid cases
    assert result == []  # noqa: S101


@pytest.mark.asyncio
@pytest.mark.parametrize("urls",[
        (
            "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
            "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
            "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
            "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
        ),
        (), # empty tuple
    ],
)
async def test_download_all_async(urls: tuple, tmp_path: Path) -> None:
    """Verify that concurrent downloads save all requested files."""
    save_path = tmp_path / "downloads"
    download_paths = await download_all_async(urls, save_path,2)
    assert len(download_paths) == len(urls)

    if len(download_paths) > 0:
        for path in download_paths:
            assert path is not None
            assert path.exists()
