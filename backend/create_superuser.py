"""
Helper script to create a Django superuser non-interactively.
Usage: python create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemical_equipment.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin'
    
    if User.objects.filter(username=username).exists():
        print(f'User "{username}" already exists.')
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f'Superuser "{username}" created successfully!')
        print(f'Username: {username}')
        print(f'Password: {password}')

if __name__ == '__main__':
    create_superuser()
