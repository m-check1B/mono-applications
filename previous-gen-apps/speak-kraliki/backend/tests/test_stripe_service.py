"""Stripe Service Tests for Speak by Kraliki."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.stripe_service import StripeService, stripe_service


@pytest.fixture
def stripe_service_instance():
    """Create a fresh StripeService instance for testing."""
    return StripeService()


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_company():
    """Mock company object."""
    company = Mock()
    company.id = uuid4()
    company.stripe_customer_id = None
    company.plan = "free"
    company.stripe_subscription_id = None
    return company


@pytest.fixture
def mock_stripe_customer():
    """Mock Stripe customer."""
    customer = Mock()
    customer.id = "cus_test123"
    return customer


@pytest.fixture
def mock_stripe_session():
    """Mock Stripe checkout session."""
    session = Mock()
    session.id = "cs_test123"
    session.url = "https://checkout.stripe.com/pay/cs_test123"
    session.subscription = "sub_test123"
    session.metadata = {"company_id": str(uuid4()), "plan": "personal"}
    return session


@pytest.fixture
def mock_stripe_subscription():
    """Mock Stripe subscription."""
    subscription = Mock()
    subscription.id = "sub_test123"
    subscription.metadata = {"company_id": str(uuid4()), "plan": "premium"}
    return subscription


class TestStripeServiceInitialization:
    """Test StripeService initialization."""

    def test_stripe_service_init(self, stripe_service_instance):
        """Test that StripeService initializes correctly."""
        assert stripe_service_instance.price_map is not None
        assert "personal" in stripe_service_instance.price_map
        assert "premium" in stripe_service_instance.price_map
        assert "pro" in stripe_service_instance.price_map


class TestCreateCustomer:
    """Test customer creation."""

    @pytest.mark.asyncio
    async def test_create_new_customer(
        self,
        stripe_service_instance,
        mock_db_session,
        mock_company,
        mock_stripe_customer,
    ):
        """Test creating a new Stripe customer."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_company
        mock_db_session.execute.return_value = mock_result

        with patch("stripe.Customer.create", return_value=mock_stripe_customer):
            customer_id = await stripe_service_instance.create_customer(
                db=mock_db_session,
                company_id=mock_company.id,
                email="test@example.com",
                name="Test Company",
            )

            assert customer_id == "cus_test123"
            assert mock_company.stripe_customer_id == "cus_test123"
            mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_customer_already_exists(
        self, stripe_service_instance, mock_db_session, mock_company
    ):
        """Test when customer already exists."""
        mock_company.stripe_customer_id = "cus_existing123"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_company
        mock_db_session.execute.return_value = mock_result

        with patch("stripe.Customer.create") as mock_create:
            customer_id = await stripe_service_instance.create_customer(
                db=mock_db_session,
                company_id=mock_company.id,
                email="test@example.com",
                name="Test Company",
            )

            assert customer_id == "cus_existing123"
            mock_create.assert_not_called()
            mock_db_session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_create_customer_no_company(
        self, stripe_service_instance, mock_db_session, mock_stripe_customer
    ):
        """Test creating customer when company doesn't exist in database."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with patch("stripe.Customer.create", return_value=mock_stripe_customer):
            customer_id = await stripe_service_instance.create_customer(
                db=mock_db_session,
                company_id=uuid4(),
                email="test@example.com",
                name="Test Company",
            )

            assert customer_id == "cus_test123"
            mock_db_session.commit.assert_not_awaited()


class TestCreateCheckoutSession:
    """Test checkout session creation."""

    @pytest.mark.asyncio
    async def test_create_checkout_session_personal(
        self, stripe_service_instance, mock_stripe_session
    ):
        """Test creating checkout session for personal plan."""
        company_id = uuid4()
        customer_id = "cus_test123"

        mock_session_obj = Mock()
        mock_session_obj.id = "cs_test123"
        mock_session_obj.url = "https://checkout.stripe.com/pay/cs_test123"

        with patch("stripe.checkout.Session.create", return_value=mock_session_obj):
            url = await stripe_service_instance.create_checkout_session(
                company_id=company_id,
                customer_id=customer_id,
                plan_name="personal",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

            assert url == "https://checkout.stripe.com/pay/cs_test123"
            stripe.checkout.Session.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_checkout_session_premium(
        self, stripe_service_instance, mock_stripe_session
    ):
        """Test creating checkout session for premium plan."""
        company_id = uuid4()
        customer_id = "cus_test123"

        mock_session_obj = Mock()
        mock_session_obj.id = "cs_test123"
        mock_session_obj.url = "https://checkout.stripe.com/pay/cs_test123"

        with patch("stripe.checkout.Session.create", return_value=mock_session_obj):
            url = await stripe_service_instance.create_checkout_session(
                company_id=company_id,
                customer_id=customer_id,
                plan_name="premium",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

            assert url == "https://checkout.stripe.com/pay/cs_test123"

    @pytest.mark.asyncio
    async def test_create_checkout_session_pro(
        self, stripe_service_instance, mock_stripe_session
    ):
        """Test creating checkout session for pro plan."""
        company_id = uuid4()
        customer_id = "cus_test123"

        mock_session_obj = Mock()
        mock_session_obj.id = "cs_test123"
        mock_session_obj.url = "https://checkout.stripe.com/pay/cs_test123"

        with patch("stripe.checkout.Session.create", return_value=mock_session_obj):
            url = await stripe_service_instance.create_checkout_session(
                company_id=company_id,
                customer_id=customer_id,
                plan_name="pro",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

            assert url == "https://checkout.stripe.com/pay/cs_test123"

    @pytest.mark.asyncio
    async def test_create_checkout_session_invalid_plan(self, stripe_service_instance):
        """Test creating checkout session with invalid plan."""
        with pytest.raises(ValueError, match="Invalid plan name"):
            await stripe_service_instance.create_checkout_session(
                company_id=uuid4(),
                customer_id="cus_test123",
                plan_name="invalid_plan",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )


class TestHandleWebhook:
    """Test webhook handling."""

    @pytest.mark.asyncio
    async def test_handle_webhook_checkout_completed(
        self,
        stripe_service_instance,
        mock_db_session,
        mock_company,
        mock_stripe_session,
    ):
        """Test handling checkout.session.completed webhook event."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_company
        mock_db_session.execute.return_value = mock_result

        mock_event = Mock()
        mock_event.type = "checkout.session.completed"
        mock_event.data.object = mock_stripe_session

        with patch("stripe.Webhook.construct_event", return_value=mock_event):
            await stripe_service_instance.handle_webhook(
                payload=b"test_payload", sig_header="test_sig", db=mock_db_session
            )

            assert mock_company.plan == "personal"
            assert mock_company.stripe_subscription_id == "sub_test123"
            mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handle_webhook_subscription_updated(
        self,
        stripe_service_instance,
        mock_db_session,
        mock_company,
        mock_stripe_subscription,
    ):
        """Test handling customer.subscription.updated webhook event."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_company
        mock_db_session.execute.return_value = mock_result

        mock_event = Mock()
        mock_event.type = "customer.subscription.updated"
        mock_event.data.object = mock_stripe_subscription

        with patch("stripe.Webhook.construct_event", return_value=mock_event):
            await stripe_service_instance.handle_webhook(
                payload=b"test_payload", sig_header="test_sig", db=mock_db_session
            )

    @pytest.mark.asyncio
    async def test_handle_webhook_subscription_deleted(
        self,
        stripe_service_instance,
        mock_db_session,
        mock_company,
        mock_stripe_subscription,
    ):
        """Test handling customer.subscription.deleted webhook event."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_company
        mock_db_session.execute.return_value = mock_result

        mock_event = Mock()
        mock_event.type = "customer.subscription.deleted"
        mock_event.data.object = mock_stripe_subscription

        with patch("stripe.Webhook.construct_event", return_value=mock_event):
            await stripe_service_instance.handle_webhook(
                payload=b"test_payload", sig_header="test_sig", db=mock_db_session
            )

            assert mock_company.plan == "free"
            assert mock_company.stripe_subscription_id is None
            mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handle_webhook_invalid_payload(
        self, stripe_service_instance, mock_db_session
    ):
        """Test webhook with invalid payload."""
        with patch(
            "stripe.Webhook.construct_event", side_effect=ValueError("Invalid payload")
        ):
            with pytest.raises(ValueError, match="Invalid payload"):
                await stripe_service_instance.handle_webhook(
                    payload=b"invalid", sig_header="test_sig", db=mock_db_session
                )

    @pytest.mark.asyncio
    async def test_handle_webhook_invalid_signature(
        self, stripe_service_instance, mock_db_session
    ):
        """Test webhook with invalid signature."""
        with patch(
            "stripe.Webhook.construct_event", side_effect=Exception("Invalid signature")
        ):
            with pytest.raises(ValueError):
                await stripe_service_instance.handle_webhook(
                    payload=b"test_payload",
                    sig_header="invalid_sig",
                    db=mock_db_session,
                )

    @pytest.mark.asyncio
    async def test_handle_webhook_unknown_event_type(
        self, stripe_service_instance, mock_db_session
    ):
        """Test webhook with unknown event type."""
        mock_event = Mock()
        mock_event.type = "unknown.event"

        with patch("stripe.Webhook.construct_event", return_value=mock_event):
            await stripe_service_instance.handle_webhook(
                payload=b"test_payload", sig_header="test_sig", db=mock_db_session
            )


