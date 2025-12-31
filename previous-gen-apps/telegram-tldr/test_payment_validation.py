import sys
sys.path.insert(0, '.')

from unittest.mock import patch, MagicMock
import asyncio

async def test_validation():
    # Test 1: Valid prices should pass
    print("Test 1: Valid prices")
    with patch('app.core.config.get_settings') as mock_settings:
        mock = MagicMock()
        mock.subscription_price_stars = 250
        mock.newsletter_price_stars = 250
        mock.telegram_webhook_url = ""
        mock.telegram_webhook_secret = None
        mock_settings.return_value = mock
        
        from app.main import lifespan
        async with lifespan(None):
            print("  ✅ Valid prices passed validation")
    
    # Test 2: Invalid subscription price should fail
    print("\nTest 2: Invalid subscription price (0)")
    with patch('app.core.config.get_settings') as mock_settings:
        mock = MagicMock()
        mock.subscription_price_stars = 0
        mock.newsletter_price_stars = 250
        mock.telegram_webhook_url = ""
        mock.telegram_webhook_secret = None
        mock_settings.return_value = mock
        
        from app.main import lifespan
        try:
            async with lifespan(None):
                print("  ❌ Should have raised error!")
                return False
        except RuntimeError as e:
            if "SUBSCRIPTION_PRICE_STARS" in str(e):
                print("  ✅ Correctly rejected invalid price")
            else:
                print(f"  ❌ Wrong error: {e}")
                return False
    
    # Test 3: Invalid newsletter price should fail
    print("\nTest 3: Invalid newsletter price (0)")
    with patch('app.core.config.get_settings') as mock_settings:
        mock = MagicMock()
        mock.subscription_price_stars = 250
        mock.newsletter_price_stars = 0
        mock.telegram_webhook_url = ""
        mock.telegram_webhook_secret = None
        mock_settings.return_value = mock
        
        from app.main import lifespan
        try:
            async with lifespan(None):
                print("  ❌ Should have raised error!")
                return False
        except RuntimeError as e:
            if "NEWSLETTER_PRICE_STARS" in str(e):
                print("  ✅ Correctly rejected invalid price")
            else:
                print(f"  ❌ Wrong error: {e}")
                return False
    
    print("\n✅ All validation tests passed!")
    return True

if __name__ == '__main__':
    success = asyncio.run(test_validation())
    sys.exit(0 if success else 1)
