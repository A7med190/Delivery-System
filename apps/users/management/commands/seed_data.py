from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import User
from apps.restaurants.models import Restaurant, MenuItem
from apps.addresses.models import Address
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Delivery System database...')

        # Create admin
        if not User.objects.filter(email='admin@delivery.com').exists():
            User.objects.create_superuser(
                email='admin@delivery.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )

        # Create customers
        for i in range(5):
            email = f'customer{i+1}@example.com'
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    password='password123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                Address.objects.create(
                    user=user,
                    street=fake.street_address(),
                    city=fake.city(),
                    state=fake.state(),
                    zip_code=fake.zipcode(),
                    country=fake.country(),
                    is_default=True
                )

        # Create restaurants
        restaurants_data = [
            ('Pizza Palace', 'Italian', '123 Main St'),
            ('Burger King', 'American', '456 Oak Ave'),
            ('Sushi House', 'Japanese', '789 Elm St'),
            ('Taco Town', 'Mexican', '321 Pine Rd'),
            ('Curry Corner', 'Indian', '654 Maple Dr'),
        ]

        for name, cuisine, address in restaurants_data:
            restaurant, created = Restaurant.objects.get_or_create(
                name=name,
                defaults={
                    'cuisine_type': cuisine,
                    'address': address,
                    'city': fake.city(),
                    'phone': fake.phone_number(),
                    'is_active': True,
                    'delivery_radius': random.randint(5, 20)
                }
            )
            if created:
                # Create menu items
                for item in ['Burger', 'Pizza', 'Pasta', 'Salad', 'Dessert']:
                    MenuItem.objects.create(
                        restaurant=restaurant,
                        name=f'{item}',
                        description=fake.text(max_nb_chars=50),
                        price=round(random.uniform(5, 25), 2),
                        is_available=True
                    )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Delivery database!'))