class TestHandleSubscriptionSuccess:
    """Test subscription success handling."""

    @pytest.mark.asyncio
    async def test_handle_subscription_success(
        self,
        stripe_service_instance,
        mock_db_session,
        mock_company,
        mock_stripe_session,
    ):
        """Test handling successful subscription."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_company
        mock_db_session.execute.return_value = mock_result

        await stripe_service_instance._handle_subscription_success(
            mock_stripe_session, mock_db_session
        )

        assert mock_company.plan == "personal"
        assert mock_company.stripe_subscription_id == "sub_test123"
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handle_subscription_success_no_company_id(
        self, stripe_service_instance, mock_db_session, mock_stripe_session
    ):
        """Test handling subscription success without company_id."""
        mock_stripe_session.metadata = {}

        await stripe_service_instance._handle_subscription_success(
            mock_stripe_session, mock_db_session
        )

        mock_db_session.execute.assert_not_awaited()
        mock_db_session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_handle_subscription_success_company_not_found(
        self, stripe_service_instance, mock_db_session, mock_stripe_session
    ):
        """Test handling subscription success when company not found."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        await stripe_service_instance._handle_subscription_success(
            mock_stripe_session, mock_db_session
        )

        mock_db_session.commit.assert_not_awaited()


class TestHandleSubscriptionUpdated:
    """Test subscription update handling."""

    @pytest.mark.asyncio
    async def test_handle_subscription_updated(
        self,
        stripe_service_instance,
        mock_db_session,
        mock_company,
        mock_stripe_subscription,
    ):
        """Test handling subscription update."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_company
        mock_db_session.execute.return_value = mock_result

        await stripe_service_instance._handle_subscription_updated(
            mock_stripe_subscription, mock_db_session
        )


class TestHandleSubscriptionDeleted:
    """Test subscription deletion handling."""

    @pytest.mark.asyncio
    async def test_handle_subscription_deleted(
        self,
        stripe_service_instance,
        mock_db_session,
        mock_company,
        mock_stripe_subscription,
    ):
        """Test handling subscription deletion."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_company
        mock_db_session.execute.return_value = mock_result

        await stripe_service_instance._handle_subscription_deleted(
            mock_stripe_subscription, mock_db_session
        )

        assert mock_company.plan == "free"
        assert mock_company.stripe_subscription_id is None
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handle_subscription_deleted_no_company_id(
        self, stripe_service_instance, mock_db_session, mock_stripe_subscription
    ):
        """Test handling subscription deletion without company_id."""
        mock_stripe_subscription.metadata = {}

        await stripe_service_instance._handle_subscription_deleted(
            mock_stripe_subscription, mock_db_session
        )

        mock_db_session.execute.assert_not_awaited()
        mock_db_session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_handle_subscription_deleted_company_not_found(
        self, stripe_service_instance, mock_db_session, mock_stripe_subscription
    ):
        """Test handling subscription deletion when company not found."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        await stripe_service_instance._handle_subscription_deleted(
            mock_stripe_subscription, mock_db_session
        )

        mock_db_session.commit.assert_not_awaited()
