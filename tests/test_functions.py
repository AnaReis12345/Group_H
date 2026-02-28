import pytest
import os
import tempfile

from app.data_downloader import datasets_download
from app.data_merger import merge_map_with_datasets


def test_function1_exists():
    """Test that Function 1 exists."""
    assert callable(datasets_download)


def test_function2_exists():
    """Test that Function 2 exists."""
    assert callable(merge_map_with_datasets)