import pytest

from briefbot.batch import discover_brief_files
from briefbot.models import BriefError


def test_discovers_json_files_in_deterministic_order(tmp_path):
    (tmp_path / "zeta.JSON").write_text("{}", encoding="utf-8")
    (tmp_path / "Alpha.json").write_text("{}", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("{}", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "inside.json").write_text("{}", encoding="utf-8")

    shallow = discover_brief_files(tmp_path)
    recursive = discover_brief_files(tmp_path, recursive=True)

    assert [path.name for path in shallow] == ["Alpha.json", "zeta.JSON"]
    assert [path.relative_to(tmp_path).as_posix() for path in recursive] == [
        "Alpha.json",
        "nested/inside.json",
        "zeta.JSON",
    ]


def test_skips_symbolic_linked_files_and_directories(tmp_path):
    real = tmp_path / "real.json"
    real.write_text("{}", encoding="utf-8")
    linked_file = tmp_path / "linked.json"
    linked_file.symlink_to(real)

    real_directory = tmp_path / "private"
    real_directory.mkdir()
    (real_directory / "nested.json").write_text("{}", encoding="utf-8")
    linked_directory = tmp_path / "linked-directory"
    linked_directory.symlink_to(real_directory, target_is_directory=True)

    found = discover_brief_files(tmp_path, recursive=True)

    assert linked_file not in found
    assert all("linked-directory" not in str(path) for path in found)


@pytest.mark.parametrize("value", [0, 1001, True, 1.5])
def test_rejects_invalid_file_limits(tmp_path, value):
    with pytest.raises(BriefError, match="max_files"):
        discover_brief_files(tmp_path, max_files=value)


def test_rejects_folder_larger_than_limit(tmp_path):
    for index in range(3):
        (tmp_path / f"{index}.json").write_text("{}", encoding="utf-8")

    with pytest.raises(BriefError, match="more than max_files=2"):
        discover_brief_files(tmp_path, max_files=2)


def test_rejects_symbolic_link_root(tmp_path):
    actual = tmp_path / "actual"
    actual.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(actual, target_is_directory=True)

    with pytest.raises(BriefError, match="symbolic link"):
        discover_brief_files(linked)
