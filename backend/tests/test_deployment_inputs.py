from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_dockerfiles_only_copy_existing_required_inputs():
    assert (ROOT / "backend" / "uv.lock").is_file()
    frontend_dockerfile = (ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")
    assert ".npmrc" not in frontend_dockerfile
    assert "pnpm@11.21.0" in frontend_dockerfile


def test_compose_required_variables_are_documented():
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    for name in ("MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_ROOT_PASSWORD"):
        assert f"{name}=" in example
