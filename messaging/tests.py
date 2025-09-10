from django.test import TestCase
from .models import Contact, Message, BulkMessage

class ContactModelTest(TestCase):
    def test_contact_creation(self):
        contact = Contact.objects.create(
            name="Test User",
            phone_number="+1234567890"
        )
        self.assertEqual(contact.name, "Test User")
        self.assertEqual(contact.phone_number, "+1234567890")

class MessageModelTest(TestCase):
    def test_message_creation(self):
        message = Message.objects.create(
            text_content="Test message"
        )
        self.assertEqual(message.text_content, "Test message")
