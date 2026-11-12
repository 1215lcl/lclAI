"""配置变更审计测试。"""

from pathlib import Path

from lclai.audit import ConfigAuditRepository
from lclai.storage import LocalStorage


def test_config_audit_persists_only_non_sensitive_summary(tmp_path: Path) -> None:
    storage = LocalStorage(tmp_path / "state")
    assert storage.initialize().ready is True
    repository = ConfigAuditRepository(storage.database_path)

    repository.record_config_change(
        provider_id="openai",
        configuration={
            "model_id": "gpt-test",
            "timeout_seconds": 30,
            "max_retries": 1,
            "api_key": "plain-secret-must-not-persist",
            "Authorization": "Bearer another-plain-secret",
        },
        success=True,
    )

    records = repository.list_recent()
    database_contents = storage.database_path.read_bytes()

    assert len(records) == 1
    assert records[0].provider_id == "openai"
    assert records[0].summary == {
        "credential_present": True,
        "max_retries": 1,
        "model_id": "gpt-test",
        "timeout_seconds": 30,
    }
    assert records[0].success is True
    assert b"plain-secret-must-not-persist" not in database_contents
    assert b"another-plain-secret" not in database_contents
