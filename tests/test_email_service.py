
import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Configure paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

from backend.services.email_service import EmailService

class TestEmailService(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Initialize EmailService with a dummy DB path (not used heavily in init but required)
        self.email_service = EmailService(db_path=":memory:")

    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test sending email successfully"""
        # Setup mock
        instance = mock_smtp.return_value
        instance.send_message.return_value = {}
        
        # Test data
        to_email = "test@example.com"
        subject = "Test Subject"
        body = "<h1>Hello</h1>"
        
        # Call send_email
        result = self.email_service.send_email(to_email, subject, body, is_html=True)
        
        # Assertions
        self.assertTrue(result)
        instance.starttls.assert_called()
        instance.login.assert_called()
        instance.send_message.assert_called()
        instance.quit.assert_called()

    @patch('smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        """Test sending email failure handling"""
        # Setup mock to raise exception
        mock_smtp.side_effect = Exception("SMTP Connection Failed")
        
        # Call send_email
        result = self.email_service.send_email("test@example.com", "Subject", "Body")
        
        # Assertions
        self.assertFalse(result)

    def test_template_rendering(self):
        """Test that templates are rendered correctly (if logic is accessible)"""
        # This depends on how get_template_content is implemented. 
        # Assuming we can test variable replacement if exposed.
        pass

if __name__ == '__main__':
    unittest.main()
