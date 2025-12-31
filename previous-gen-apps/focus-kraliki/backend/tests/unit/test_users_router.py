import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from fastapi import HTTPException
from app.routers.users import (
    get_profile,
    update_profile,
    get_preferences,
    update_preferences,
)
from app.models.user import User, Role, UserStatus
from app.schemas.user import UserProfileUpdate, UserPreferences, UserResponse


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = "test-user-id"
    user.email = "test@example.com"
    user.firstName = "Test"
    user.lastName = "User"
    user.username = "testuser"
    user.role = Role.AGENT
    user.status = UserStatus.ACTIVE
    user.createdAt = datetime(2024, 1, 1)
    user.usageCount = 10
    user.isPremium = False
    user.activeWorkspaceId = "workspace-123"
    user.preferences = {"theme": "dark", "notifications": True}
    return user


class TestUsersRouter:
    @patch("app.routers.users.get_current_user")
    async def test_get_profile(self, mock_get_user, mock_user):
        """Test getting user profile."""
        mock_get_user.return_value = mock_user

        response = await get_profile(current_user=mock_user)

        assert isinstance(response, UserResponse)
        assert response.id == mock_user.id
        assert response.email == mock_user.email

    @patch("app.routers.users.get_current_user")
    @patch("app.routers.users.get_db")
    async def test_update_profile_success(
        self, mock_get_db, mock_get_user, mock_user, mock_db
    ):
        """Test successful profile update."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db

        update_data = UserProfileUpdate(firstName="Updated", lastName="Name")
        response = await update_profile(
            profile_update=update_data, current_user=mock_user, db=mock_db
        )

        assert isinstance(response, UserResponse)
        assert mock_user.firstName == "Updated"
        assert mock_user.lastName == "Name"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)

    @patch("app.routers.users.get_current_user")
    @patch("app.routers.users.get_db")
    async def test_update_profile_partial_update(
        self, mock_get_db, mock_get_user, mock_user, mock_db
    ):
        """Test partial profile update."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db

        original_last_name = mock_user.lastName
        update_data = UserProfileUpdate(firstName="NewFirst")
        response = await update_profile(
            profile_update=update_data, current_user=mock_user, db=mock_db
        )

        assert mock_user.firstName == "NewFirst"
        assert mock_user.lastName == original_last_name
        mock_db.commit.assert_called_once()

    @patch("app.routers.users.get_current_user")
    async def test_get_preferences_with_preferences(self, mock_get_user, mock_user):
        """Test getting user preferences when preferences exist."""
        mock_get_user.return_value = mock_user

        response = await get_preferences(current_user=mock_user)

        assert response == {"theme": "dark", "notifications": True}

    @patch("app.routers.users.get_current_user")
    async def test_get_preferences_without_preferences(self, mock_get_user, mock_user):
        """Test getting user preferences when no preferences exist."""
        mock_user.preferences = None
        mock_get_user.return_value = mock_user

        response = await get_preferences(current_user=mock_user)

        assert response == {}

    @patch("app.routers.users.get_current_user")
    @patch("app.routers.users.get_db")
    async def test_update_preferences_merge(
        self, mock_get_db, mock_get_user, mock_user, mock_db
    ):
        """Test updating preferences merges with existing."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db

        new_prefs = UserPreferences(theme="light")
        response = await update_preferences(
            preferences=new_prefs, current_user=mock_user, db=mock_db
        )

        assert response["success"] is True
        assert response["preferences"]["theme"] == "light"
        assert response["preferences"]["notifications"] is True
        assert mock_user.preferences == response["preferences"]
        mock_db.commit.assert_called_once()

    @patch("app.routers.users.get_current_user")
    @patch("app.routers.users.get_db")
    async def test_update_preferences_new_preference(
        self, mock_get_db, mock_get_user, mock_user, mock_db
    ):
        """Test adding a new preference."""
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db

        new_prefs = UserPreferences(workHoursStart="09:00")
        response = await update_preferences(
            preferences=new_prefs, current_user=mock_user, db=mock_db
        )

        assert response["success"] is True
        assert response["preferences"]["workHoursStart"] == "09:00"
        assert response["preferences"]["theme"] == "dark"
        assert response["preferences"]["notifications"] is True
        mock_db.commit.assert_called_once()

    @patch("app.routers.users.get_current_user")
    @patch("app.routers.users.get_db")
    async def test_update_preferences_from_none(
        self, mock_get_db, mock_get_user, mock_user, mock_db
    ):
        """Test updating preferences when user has no existing preferences."""
        mock_user.preferences = None
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = mock_db

        new_prefs = UserPreferences(theme="dark")
        response = await update_preferences(
            preferences=new_prefs, current_user=mock_user, db=mock_db
        )

        assert response["success"] is True
        assert response["preferences"]["theme"] == "dark"
        mock_db.commit.assert_called_once()
