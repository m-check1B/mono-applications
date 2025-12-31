import pytest
import os
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class TestPromptLibraryStructure:
    """Test that prompt library is properly structured."""

    def test_prompts_directory_exists(self):
        """Prompts directory should exist."""
        assert PROMPTS_DIR.exists(), "prompts/ directory not found"

    def test_required_directories_exist(self):
        """Required subdirectories should exist."""
        required_dirs = [
            "orchestrator",
            "workers/gemini",
            "workers/codex",
            "patterns",
        ]
        for dir_path in required_dirs:
            full_path = PROMPTS_DIR / dir_path
            assert full_path.exists() and full_path.is_dir(), (
                f"Missing directory: {dir_path}"
            )

    def test_readme_exists(self):
        """README.md should exist in prompts directory."""
        readme_path = PROMPTS_DIR / "README.md"
        assert readme_path.exists(), "prompts/README.md not found"


class TestOrchestratorPrompts:
    """Test orchestrator prompts (Claude Opus)."""

    def test_all_orchestrator_prompts_exist(self):
        """All required orchestrator prompts should exist."""
        required_prompts = [
            "task-decomposition.md",
            "quality-control.md",
            "context-management.md",
            "strategic-planning.md",
        ]
        for prompt_file in required_prompts:
            path = PROMPTS_DIR / "orchestrator" / prompt_file
            assert path.exists(), f"Missing orchestrator prompt: {prompt_file}"

    def test_orchestrator_prompts_are_valid_markdown(self):
        """All orchestrator prompts should be valid markdown."""
        for prompt_file in (PROMPTS_DIR / "orchestrator").glob("*.md"):
            content = prompt_file.read_text()
            assert len(content) > 100, f"{prompt_file.name} is too short"
            assert "```" in content or "##" in content, (
                f"{prompt_file.name} may not be formatted correctly"
            )


class TestWorkerPromptsGemini:
    """Test Gemini worker prompts."""

    def test_all_gemini_prompts_exist(self):
        """All required Gemini prompts should exist."""
        required_prompts = [
            "frontend-builder.md",
            "researcher.md",
            "documentation.md",
        ]
        for prompt_file in required_prompts:
            path = PROMPTS_DIR / "workers" / "gemini" / prompt_file
            assert path.exists(), f"Missing Gemini prompt: {prompt_file}"


class TestWorkerPromptsCodex:
    """Test Codex worker prompts."""

    def test_all_codex_prompts_exist(self):
        """All required Codex prompts should exist."""
        required_prompts = [
            "backend-builder.md",
            "code-auditor.md",
            "security-analyzer.md",
        ]
        for prompt_file in required_prompts:
            path = PROMPTS_DIR / "workers" / "codex" / prompt_file
            assert path.exists(), f"Missing Codex prompt: {prompt_file}"


class TestPatternPrompts:
    """Test pattern prompts."""

    def test_all_pattern_prompts_exist(self):
        """All required pattern prompts should exist."""
        required_prompts = [
            "build-audit-fix.md",
            "parallel-execution.md",
            "hard-problem-voting.md",
            "research-implement.md",
        ]
        for prompt_file in required_prompts:
            path = PROMPTS_DIR / "patterns" / prompt_file
            assert path.exists(), f"Missing pattern prompt: {prompt_file}"

    def test_pattern_prompts_describe_workflow(self):
        """Each pattern should describe a workflow."""
        for prompt_file in (PROMPTS_DIR / "patterns").glob("*.md"):
            content = prompt_file.read_text()
            assert "##" in content, f"{prompt_file.name} lacks markdown headers"
            assert "## " in content or "#" in content, (
                f"{prompt_file.name} should have title sections"
            )


