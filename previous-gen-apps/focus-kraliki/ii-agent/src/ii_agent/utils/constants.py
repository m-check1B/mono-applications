from enum import Enum


UPLOAD_FOLDER_NAME = "uploaded_files"
COMPLETE_MESSAGE = "Completed the task."
DEFAULT_MODEL = "claude-opus-4-20250514"

TOKEN_BUDGET = 120_000
SUMMARY_MAX_TOKENS = 32_000
VISIT_WEB_PAGE_MAX_OUTPUT_LENGTH = 40_000

# Workspace path alias used in terminal and file management
# This constant ensures consistency across all managers
WORKSPACE_ALIAS = ".WORKING_DIR"


class WorkSpaceMode(Enum):
    DOCKER = "docker"
    E2B = "e2b"
    LOCAL = "local"

    def __str__(self):
        return self.value
