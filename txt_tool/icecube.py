from pathlib import Path
from datetime import datetime
from enum import Enum
from functools import wraps, partial, lru_cache
from dataclasses import dataclass, field
from collections import Counter, defaultdict, deque
from itertools import chain, islice, groupby
from typing import Union, Optional, TypeVar, Generator
import logging
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileMode(Enum):
    READ = 'r'
    WRITE = 'w'
    APPEND = 'a'

class FileRecord:

    def __init__(self, file_name: Union[str, Path], mode: str = "r"):
        self.file_name = Path(file_name)
        self.mode = mode
        self.line_count = 0
        self.created_at = datetime.now()

    def __repr__(self) -> str:       
        return f"FileRecord(file_name='{self.file_name}', mode='{self.mode}', line_count={self.line_count}, file_size={self.file_size}, created_at={self.created_at})"

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, mode: str) -> None:
        valid = [m.value for m in FileMode]
        if mode not in valid:
            raise ValueError(f"mode should be one of {valid}")
        self._mode = mode

    @staticmethod
    @lru_cache
    def validate_extension(file_name: str) -> bool:
        return file_name.endswith(".txt")
    
    @property
    def file_size(self) -> int:
        if self.file_name.exists():
            return self.file_name.stat().st_size
        return 0

class FileReader(FileRecord):

    def __init__(self, file_name: Union[str, Path]):
        super().__init__(file_name, mode= FileMode.READ.value)

    def line_reader(self) -> None:
        count = 0
        for line in file_line_reader(self.file_name):
            count += 1
        self.line_count = count
    
    def __enter__(self):
        try:
            self.file = open(self.file_name, "r")
            return self.file
        except FileNotFoundError:
            logger.warning(f"File not found: {self.file_name}")
            self.file = None
            return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False

class FileWriter(FileRecord):

    def __init__(self, file_name: str):
        super().__init__(file_name, mode= FileMode.WRITE.value)

    def text_writer(self, message: str) -> None:
        try:
            with open(self.file_name, 'w') as f:
                f.write(message)
                logger.info(f"{self.file_name} written successfully")
        except PermissionError:
            logger.error(f"Permission Denied: {self.file_name}")

class FileAppender(FileRecord):

    def __init__(self, file_name: str):
        super().__init__(file_name, mode= FileMode.APPEND.value)

    def text_appender(self, message: str) -> None:
        try:
            with open(self.file_name, 'a') as f:
                f.write(message)
                logger.info(f"{self.file_name} written successfully")
        except PermissionError:
            logger.error(f"Permission Denied: {self.file_name}")

@dataclass
class FileReport:
    file_name: str
    line_count: int
    file_size: int 
    processed_at: datetime = field(default_factory=datetime.now)

def file_line_reader(file_name: Union[str, Path]) -> Generator[str, None, None]:
    try:
        with open(file_name, 'r') as f:
            for line in f:
                yield line
    except FileNotFoundError:
        logger.warning(f"File not found: {file_name}")

def get_txt_file(folder: Path | str) -> list[Path]:
    p = Path(folder)
    return list(p.glob("*.txt"))

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug(f"{func.__name__} takes {end - start} seconds to run.")
        return result
    return wrapper

@timer
def process_folder(folder: Path | str) -> list[FileReader]:
    n = get_txt_file(folder)
    m = [FileReader(x) for x in n]
    for i in m:
        i.line_reader()
    return m

def print_report(summary: list[FileReader]) -> None:
    
    text = "File Batch Report"
    print(f"{text :=^70}")
    print(f"File Processed: {len(summary)}")
    print("-" * 70)
    print(f"{'Filename':<15} {'Lines':<8} {'Size(bytes)':<15} {'Last modified'}")
    for file in summary:
        report = FileReport(
            file_name= Path(file.file_name).name,
            line_count= file.line_count,
            file_size= file.file_size
        )
        print(f"{report.file_name :<15} {report.line_count :<8} {report.file_size:<15} {report.processed_at}")
    print("-" * 70)
    print(f"Total Lines: {sum(x.line_count for x in summary)}")

def analyze_folder(folder: Path | str) -> None:
    files = process_folder(folder)
    line_count = [file.line_count for file in files]
    analyze = Counter(line_count)
    for linecount, numfiles in analyze.most_common():
        print(f'{linecount} Line : {numfiles} File')

def tail(file_name: str, n: int) -> list[str]:
    lines = deque(maxlen=n)
    for line in file_line_reader(file_name=file_name):
        lines.append(line.strip())
    return list(lines)

def head(file_name: str, n: int) -> list[str]:
    return list(islice(file_line_reader(file_name), n))
    
def read_all_files(folder: Path | str) ->Generator[str, None, None]:
    generators = [file_line_reader(f) for f in get_txt_file(folder)]

    yield from chain.from_iterable(generators)

def group_by_linecount(folder: Path | str):
    files = sorted(process_folder(folder), key= lambda x: x.line_count)
    for key, group in groupby(files, key= lambda x: x.line_count):
        print(f"{key} lines:")
        for file in group:
            print(f"  {Path(file.file_name).name}")