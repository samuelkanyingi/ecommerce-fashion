# FashionHub - E-Commerce FashionHub Platform

A e-commerce platform built with Django, featuring M-Pesa payment integration, real-time cart updates with HTMX, and a responsive user interface.

## Features

### 🛍️ Shopping Experience
- Browse men's and women's fashion collections
- Filter products by category and subcategory
- Sort products by price (low to high, high to low)
- Real-time shopping cart updates without page refresh
- Dynamic cart item counter

### 💳 Payment Integration
- M-Pesa Daraja API integration (STK Push)
- Secure payment processing
- Real-time payment status updates

### 👤 User Management
- User registration and authentication
- Login/logout functionality
- Password reset with email verification

### 📦 Order Management
- Multi-step checkout process with progress indicator
- Shipping information collection (Address, City, Location)
- Email confirmation on order placement
- Automatic order creation and updates

### 📧 Email Notifications
- Order confirmation emails
- Payment initiation notifications
- Delivery information included in emails
- Newsletter subscription system

### 🎨 User Interface
- Responsive design
- Dynamic navigation with sidebar menu
- Animated progress bars for checkout
- HTMX-powered dynamic content updates
- Alpine.js for interactive components

## Tech Stack

### Backend
- **Django 5.2.9** - Python web framework
- **PostgreSQL** - Database
- **Requests** - HTTP library for M-Pesa API calls

### Frontend
- **HTMX 1.9.10** - Dynamic HTML updates
- **Alpine.js 3.x** - Lightweight JavaScript framework
- **Font Awesome 4.7** - Icons
- **Custom CSS** - Styling

### Payment Gateway
- **M-Pesa Daraja API** - Mobile money payment integration

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### Setup Instructions

1. **Clone the repository**
```bash
cd c:\Users\user\Desktop\school\sci400\FashionHub\fashion_project
```



2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure PostgreSQL Database**
Create a PostgreSQL database named `fashionhub`:
```sql
CREATE DATABASE fashionhub;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fashionhub TO postgres;
```

5. **Update Database Settings**
Edit `fashion_project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fashionhub',
        'USER': 'postgres',
        'PASSWORD': 'your_password',  
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

6. **Configure Email Settings**
Update the email configuration in `settings.py`:
```python
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'  
```

7. **Configure M-Pesa Credentials**
Update M-Pesa settings in `settings.py`:
```python
MPESA_CONSUMER_KEY = 'your_consumer_key'
MPESA_CONSUMER_SECRET = 'your_consumer_secret'
MPESA_SHORTCODE = 'your_shortcode'
MPESA_PASSKEY = 'your_passkey'
MPESA_CALLBACK_URL = 'your_ngrok_url/mpesa/callback/'
```

8. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

9. **Create Superuser**
```bash
python manage.py createsuperuser
```

10. **Collect Static Files**
```bash
python manage.py collectstatic
```

11. **Run Development Server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Project Structure

```
fashion_project/
├── fashion_project/         
│   ├── settings.py          
│   ├── urls.py             
│   └── wsgi.py             
├── shop/                 
│   ├── migrations/       
│   ├── utils/           
│   │   └── mpesa.py        
│   ├── models.py          
│   ├── views.py            
│   ├── urls.py          
│   └── admin.py          
├── templates/shop/      
│   ├── index.html        
│   ├── women.html        
│   ├── men.html          
│   ├── cart.html         
│   ├── login.html        
│   └── register.html     
├── static/               
│   ├── css/             
│   ├── js/              
│   └── images/           
├── media/                
│   └── products/          
├── manage.py              
├── requirements.txt      
└── README.md          
```

## Usage

### Admin Panel
Access the admin panel at `http://127.0.0.1:8000/admin/`
- Add/edit products
- Manage categories

### Adding Products
1. Login to admin panel
2. Navigate to Products
3. Click "Add Product"
4. Fill in product details (name, price, category, subcategory, image)
5. Save

### Testing M-Pesa Integration
1. Use ngrok to expose your local server:
```bash
ngrok http 8000
```
2. Update `MPESA_CALLBACK_URL` in settings.py with your ngrok URL





```python

## API Endpoints

### M-Pesa Integration
- `POST /mpesa/stk-push/<order_id>/` - Initiate STK push
- `POST /mpesa/callback/` - M-Pesa payment callback

### Shopping Cart
- `POST /add-to-cart/` - Add item to cart
- `POST /update-cart/` - Update cart quantities
- `POST /remove-item/` - Remove item from cart
- `GET /cart/` - View cart

### User Authentication
- `POST /login/` - User login
- `POST /register/` - User registration
- `POST /logout/` - User logout

```
## Contact

For questions or support, please contact: samuelkanyingi2016@gmail.com

## Acknowledgments

- Django Documentation
- Safaricom Daraja API
- HTMX Documentation
- Alpine.js Documentation
