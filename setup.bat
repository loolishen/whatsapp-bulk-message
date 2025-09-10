@echo off
echo Setting up WhatsApp Bulk Message Django App...

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Creating some sample contacts...
echo from messaging.models import Contact > create_contacts.py
echo Contact.objects.get_or_create(name='Alice Johnson', phone_number='+1234567890') >> create_contacts.py
echo Contact.objects.get_or_create(name='Bob Smith', phone_number='+1987654321') >> create_contacts.py
echo Contact.objects.get_or_create(name='Charlie Brown', phone_number='+1122334455') >> create_contacts.py
echo Contact.objects.get_or_create(name='Diana Prince', phone_number='+1098765432') >> create_contacts.py
echo print('Sample contacts created!') >> create_contacts.py
python manage.py shell < create_contacts.py
del create_contacts.py

echo.
echo Setup complete! You can now run:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Then open http://127.0.0.1:8000 in your browser

pause
