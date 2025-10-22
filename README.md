TradeFair Project
TradeFair is a Django REST Framework-based marketplace API enabling customers to follow vendors, browse products, place preorders, and process payments via Paystack. The project includes apps for users, vendors, products, orders, followers, and payments, with comprehensive API documentation via Swagger UI.
Features

User Management: Register and manage customer or vendor profiles.
Vendor Management: Create and manage sheds for product listings.
Product Management: List, browse, and filter products by vendor or category.
Preorders: Customers can create preorders, vendors can confirm or cancel them.
Follows: Customers can follow/unfollow vendors to track updates.
Payments: Initiate and verify payments for preorders via Paystack.
API Documentation: Interactive Swagger UI and ReDoc for exploring endpoints.

Prerequisites

Python 3.12
PostgreSQL (recommended) or another Django-supported database
Paystack account for payment integration
Git

Setup Instructions
1. Clone the Repository
Clone the project and navigate to the directory:
git clone <repository-url>
cd tradefair_project

2. Create and Activate a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies
Create a requirements.txt file with the following:
django>=4.2
djangorestframework>=3.14
drf-yasg>=1.21
paystackapi>=2.1
pillow>=9.0
psycopg2-binary>=2.9
python-dotenv>=1.0
setuptools<81

Install dependencies:
pip install -r requirements.txt

4. Configure Environment Variables
Create a .env file in the project root:
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/tradefair
PAYSTACK_SECRET_KEY=your-paystack-secret-key
MEDIA_URL=/media/
MEDIA_ROOT=/path/to/tradefair_project/media


Generate a Django secret key using a tool like django-secret-keygen.
Obtain a Paystack secret key from paystack.com.
Set MEDIA_ROOT to a directory for storing uploaded files (e.g., product images).

5. Configure Django Settings
Update tradefair_project/settings.py to load environment variables:
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradefair',
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', BASE_DIR / 'media')

PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

6. Set Up the Database
Create a PostgreSQL database named tradefair:
createdb tradefair

Run migrations:
python manage.py makemigrations
python manage.py migrate

7. Create a Superuser
Create an admin user for the Django admin interface:
python manage.py createsuperuser

8. Run the Development Server
Start the server:
python manage.py runserver

Access the API at http://localhost:8000, admin at http://localhost:8000/admin/, and Swagger UI at http://localhost:8000/swagger/.
9. Run Tests
Verify the application with the test suite:
python manage.py test users vendors products orders followers payments

API Documentation
Explore the API using Swagger UI at http://localhost:8000/swagger/ or ReDoc at http://localhost:8000/redoc/. Key endpoints include:

Authentication: POST /api/token/ (obtain token), POST /api/register/ (create user)
Users: GET/POST /api/users/vendors/ (manage vendor profiles)
Vendors: GET/POST /api/vendors/sheds/ (manage sheds)
Products: GET/POST /api/products/ (list/create products, filter by vendor or category)
Preorders: GET/POST /api/preorders/ (list/create preorders), PATCH /api/preorders/{id}/confirm/ (vendor confirm), POST /api/preorders/{id}/initiate_payment/ (initiate payment)
Followers: GET/POST /api/followers/ (list/create follows), DELETE /api/followers/{vendor_id}/unfollow/ (unfollow vendor)
Payments: GET/POST /api/payments/ (manage payment transactions)

Notes

Ensure valid Paystack API keys for payment functionality.
Media files (e.g., product images) are served at /media/ in DEBUG mode.
Pin setuptools<81 to suppress drf-yasg warnings.
For production, configure a WSGI server (e.g., Gunicorn) and a web server (e.g., Nginx).

Contact
For support, email support@tradefair.com or open an issue on the repository.

To register a user/vendor:
POST https://alx-se-be-capstone-project-tradefair-api.onrender.com/api/register/

{
  "username": "demo2_customer",
  "domain": "FB",
  "password": "securepass123",
  "email": "vendor.com",
  "is_vendor": true
}
