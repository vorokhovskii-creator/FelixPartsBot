import sys
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Set required environment variables before importing
os.environ.setdefault('TELEGRAM_TOKEN', 'test_token')
os.environ.setdefault('BOT_TOKEN', 'test_token')

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../felix_hub/backend'))


class TestTelegramNotifications(unittest.TestCase):
    """Test suite for Telegram admin notifications."""
    
    def setUp(self):
        """Set up test fixtures."""
        from app import app, db
        
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        
        self.app = app
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        self.db = db
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_format_order_summary(self):
        """Test order summary formatting."""
        from models import Order
        from services.telegram import _format_order_summary
        
        order = Order(
            mechanic_name='Test Mechanic',
            telegram_id='123456789',
            category='Тормоза',
            vin='TEST1234',
            car_number='ABC123',
            selected_parts=[
                {'name': 'Передние колодки', 'quantity': 2},
                {'name': 'Диски передние', 'quantity': 1}
            ],
            is_original=False
        )
        
        parts_text, car_identifier = _format_order_summary(order)
        
        self.assertIn('Передние колодки', parts_text)
        self.assertIn('Диски передние', parts_text)
        self.assertEqual(car_identifier, 'ABC123')
    
    def test_get_admin_chat_ids(self):
        """Test parsing admin chat IDs from environment."""
        from services.telegram import _get_admin_chat_ids
        
        # Test with no env variable
        with patch.dict(os.environ, {}, clear=True):
            chat_ids = _get_admin_chat_ids()
            self.assertEqual(chat_ids, [])
        
        # Test with single chat ID
        with patch.dict(os.environ, {'ADMIN_CHAT_IDS': '123456789'}):
            chat_ids = _get_admin_chat_ids()
            self.assertEqual(chat_ids, ['123456789'])
        
        # Test with multiple chat IDs
        with patch.dict(os.environ, {'ADMIN_CHAT_IDS': '123456789, 987654321,  111222333'}):
            chat_ids = _get_admin_chat_ids()
            self.assertEqual(chat_ids, ['123456789', '987654321', '111222333'])
    
    def test_generate_admin_order_link(self):
        """Test admin order link generation."""
        from services.telegram import _generate_admin_order_link
        
        with patch.dict(os.environ, {'FRONTEND_URL': 'https://example.com'}):
            link = _generate_admin_order_link(42)
            self.assertEqual(link, 'https://example.com/#/admin/orders/42')
    
    @patch('services.telegram.requests.post')
    def test_send_telegram_message_success(self, mock_post):
        """Test successful message sending."""
        from services.telegram import _send_telegram_message
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            result = _send_telegram_message('123456789', 'Test message')
            self.assertTrue(result)
            mock_post.assert_called_once()
    
    @patch('services.telegram.requests.post')
    def test_send_telegram_message_rate_limit(self, mock_post):
        """Test handling of rate limits."""
        from services.telegram import _send_telegram_message
        
        # First call returns 429 (rate limit), second call succeeds
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_429.json.return_value = {'parameters': {'retry_after': 1}}
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        
        mock_post.side_effect = [mock_response_429, mock_response_200]
        
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            with patch('services.telegram.time.sleep'):  # Skip actual sleep
                result = _send_telegram_message('123456789', 'Test message')
                self.assertTrue(result)
                self.assertEqual(mock_post.call_count, 2)
    
    @patch('services.telegram.requests.post')
    def test_send_telegram_message_retry_exponential_backoff(self, mock_post):
        """Test exponential backoff on retries."""
        from services.telegram import _send_telegram_message
        
        # Simulate timeout errors that trigger retries
        mock_post.side_effect = Exception("Network error")
        
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            with patch('services.telegram.time.sleep') as mock_sleep:
                result = _send_telegram_message('123456789', 'Test message')
                self.assertFalse(result)
                
                # Check that we retried MAX_RETRIES times
                self.assertEqual(mock_post.call_count, 3)
                
                # Check exponential backoff: 1s, 2s
                self.assertEqual(mock_sleep.call_count, 2)
                mock_sleep.assert_any_call(1)  # 2^0
                mock_sleep.assert_any_call(2)  # 2^1
    
    @patch('services.telegram.requests.post')
    def test_send_telegram_message_client_error_no_retry(self, mock_post):
        """Test that client errors (4xx except 429) don't trigger retries."""
        from services.telegram import _send_telegram_message
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad request'
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            result = _send_telegram_message('123456789', 'Test message')
            self.assertFalse(result)
            # Should only try once for 4xx errors
            self.assertEqual(mock_post.call_count, 1)
    
    @patch('services.telegram._send_telegram_message')
    def test_notify_admin_new_order_success(self, mock_send):
        """Test successful admin notification."""
        from models import Order
        from services.telegram import notify_admin_new_order
        
        mock_send.return_value = True
        
        order = Order(
            mechanic_name='Test Mechanic',
            telegram_id='123456789',
            category='Тормоза',
            vin='TEST1234',
            car_number='ABC123',
            selected_parts=[{'name': 'Передние колодки'}],
            is_original=False
        )
        self.db.session.add(order)
        self.db.session.commit()
        
        with patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'ADMIN_CHAT_IDS': '123456789,987654321',
            'ENABLE_TG_ADMIN_NOTIFS': 'true'
        }):
            result = notify_admin_new_order(order, self.db.session)
            self.assertTrue(result)
            # Should send to both admins
            self.assertEqual(mock_send.call_count, 2)
    
    @patch('services.telegram._send_telegram_message')
    def test_notify_admin_new_order_feature_flag_disabled(self, mock_send):
        """Test that notifications are skipped when feature flag is disabled."""
        from models import Order
        from services.telegram import notify_admin_new_order
        
        order = Order(
            mechanic_name='Test Mechanic',
            telegram_id='123456789',
            category='Тормоза',
            vin='TEST1234',
            selected_parts=[{'name': 'Передние колодки'}],
            is_original=False
        )
        
        with patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'ADMIN_CHAT_IDS': '123456789',
            'ENABLE_TG_ADMIN_NOTIFS': 'false'
        }):
            result = notify_admin_new_order(order)
            # Should return True but not send
            self.assertTrue(result)
            mock_send.assert_not_called()
    
    @patch('services.telegram._send_telegram_message')
    def test_notify_admin_new_order_no_admin_chats(self, mock_send):
        """Test handling when no admin chat IDs are configured."""
        from models import Order
        from services.telegram import notify_admin_new_order
        
        order = Order(
            mechanic_name='Test Mechanic',
            telegram_id='123456789',
            category='Тормоза',
            vin='TEST1234',
            selected_parts=[{'name': 'Передние колодки'}],
            is_original=False
        )
        
        with patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'ADMIN_CHAT_IDS': '',
            'ENABLE_TG_ADMIN_NOTIFS': 'true'
        }):
            result = notify_admin_new_order(order)
            self.assertFalse(result)
            mock_send.assert_not_called()
    
    @patch('services.telegram._send_telegram_message')
    def test_notify_admin_new_order_partial_failure(self, mock_send):
        """Test handling when notification fails for some admins."""
        from models import Order
        from services.telegram import notify_admin_new_order
        
        # First admin succeeds, second fails
        mock_send.side_effect = [True, False]
        
        order = Order(
            mechanic_name='Test Mechanic',
            telegram_id='123456789',
            category='Тормоза',
            vin='TEST1234',
            car_number='ABC123',
            selected_parts=[{'name': 'Передние колодки'}],
            is_original=False
        )
        self.db.session.add(order)
        self.db.session.commit()
        
        with patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'ADMIN_CHAT_IDS': '123456789,987654321',
            'ENABLE_TG_ADMIN_NOTIFS': 'true'
        }):
            result = notify_admin_new_order(order, self.db.session)
            # Should return True if at least one succeeds
            self.assertTrue(result)
            self.assertEqual(mock_send.call_count, 2)
    
    @patch('services.telegram._send_telegram_message')
    def test_notify_admin_logs_to_database(self, mock_send):
        """Test that notifications are logged to database."""
        from models import Order, NotificationLog
        from services.telegram import notify_admin_new_order
        
        mock_send.return_value = True
        
        order = Order(
            mechanic_name='Test Mechanic',
            telegram_id='123456789',
            category='Тормоза',
            vin='TEST1234',
            car_number='ABC123',
            selected_parts=[{'name': 'Передние колодки'}],
            is_original=False
        )
        self.db.session.add(order)
        self.db.session.commit()
        
        with patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'ADMIN_CHAT_IDS': '123456789',
            'ENABLE_TG_ADMIN_NOTIFS': 'true'
        }):
            notify_admin_new_order(order, self.db.session)
            
            # Check that notification was logged
            log = NotificationLog.query.filter_by(
                notification_type='admin_new_order',
                order_id=order.id
            ).first()
            
            self.assertIsNotNone(log)
            self.assertEqual(log.telegram_id, '123456789')
            self.assertTrue(log.success)
    
    @patch('services.telegram._send_telegram_message')
    def test_notify_admin_graceful_failure(self, mock_send):
        """Test that notification failures don't raise exceptions."""
        from models import Order
        from services.telegram import notify_admin_new_order
        
        # Simulate exception during sending
        mock_send.side_effect = Exception("Unexpected error")
        
        order = Order(
            mechanic_name='Test Mechanic',
            telegram_id='123456789',
            category='Тормоза',
            vin='TEST1234',
            selected_parts=[{'name': 'Передние колодки'}],
            is_original=False
        )
        
        with patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'ADMIN_CHAT_IDS': '123456789',
            'ENABLE_TG_ADMIN_NOTIFS': 'true'
        }):
            # Should not raise exception
            try:
                result = notify_admin_new_order(order)
                # Should return False on error
                self.assertFalse(result)
            except Exception:
                self.fail("notify_admin_new_order raised an exception")


def test_telegram_notifications():
    """Run all tests and print results."""
    print("\n" + "="*60)
    print("Testing Telegram Admin Notifications")
    print("="*60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTelegramNotifications)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ ALL TELEGRAM NOTIFICATION TESTS PASSED!")
    else:
        print(f"❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = test_telegram_notifications()
    sys.exit(0 if success else 1)
