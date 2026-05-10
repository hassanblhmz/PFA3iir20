"""
Script de génération des données de test (seed)
Usage: python manage.py shell < seed_data.py
  ou : python seed_data.py (depuis le dossier backend avec django configuré)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from suppliers.models import Supplier
from products.models import Category, Product
from purchases.models import PurchaseRequest, PurchaseRequestLine

print("🌱 Génération des données de test...")

# ---- UTILISATEURS ----
users_data = [
    {'email': 'admin@pfa.ma', 'username': 'admin', 'first_name': 'Admin', 'last_name': 'Système',
     'role': 'admin', 'department': 'Direction', 'password': 'admin123'},
    {'email': 'demandeur@pfa.ma', 'username': 'demandeur1', 'first_name': 'Youssef', 'last_name': 'Benali',
     'role': 'demandeur', 'department': 'Informatique', 'password': 'test123'},
    {'email': 'validateur@pfa.ma', 'username': 'validateur1', 'first_name': 'Fatima', 'last_name': 'Zahra',
     'role': 'validateur', 'department': 'Direction', 'password': 'test123'},
    {'email': 'acheteur@pfa.ma', 'username': 'acheteur1', 'first_name': 'Mohamed', 'last_name': 'Rachid',
     'role': 'acheteur', 'department': 'Achats', 'password': 'test123'},
    {'email': 'magasinier@pfa.ma', 'username': 'magasinier1', 'first_name': 'Khalid', 'last_name': 'Amrani',
     'role': 'magasinier', 'department': 'Logistique', 'password': 'test123'},
]

for u in users_data:
    if not User.objects.filter(email=u['email']).exists():
        password = u.pop('password')
        user = User(**u)
        user.set_password(password)
        user.is_staff = (u.get('role') == 'admin')
        user.is_superuser = (u.get('role') == 'admin')
        user.save()
        print(f"  ✅ Utilisateur: {u['email']}")

# ---- FOURNISSEURS ----
suppliers_data = [
    {'code': 'F001', 'name': 'Tech Maroc SARL', 'contact_name': 'Amine Tazi',
     'email': 'contact@techmaroc.ma', 'phone': '0522-123456', 'city': 'Casablanca',
     'payment_terms': 30, 'status': 'actif'},
    {'code': 'F002', 'name': 'Bureau Plus SA', 'contact_name': 'Nadia Benkirane',
     'email': 'nadia@bureauplus.ma', 'phone': '0537-654321', 'city': 'Rabat',
     'payment_terms': 45, 'status': 'actif'},
    {'code': 'F003', 'name': 'InfoSystems Maroc', 'contact_name': 'Karim Idrissi',
     'email': 'k.idrissi@infosys.ma', 'phone': '0524-789012', 'city': 'Marrakech',
     'payment_terms': 60, 'status': 'actif'},
    {'code': 'F004', 'name': 'Fournitures Express', 'contact_name': 'Sara Chaoui',
     'email': 'sara@fexpress.ma', 'phone': '0535-345678', 'city': 'Fès',
     'payment_terms': 30, 'status': 'actif'},
]

for s in suppliers_data:
    Supplier.objects.get_or_create(code=s['code'], defaults=s)
    print(f"  ✅ Fournisseur: {s['name']}")

# ---- CATÉGORIES ----
categories_data = [
    ('Informatique', 'Matériel et accessoires informatiques'),
    ('Bureau', 'Fournitures de bureau'),
    ('Mobilier', 'Mobilier de bureau'),
    ('Consommables', 'Papeterie et consommables'),
    ('Réseau', 'Équipements réseaux et câblage'),
]

for name, desc in categories_data:
    cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
    print(f"  ✅ Catégorie: {name}")

# ---- ARTICLES ----
it_cat = Category.objects.get(name='Informatique')
bureau_cat = Category.objects.get(name='Bureau')
conso_cat = Category.objects.get(name='Consommables')
reseau_cat = Category.objects.get(name='Réseau')

products_data = [
    {'code': 'ART001', 'name': 'Ordinateur portable Dell Latitude', 'category': it_cat,
     'unit': 'pièce', 'unit_price': 8500, 'current_stock': 5, 'min_stock': 3},
    {'code': 'ART002', 'name': 'Écran 24" Full HD', 'category': it_cat,
     'unit': 'pièce', 'unit_price': 2200, 'current_stock': 2, 'min_stock': 5},  # Critique
    {'code': 'ART003', 'name': 'Clavier USB sans fil', 'category': it_cat,
     'unit': 'pièce', 'unit_price': 350, 'current_stock': 15, 'min_stock': 5},
    {'code': 'ART004', 'name': 'Souris optique USB', 'category': it_cat,
     'unit': 'pièce', 'unit_price': 120, 'current_stock': 0, 'min_stock': 10},  # Rupture
    {'code': 'ART005', 'name': 'Rame de papier A4 (500 feuilles)', 'category': conso_cat,
     'unit': 'carton', 'unit_price': 45, 'current_stock': 80, 'min_stock': 20},
    {'code': 'ART006', 'name': 'Cartouche d\'encre HP', 'category': conso_cat,
     'unit': 'pièce', 'unit_price': 280, 'current_stock': 4, 'min_stock': 10},  # Critique
    {'code': 'ART007', 'name': 'Switch réseau 24 ports', 'category': reseau_cat,
     'unit': 'pièce', 'unit_price': 3500, 'current_stock': 3, 'min_stock': 2},
    {'code': 'ART008', 'name': 'Câble RJ45 CAT6 (100m)', 'category': reseau_cat,
     'unit': 'lot', 'unit_price': 650, 'current_stock': 8, 'min_stock': 5},
    {'code': 'ART009', 'name': 'Chaise de bureau ergonomique', 'category': bureau_cat,
     'unit': 'pièce', 'unit_price': 1800, 'current_stock': 10, 'min_stock': 5},
    {'code': 'ART010', 'name': 'Stylos Bic (boîte de 50)', 'category': conso_cat,
     'unit': 'lot', 'unit_price': 35, 'current_stock': 25, 'min_stock': 10},
]

sup1 = Supplier.objects.get(code='F001')
sup2 = Supplier.objects.get(code='F002')
for p in products_data:
    product, _ = Product.objects.get_or_create(code=p['code'], defaults=p)
    product.suppliers.add(sup1)
    print(f"  ✅ Article: {p['name']}")

print("\n✨ Données de test générées avec succès!")
print("\n📋 Comptes de test:")
print("  admin@pfa.ma / admin123  (Admin)")
print("  demandeur@pfa.ma / test123  (Demandeur)")
print("  validateur@pfa.ma / test123  (Validateur)")
print("  acheteur@pfa.ma / test123  (Acheteur)")
print("  magasinier@pfa.ma / test123  (Magasinier)")
