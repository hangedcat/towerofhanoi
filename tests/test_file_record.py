import pytest
from pathlib import Path
from txt_tool import icecube

TEST_DIR = Path(__file__).parent
SAMPLE = TEST_DIR / "text.txt"
MISSING = TEST_DIR / "nonexistent.txt"

def test_raises():
    with pytest.raises(ValueError):
        p = icecube.FileRecord(SAMPLE)
        p.mode = 'x'

def test_valid_mode():
    p = icecube.FileRecord(SAMPLE)
    p.mode = 'r'
    assert p.mode == 'r'

def test_validate_extension():
    assert icecube.FileRecord.validate_extension("text.txt") == True
    assert icecube.FileRecord.validate_extension("text.csv") == False

def test_file_line_reader():
    lines = list(line for line in icecube.file_line_reader(SAMPLE))
    assert len(lines) == 11

def test_file_line_reader2():
    lines = list(icecube.file_line_reader(MISSING))
    assert len(lines) == 0

def test_filereader_cm():
    with icecube.FileReader(SAMPLE) as f:
        assert f is not None

def test_filereader_cm2():
    with icecube.FileReader(MISSING) as f:
        assert f is None