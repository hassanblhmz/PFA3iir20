"""
Seed data for the GestAchats demo database.

Usage from the backend folder:
    python manage.py shell < seed_data.py
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from products.models import Category, Product
from suppliers.models import Supplier
from users.models import User


print("Seeding GestAchats demo data...")

suppliers_data = [
    {
        'code': 'F001',
        'name': 'Tech Maroc SARL',
        'contact_name': 'Amine Tazi',
        'email': 'contact@techmaroc.ma',
        'phone': '0522-123456',
        'city': 'Casablanca',
        'payment_terms': 30,
        'status': 'actif',
    },
    {
        'code': 'F002',
        'name': 'Bureau Plus SA',
        'contact_name': 'Nadia Benkirane',
        'email': 'nadia@bureauplus.ma',
        'phone': '0537-654321',
        'city': 'Rabat',
        'payment_terms': 45,
        'status': 'actif',
    },
    {
        'code': 'F003',
        'name': 'InfoSystems Maroc',
        'contact_name': 'Karim Idrissi',
        'email': 'k.idrissi@infosys.ma',
        'phone': '0524-789012',
        'city': 'Marrakech',
        'payment_terms': 60,
        'status': 'actif',
    },
    {
        'code': 'F004',
        'name': 'Fournitures Express',
        'contact_name': 'Sara Chaoui',
        'email': 'sara@fexpress.ma',
        'phone': '0535-345678',
        'city': 'Fes',
        'payment_terms': 30,
        'status': 'actif',
    },
]

for supplier_data in suppliers_data:
    supplier, _ = Supplier.objects.update_or_create(
        code=supplier_data['code'],
        defaults=supplier_data,
    )
    print(f"Supplier ready: {supplier.code}")

supplier_f001 = Supplier.objects.get(code='F001')

users_data = [
    {
        'email': 'admin@pfa.ma',
        'username': 'admin',
        'first_name': 'Admin',
        'last_name': 'Systeme',
        'role': 'admin',
        'department': 'Direction',
        'password': 'admin123',
    },
    {
        'email': 'demandeur@pfa.ma',
        'username': 'demandeur1',
        'first_name': 'Youssef',
        'last_name': 'Benali',
        'role': 'demandeur',
        'department': 'Informatique',
        'password': 'test123',
    },
    {
        'email': 'validateur@pfa.ma',
        'username': 'validateur1',
        'first_name': 'Fatima',
        'last_name': 'Zahra',
        'role': 'validateur',
        'department': 'Direction',
        'password': 'test123',
    },
    {
        'email': 'acheteur@pfa.ma',
        'username': 'acheteur1',
        'first_name': 'Mohamed',
        'last_name': 'Rachid',
        'role': 'acheteur',
        'department': 'Achats',
        'password': 'test123',
    },
    {
        'email': 'magasinier@pfa.ma',
        'username': 'magasinier1',
        'first_name': 'Khalid',
        'last_name': 'Amrani',
        'role': 'magasinier',
        'department': 'Logistique',
        'password': 'test123',
    },
    {
        'email': 'fournisseur@pfa.ma',
        'username': 'fournisseur1',
        'first_name': 'Amine',
        'last_name': 'Tazi',
        'role': 'fournisseur',
        'department': supplier_f001.name,
        'supplier': supplier_f001,
        'password': 'test123',
    },
]

for user_data in users_data:
    password = user_data.pop('password')
    user, _ = User.objects.update_or_create(
        email=user_data['email'],
        defaults=user_data,
    )
    user.set_password(password)
    user.is_staff = user.role == 'admin'
    user.is_superuser = user.role == 'admin'
    user.save()
    print(f"User ready: {user.email}")

categories_data = [
    ('Informatique', 'Materiel et accessoires informatiques'),
    ('Bureau', 'Fournitures de bureau'),
    ('Mobilier', 'Mobilier de bureau'),
    ('Consommables', 'Papeterie et consommables'),
    ('Reseau', 'Equipements reseau et cablage'),
]

categories = {}
for name, description in categories_data:
    category, _ = Category.objects.update_or_create(
        name=name,
        defaults={'description': description},
    )
    categories[name] = category
    print(f"Category ready: {name}")

products_data = [
    {
        'code': 'ART001',
        'name': 'Ordinateur portable Dell Latitude',
        'category': categories['Informatique'],
        'unit': 'lot',
        'unit_price': 8500,
        'current_stock': 5,
        'min_stock': 3,
        'max_stock': 15,
    },
    {
        'code': 'ART002',
        'name': 'Ecran 24 pouces Full HD',
        'category': categories['Informatique'],
        'unit': 'lot',
        'unit_price': 2200,
        'current_stock': 2,
        'min_stock': 5,
        'max_stock': 20,
    },
    {
        'code': 'ART003',
        'name': 'Clavier USB sans fil',
        'category': categories['Informatique'],
        'unit': 'lot',
        'unit_price': 350,
        'current_stock': 15,
        'min_stock': 5,
        'max_stock': 30,
    },
    {
        'code': 'ART004',
        'name': 'Souris optique USB',
        'category': categories['Informatique'],
        'unit': 'lot',
        'unit_price': 120,
        'current_stock': 0,
        'min_stock': 10,
        'max_stock': 40,
    },
    {
        'code': 'ART005',
        'name': 'Rame de papier A4',
        'category': categories['Consommables'],
        'unit': 'carton',
        'unit_price': 45,
        'current_stock': 80,
        'min_stock': 20,
        'max_stock': 200,
    },
    {
        'code': 'ART006',
        'name': "Cartouche d'encre HP",
        'category': categories['Consommables'],
        'unit': 'lot',
        'unit_price': 280,
        'current_stock': 4,
        'min_stock': 10,
        'max_stock': 40,
    },
    {
        'code': 'ART007',
        'name': 'Switch reseau 24 ports',
        'category': categories['Reseau'],
        'unit': 'lot',
        'unit_price': 3500,
        'current_stock': 3,
        'min_stock': 2,
        'max_stock': 10,
    },
    {
        'code': 'ART008',
        'name': 'Cable RJ45 CAT6 100m',
        'category': categories['Reseau'],
        'unit': 'lot',
        'unit_price': 650,
        'current_stock': 8,
        'min_stock': 5,
        'max_stock': 25,
    },
    {
        'code': 'ART009',
        'name': 'Chaise de bureau ergonomique',
        'category': categories['Bureau'],
        'unit': 'lot',
        'unit_price': 1800,
        'current_stock': 10,
        'min_stock': 5,
        'max_stock': 30,
    },
    {
        'code': 'ART010',
        'name': 'Stylos Bic boite de 50',
        'category': categories['Consommables'],
        'unit': 'lot',
        'unit_price': 35,
        'current_stock': 25,
        'min_stock': 10,
        'max_stock': 100,
    },
]

for product_data in products_data:
    product, _ = Product.objects.update_or_create(
        code=product_data['code'],
        defaults=product_data,
    )
    product.suppliers.set([supplier_f001])
    print(f"Product ready: {product.code}")

print("\nDemo accounts:")
print("  admin@pfa.ma / admin123")
print("  demandeur@pfa.ma / test123")
print("  validateur@pfa.ma / test123")
print("  acheteur@pfa.ma / test123")
print("  magasinier@pfa.ma / test123")
print("  fournisseur@pfa.ma / test123")