class TestPromptQuality:
    """Test quality of prompts."""

    def test_all_prompts_have_minimal_length(self):
        """All prompts should have minimum content length."""
        min_length = 100
        for prompt_file in PROMPTS_DIR.rglob("*.md"):
            if prompt_file.name == "README.md":
                continue
            content = prompt_file.read_text()
            assert len(content) >= min_length, (
                f"{prompt_file.relative_to(PROMPTS_DIR)} is too short ({len(content)} chars)"
            )

    def test_all_prompts_use_code_blocks_or_examples(self):
        """All prompts should include code blocks or examples."""
        for prompt_file in PROMPTS_DIR.rglob("*.md"):
            if prompt_file.name == "README.md":
                continue
            content = prompt_file.read_text()
            has_example = (
                "```" in content
                or "## Example" in content
                or "## Usage Example" in content
            )
            assert has_example, f"{prompt_file.relative_to(PROMPTS_DIR)} lacks examples"

    def test_prompts_have_consistent_formatting(self):
        """Prompts should use consistent markdown formatting."""
        for prompt_file in PROMPTS_DIR.rglob("*.md"):
            content = prompt_file.read_text()
            assert content.startswith("#"), (
                f"{prompt_file.relative_to(PROMPTS_DIR)} should start with # title"
            )
            assert "##" in content, (
                f"{prompt_file.relative_to(PROMPTS_DIR)} should have ## sections"
            )

    def test_orchestrator_and_worker_prompts_have_role_definition(self):
        """Orchestrator and worker prompts should define roles (patterns don't need roles)."""
        for prompt_file in list(PROMPTS_DIR.glob("orchestrator/*.md")) + list(
            PROMPTS_DIR.glob("workers/*/*.md")
        ):
            if prompt_file.name == "README.md":
                continue
            content = prompt_file.read_text()
            has_role = "**Role:" in content or "## Role" in content
            assert has_role, (
                f"{prompt_file.relative_to(PROMPTS_DIR)} missing role definition"
            )


class TestPromptReadme:
    """Test prompt library README."""

    def test_readme_has_documentation_sections(self):
        """README should have documentation sections."""
        readme_path = PROMPTS_DIR / "README.md"
        content = readme_path.read_text()

        required_sections = [
            "## Directory Structure",
            "## Quick Start",
            "## Usage Examples",
        ]

        for section in required_sections:
            assert section in content, f"README missing section: {section}"

    def test_readme_lists_all_prompts(self):
        """README should list all available prompts."""
        readme_path = PROMPTS_DIR / "README.md"
        content = readme_path.read_text()

        orchestrator_prompts = [
            p.name for p in (PROMPTS_DIR / "orchestrator").glob("*.md")
        ]
        for prompt in orchestrator_prompts:
            assert prompt in content, f"README doesn't mention {prompt}"


class TestPromptIntegration:
    """Test that prompts are ready for use."""

    def test_all_prompts_are_markdown_files(self):
        """All prompt files should be .md files."""
        for prompt_file in PROMPTS_DIR.rglob("*"):
            if prompt_file.is_file() and prompt_file.name != "README.md":
                assert prompt_file.suffix == ".md", (
                    f"{prompt_file.name} is not a .md file"
                )

    def test_no_empty_prompt_files(self):
        """No prompt files should be empty."""
        for prompt_file in PROMPTS_DIR.rglob("*.md"):
            content = prompt_file.read_text().strip()
            assert len(content) > 0, f"{prompt_file.relative_to(PROMPTS_DIR)} is empty"

    def test_prompts_have_descriptive_titles(self):
        """Each prompt should start with a descriptive title."""
        for prompt_file in PROMPTS_DIR.rglob("*.md"):
            if prompt_file.name == "README.md":
                continue
            first_line = prompt_file.read_text().split("\n")[0]
            assert first_line.startswith("# "), (
                f"{prompt_file.name} should start with # title"
            )
            assert len(first_line) > 10, f"{prompt_file.name} title is too short"

    def test_all_prompts_have_examples(self):
        """Each prompt should include practical examples."""
        for prompt_file in PROMPTS_DIR.rglob("*.md"):
            if prompt_file.name == "README.md":
                continue
            content = prompt_file.read_text()
            has_example = (
                "```" in content or "## Example" in content or "## Usage" in content
            )
            assert has_example, f"{prompt_file.relative_to(PROMPTS_DIR)} lacks examples"
