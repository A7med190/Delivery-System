# Delivery System

A comprehensive REST API for managing food delivery operations including restaurants, orders, deliveries, payments, and reviews.

## Tech Stack

- **Backend**: Django 5.0 + Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL
- **API Docs**: drf-spectacular (OpenAPI 3.0 / Swagger)
- **Testing**: pytest + pytest-django
- **Deployment**: Docker + Docker Compose

## Project Structure

```
├── apps/
│   ├── users/           # User authentication, profiles
│   ├── restaurants/    # Restaurant management
│   ├── orders/         # Order management
│   ├── delivery/       # Delivery tracking
│   ├── payments/       # Payment processing
│   ├── reviews/        # Restaurant/order reviews
│   ├── addresses/      # User addresses
│   └── notifications   # Push notifications
├── core/               # Shared utilities
├── config/             # Django settings
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

## Local Setup (Without Docker)

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Create PostgreSQL database

```sql
CREATE DATABASE delivery_db;
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create superuser

```bash
python manage.py createsuperuser
```

### 7. Run development server

```bash
python manage.py runserver
```

## Docker Setup

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

## API Documentation

- **Swagger UI**: `http://localhost:8000/api/v1/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/v1/schema/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/schema/`

## Authentication

### 1. Register User
```bash
POST /api/v1/users/register/
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

### 2. Login (Get Token)
```bash
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "password123"
}
```

### 3. Refresh Token
```bash
POST /api/v1/auth/token/refresh/
{
  "refresh": "YOUR_REFRESH_TOKEN"
}
```

## API Endpoints

### Authentication
- `POST /api/v1/users/register/` - Register new user
- `POST /api/v1/auth/login/` - Login (get tokens)
- `POST /api/v1/auth/token/refresh/` - Refresh access token
- `GET /api/v1/users/profile/` - Get profile
- `PUT /api/v1/users/profile/` - Update profile

### Restaurants
- `GET /api/v1/restaurants/` - List restaurants (with filters)
- `POST /api/v1/restaurants/` - Create restaurant (owner)
- `GET /api/v1/restaurants/<id>/` - Get restaurant details
- `PUT /api/v1/restaurants/<id>/` - Update restaurant
- `DELETE /api/v1/restaurants/<id>/` - Delete restaurant
- `GET /api/v1/restaurants/<id>/menu/` - Get restaurant menu
- `GET /api/v1/restaurants/<id>/reviews/` - Get restaurant reviews

### Orders
- `GET /api/v1/orders/` - List user orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/<id>/` - Get order details
- `PUT /api/v1/orders/<id>/cancel/` - Cancel order (before delivery)
- `GET /api/v1/orders/<id>/track/` - Track order status

### Delivery
- `GET /api/v1/delivery/available/` - Get available deliveries
- `POST /api/v1/delivery/accept/<order_id>/` - Accept delivery
- `PUT /api/v1/delivery/status/<id>/` - Update delivery status
- `GET /api/v1/delivery/<id>/track/` - Track driver location

### Payments
- `POST /api/v1/payments/create/` - Create payment
- `POST /api/v1/payments/webhook/` - Payment webhook
- `GET /api/v1/payments/<id>/` - Get payment status
- `GET /api/v1/payments/history/` - Payment history

### Reviews
- `POST /api/v1/reviews/` - Create review
- `GET /api/v1/reviews/<id>/` - Get review
- `PUT /api/v1/reviews/<id>/` - Update review
- `DELETE /api/v1/reviews/<id>/` - Delete review

### Addresses
- `GET /api/v1/addresses/` - List saved addresses
- `POST /api/v1/addresses/` - Add new address
- `PUT /api/v1/addresses/<id>/` - Update address
- `DELETE /api/v1/addresses/<id>/` - Delete address

## User Roles

| Role | Permissions |
|---|---|
| `ADMIN` | Full access to everything |
| `OWNER` | Manage own restaurants |
| `DRIVER` | Accept and complete deliveries |
| `CUSTOMER` | Order food, track orders |

## Running Tests

```bash
pytest
pytest --cov=. --cov-report=html
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | - |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DB_NAME` | PostgreSQL database name | `delivery_db` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |

## Deployment

Production deployment with:
- Gunicorn (4 workers)
- PostgreSQL 15

## License

MIT