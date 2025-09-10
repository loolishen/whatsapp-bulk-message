# WhatsApp Bulk Message Django App

This Django application provides a web interface for creating and previewing WhatsApp messages with images, selecting recipients, and sending bulk messages.

## Features

- **Message Composer**: Create messages with text and images
- **Live Preview**: See how your message will appear to recipients
- **Recipient Management**: Add and manage contacts
- **Bulk Messaging**: Select multiple recipients and send messages

## Setup Instructions

1. **Install Python** (3.8 or higher)
<!-- make sure to use python 3.11.9 -->

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install cloudinary
   pip install pandas
   pip install requests
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Open your browser** and go to `http://127.0.0.1:8000`

## Usage

1. **Home Page** (`/`): Compose your message and upload an image. See live preview of how it will appear.

2. **Recipients Page** (`/recipients/`): Select recipients from your contact list and send the message.

3. **Admin Panel** (`/admin/`): Manage contacts, messages, and bulk messages (requires superuser account).

## File Structure

- `messaging/models.py`: Database models for Contact, Message, and BulkMessage
- `messaging/views.py`: View logic for handling requests
- `messaging/urls.py`: URL routing
- `templates/messaging/`: HTML templates
- `static/`: Static files (CSS, JS, images)

## Next Steps

To integrate with actual WhatsApp messaging, you would need to:

1. Set up WhatsApp Business API
2. Implement webhook handling
3. Add authentication and authorization
4. Add message status tracking
5. Implement rate limiting and queue management

## Models

- **Contact**: Store recipient information (name, phone number)
- **Message**: Store message content and images
- **BulkMessage**: Track bulk message campaigns and recipients
