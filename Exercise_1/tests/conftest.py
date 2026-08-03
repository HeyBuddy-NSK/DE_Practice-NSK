import pytest


@pytest.fixture
def test_valid_download_uri() -> str:
    """Fixture providing a valid Divvy dataset download URI."""
    return "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip"

@pytest.fixture
def test_invalid_download_uri() -> str:
    """Fixture providing an invalid Divvy dataset download URI."""
    return "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip_invalid"

