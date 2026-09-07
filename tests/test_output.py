import pytest

from briefbot.models import BriefError
from briefbot.output import write_output


def test_writes_utf8_output_and_creates_parent(tmp_path):
    destination = tmp_path / "reports" / "brief.md"

    assert write_output(destination, "# Brief\n") == destination
    assert destination.read_text(encoding="utf-8") == "# Brief\n"
    assert not list(destination.parent.glob("*.tmp"))


def test_refuses_to_replace_existing_output(tmp_path):
    destination = tmp_path / "brief.md"
    destination.write_text("keep me", encoding="utf-8")

    with pytest.raises(BriefError, match="already exists"):
        write_output(destination, "replacement")

    assert destination.read_text(encoding="utf-8") == "keep me"


def test_failed_collision_leaves_no_temporary_files(tmp_path):
    destination = tmp_path / "brief.json"
    destination.write_text("existing", encoding="utf-8")

    with pytest.raises(BriefError):
        write_output(destination, "{}")

    assert list(tmp_path.iterdir()) == [destination]
