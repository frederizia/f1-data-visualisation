import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

import pytest


src_dir = Path(__file__).parent.parent.parent.parent


def test_tests_mirror_application_modules() -> None:
    unexpected_misplaced_tests = tuple(find_misplaced_test_modules())

    if unexpected_misplaced_tests:
        msg = dedent(
            f"""\
            There are test modules with no counterpart in the application:
            {"\n".join(_render_misplaced_test(test) for test in unexpected_misplaced_tests)}
            """
        )

        pytest.fail(msg, pytrace=False)


@dataclass
class MisplacedTest:
    filepath: str
    possible_application_paths: tuple[str, ...]


def find_misplaced_test_modules() -> Iterator[MisplacedTest]:
    for filepath in _python_files_in_path(
        ("tests/f1_data_visualisation/unit/", "tests/f1_data_visualisation/integration/")
    ):
        if not _should_check(filepath):
            continue

        possible_application_paths = _corresponding_application_paths(filepath)
        if not any(Path(path).exists() for path in possible_application_paths):
            yield MisplacedTest(filepath, tuple(possible_application_paths))


def _python_files_in_path(pathnames: Iterable[str]) -> Iterator[str]:
    for pathname in pathnames:
        yield from (
            str(py_file.relative_to(src_dir)) for py_file in (src_dir / pathname).glob("**/*.py")
        )


# We can exclude specific test files from these checks if needed.
EXCLUDED_TESTS = ()


def _should_check(path: str) -> bool:
    """
    Check whether a test file needs to match an application path.
    """
    return all(
        (
            _is_test_file(path),
            not _is_test_excluded(path),
        )
    )


def _is_test_file(path: str) -> bool:
    return Path(path).name.startswith("test_")


def _is_test_excluded(path: str) -> bool:
    """
    Check whether a test file is excluded from the checks.
    """
    return path in EXCLUDED_TESTS


def _corresponding_application_paths(test_module_path: str) -> tuple[str, ...]:
    """
    Return the possible paths for an application module that corresponds to a test module.
    """
    test_path = Path(test_module_path)
    test_filename = _normalise_test_filename(test_module_path)

    application_folder_path = Path(
        str(test_path.parent)
        .replace("tests/f1_data_visualisation/unit", "src/f1_data_visualisation")
        .replace(
            "tests/f1_data_visualisation/integration",
            "src/f1_data_visualisation",
        ),
    )

    if test_filename == "test_init.py":
        # test_init can match the __init__.py file or a regular init.py file.
        filenames = ["__init__.py", "init.py", "_init.py"]
    else:
        # Test modules do not require double underscores for testing application
        # files prefixed with an underscore.
        filename = re.sub("^test_", "", test_filename)
        filenames = [filename, f"_{filename}"]

    return tuple(str(application_folder_path / filename) for filename in filenames)


def _normalise_test_filename(filename: str) -> str:
    """
    Normalise the test filename.

    A test module may have a __suffix to support the splitting of test modules, so it needs to be
    removed:

        test_module.py -> test_module.py
        test_module__suffix.py -> test_module.py
    """
    prefix = filename.partition("test__")[1] or filename.partition("test_")[1]
    test_name = filename.partition(f"/{prefix}")[2]
    if not test_name:  # handle case where test file is in root of tests/unit or tests/integration
        test_name = filename.rpartition(prefix)[2]
    normalised = test_name.replace(".py", "").split("__")[0]

    return f"{prefix}{normalised}.py"


def _render_misplaced_test(test: MisplacedTest) -> str:
    return dedent(
        f"""
        - {test.filepath!r}
        Expected application modules: {test.possible_application_paths!r}
        """
    )
