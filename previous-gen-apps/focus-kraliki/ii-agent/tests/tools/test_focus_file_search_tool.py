"""Unit tests for the FocusFileSearchTool class.

This module contains tests for the FocusFileSearchTool,
which enables semantic search over user's knowledge base.
"""

import pytest
from unittest.mock import patch, AsyncMock
from ii_agent.tools.focus_tools import FocusFileSearchTool
from ii_agent.tools.base import ToolImplOutput

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_file_search_successful():
    """Test that a successful file search returns the expected output."""
    tool = FocusFileSearchTool(
        focus_api_base_url="http://127.0.0.1:3017",
        agent_token="test_token"
    )

    # Mock API response
    mock_response = {
        "answer": "You have three priorities this week: complete the API redesign, review pull requests, and prepare for the team meeting.",
        "citations": [
            {
                "documentName": "Weekly Planning - Week 45",
                "knowledgeItemId": "item_123",
                "excerpt": "This week's priorities: 1. API redesign 2. Code reviews 3. Team meeting prep"
            },
            {
                "documentName": "Project Notes",
                "knowledgeItemId": "item_456",
                "excerpt": "Need to focus on API redesign and getting it production ready"
            }
        ]
    }

    with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        result = await tool.run_impl({
            "query": "What are my priorities this week?"
        })

        # Verify API was called correctly
        mock_request.assert_called_once_with(
            "POST",
            "/ai/file-search/query",
            json_data={"query": "What are my priorities this week?"}
        )

        # Check result structure
        assert isinstance(result, ToolImplOutput)
        assert result.auxiliary_data["success"] is True
        assert result.auxiliary_data["query"] == "What are my priorities this week?"

        # Check output contains answer and citations
        output = result.tool_output
        assert "**Answer:**" in output
        assert "You have three priorities" in output
        assert "**Sources:**" in output
        assert "Weekly Planning - Week 45" in output
        assert "item_123" in output


@pytest.mark.asyncio
async def test_file_search_with_context():
    """Test file search with additional context."""
    tool = FocusFileSearchTool(
        focus_api_base_url="http://127.0.0.1:3017",
        agent_token="test_token"
    )

    mock_response = {
        "answer": "The database migration was decided to use PostgreSQL with gradual rollout.",
        "citations": []
    }

    with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        result = await tool.run_impl({
            "query": "database migration decisions",
            "context": {"project_id": "proj_123"}
        })

        # Verify context was passed
        mock_request.assert_called_once_with(
            "POST",
            "/ai/file-search/query",
            json_data={
                "query": "database migration decisions",
                "context": {"project_id": "proj_123"}
            }
        )

        assert result.auxiliary_data["success"] is True


@pytest.mark.asyncio
async def test_file_search_no_citations():
    """Test file search with no citations in response."""
    tool = FocusFileSearchTool(
        focus_api_base_url="http://127.0.0.1:3017",
        agent_token="test_token"
    )

    mock_response = {
        "answer": "I couldn't find specific information about that topic.",
        "citations": []
    }

    with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        result = await tool.run_impl({
            "query": "unknown topic"
        })

        # Check result
        assert result.auxiliary_data["success"] is True
        output = result.tool_output
        assert "**Answer:**" in output
        assert "**Sources:**" not in output  # No sources section if no citations


@pytest.mark.asyncio
async def test_file_search_api_error():
    """Test handling of API errors."""
    tool = FocusFileSearchTool(
        focus_api_base_url="http://127.0.0.1:3017",
        agent_token="test_token"
    )

    with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("API connection failed")

        result = await tool.run_impl({
            "query": "test query"
        })

        # Check error handling
        assert result.auxiliary_data["success"] is False
        assert "Failed to search knowledge base" in result.tool_output
        assert "API connection failed" in result.tool_output
        assert result.auxiliary_data["error"] == "API connection failed"


@pytest.mark.asyncio
async def test_file_search_long_excerpt_truncation():
    """Test that long excerpts are truncated properly."""
    tool = FocusFileSearchTool(
        focus_api_base_url="http://127.0.0.1:3017",
        agent_token="test_token"
    )

    # Create a very long excerpt
    long_text = "A" * 200
    mock_response = {
        "answer": "Test answer",
        "citations": [
            {
                "documentName": "Long Document",
                "knowledgeItemId": "item_789",
                "excerpt": long_text
            }
        ]
    }

    with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        result = await tool.run_impl({
            "query": "test"
        })

        # Check that excerpt was truncated
        output = result.tool_output
        assert "..." in output  # Truncation indicator
        # The exact excerpt in output should be less than original
        assert len(output) < len(long_text) + 100


@pytest.mark.asyncio
async def test_file_search_tool_schema():
    """Test that the tool has correct schema definition."""
    tool = FocusFileSearchTool(
        focus_api_base_url="http://127.0.0.1:3017",
        agent_token="test_token"
    )

    # Check tool properties
    assert tool.name == "focus_file_search_query"
    assert "Search the user's knowledge base" in tool.description

    # Check input schema
    schema = tool.input_schema
    assert schema["type"] == "object"
    assert "query" in schema["properties"]
    assert "context" in schema["properties"]
    assert "query" in schema["required"]
    assert "context" not in schema["required"]  # Optional


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
