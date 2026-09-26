from pathlib import Path

import paths

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_default_data_dir_is_relative_to_project_not_cwd(monkeypatch, tmp_path):
    monkeypatch.delenv("HANDBALL_DATA_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    assert paths.data_dir() == PROJECT_ROOT / "data"


def test_data_dir_is_configurable_via_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("HANDBALL_DATA_DIR", str(tmp_path))
    assert paths.data_dir() == tmp_path
    assert paths.processed_dir() == tmp_path / "processed"


def test_sub_dirs_are_created_on_demand(monkeypatch, tmp_path):
    monkeypatch.setenv("HANDBALL_DATA_DIR", str(tmp_path / "data"))
    for get_dir, name in [
        (paths.raw_dir, "raw"),
        (paths.processed_dir, "processed"),
        (paths.analysis_dir, "analysis"),
        (paths.visualizations_dir, "visualizations"),
    ]:
        directory = get_dir()
        assert directory == tmp_path / "data" / name
        assert directory.is_dir()


def test_has_processed_data(monkeypatch, tmp_path):
    monkeypatch.setenv("HANDBALL_DATA_DIR", str(tmp_path))
    assert not paths.has_processed_data()
    for name in paths.PROCESSED_FILES:
        (paths.processed_dir() / name).write_text("x")
    assert paths.has_processed_data()
