"""
Unit tests for app.models package exports.
Ensures models/__init__.py stays in sync with model modules.
"""


def test_models_init_exports_all_expected_symbols():
    """app.models should export the full set of expected symbols."""
    from app import models

    expected = {
        "User",
        "Task",
        "Project",
        "Session",
        "Event",
        "TimeEntry",
        "VoiceRecording",
        "WorkflowTemplate",
        "AIConversation",
        "ShadowProfile",
        "ShadowInsight",
        "ItemType",
        "KnowledgeItem",
        "FileSearchStore",
        "FileSearchDocument",
        "Workspace",
        "WorkspaceMember",
        "RequestTelemetry",
        "CommandHistory",
        "AgentSession",
        "AgentSessionEvent",
        "SearchIndex",
    }

    assert set(models.__all__) == expected
    for name in models.__all__:
        assert hasattr(models, name)
