import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.categories.models import Category
from apps.suppliers.models import Supplier
from apps.products.models import Product
from apps.inventory.models import StockLog


class Command(BaseCommand):
    help = 'Generate dummy data for the fashion inventory system'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔄 Generating dummy data...\n')

        # ===== CATEGORIES =====
        category_data = [
            ('Clothes', 'Shirts, pants, dresses, jackets and all clothing items'),
            ('Beauty', 'Makeup, skincare, haircare and beauty products'),
            ('Accessories', 'Bags, belts, scarves, watches and jewelry'),
            ('Footwear', 'Shoes, sandals, boots and sneakers'),
            ('Sportswear', 'Athletic and sports related clothing and gear'),
        ]
        categories = []
        for name, desc in category_data:
            cat, created = Category.objects.get_or_create(
                category_name=name,
                defaults={'description': desc}
            )
            categories.append(cat)
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  📁 Category: {name} [{status}]')

        # ===== SUPPLIERS =====
        supplier_data = [
            ('FashionHub India', 'contact@fashionhub.in', '+91 97845 12365', 'Mumbai, Maharashtra'),
            ('StyleCraft Exports', 'info@stylecraft.com', '+91 88456 23456', 'Delhi, NCR'),
            ('TrendLine Textiles', 'hello@trendline.in', '+91 75123 34567', 'Surat, Gujarat'),
            ('GlamWear Inc', 'sales@glamwear.com', '+91 93256 45678', 'Bangalore, Karnataka'),
            ('Elite Fashion Corp', 'orders@elitefashion.in', '+91 80123 56789', 'Chennai, Tamil Nadu'),
            ('Royal Garments', 'royal@garments.com', '+91 70234 67890', 'Jaipur, Rajasthan'),
            ('Urban Style Hub', 'urban@stylehub.in', '+91 91345 78901', 'Pune, Maharashtra'),
            ('Desi Threads', 'support@desithreads.com', '+91 85456 89012', 'Kolkata, West Bengal'),
            ('Prime Apparel', 'prime@apparel.in', '+91 78567 90123', 'Hyderabad, Telangana'),
            ('Nova Fashion House', 'nova@fashionhouse.com', '+91 62678 01234', 'Ahmedabad, Gujarat'),
        ]
        suppliers = []
        for name, email, phone, address in supplier_data:
            sup, created = Supplier.objects.get_or_create(
                supplier_name=name,
                defaults={'email': email, 'phone': phone, 'address': address}
            )
            suppliers.append(sup)
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  🚚 Supplier: {name} [{status}]')

        # ===== PRODUCTS =====
        brands = ['Nike', 'Adidas', 'Zara', 'H&M', 'Puma', 'Levi\'s', 'Gucci',
                   'Ray-Ban', 'Lakme', 'Maybelline', 'Woodland', 'Bata', 'FabIndia']
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'Free Size', '6', '7', '8', '9', '10']
        colors = ['Black', 'White', 'Red', 'Blue', 'Green', 'Navy', 'Grey',
                  'Beige', 'Pink', 'Brown', 'Maroon', 'Olive', 'Teal', 'Coral']

        product_templates = {
            'Clothes': [
                'Classic Cotton Shirt', 'Slim Fit Jeans', 'Casual Hoodie',
                'Formal Blazer', 'Summer Dress', 'Polo T-Shirt', 'Denim Jacket',
                'Linen Trousers', 'Printed Kurti', 'Silk Saree',
                'V-Neck Sweater', 'Cargo Pants', 'Maxi Skirt',
                'Checkered Flannel Shirt', 'Chino Shorts',
            ],
            'Beauty': [
                'Matte Lipstick', 'Foundation Cream', 'Eye Shadow Palette',
                'Moisturizing Lotion', 'Hair Serum', 'Perfume Spray',
                'Face Wash Gel', 'Night Cream', 'BB Cream SPF',
                'Compact Powder',
            ],
            'Accessories': [
                'Leather Belt', 'Aviator Sunglasses', 'Canvas Tote Bag',
                'Silk Scarf', 'Digital Watch', 'Pearl Necklace',
                'Beaded Bracelet', 'Leather Wallet', 'Crossbody Bag',
                'Statement Earrings',
            ],
            'Footwear': [
                'Running Sneakers', 'Leather Boots', 'Casual Loafers',
                'High Heel Sandals', 'Sports Shoes', 'Canvas Slip-Ons',
                'Ankle Boots', 'Flip Flops', 'Oxford Shoes',
                'Platform Wedges',
            ],
            'Sportswear': [
                'Track Pants', 'Sports Bra', 'Yoga Leggings',
                'Gym Tank Top', 'Windbreaker Jacket',
            ],
        }

        product_count = 0
        for cat in categories:
            templates = product_templates.get(cat.category_name, [])
            for name in templates:
                sku = f'SKU-{cat.category_name[:3].upper()}-{random.randint(1000, 9999)}'
                # Ensure unique SKU
                while Product.objects.filter(sku=sku).exists():
                    sku = f'SKU-{cat.category_name[:3].upper()}-{random.randint(1000, 9999)}'

                stock = random.choice([0, 0, 2, 5, 7, 8, 12, 15, 25, 30, 45, 50, 75, 100])
                price = round(random.uniform(199, 9999), 2)

                product = Product.objects.create(
                    name=name,
                    sku=sku,
                    category=cat,
                    brand=random.choice(brands),
                    size=random.choice(sizes),
                    color=random.choice(colors),
                    price=price,
                    stock_quantity=stock,
                    supplier=random.choice(suppliers),
                    description=f'Premium quality {name.lower()} from our curated fashion collection. Perfect for any occasion.',
                )
                product_count += 1
                self.stdout.write(f'  👕 Product: {name} (Stock: {stock}, ₹{price})')

        self.stdout.write(f'\n✅ Created {product_count} products\n')

        # ===== STOCK LOGS =====
        self.stdout.write('📊 Generating stock history logs...\n')
        products = list(Product.objects.all())
        log_count = 0
        now = timezone.now()

        for _ in range(80):
            product = random.choice(products)
            change_type = random.choice(['IN', 'IN', 'IN', 'OUT', 'OUT'])
            quantity = random.randint(1, 30)
            days_ago = random.randint(0, 150)
            created = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            notes_options = [
                'Regular restock', 'Monthly supply', 'Customer return',
                'Order fulfillment', 'New shipment', 'Seasonal update',
                'Inventory adjustment', 'Quality check return',
                'Bulk order', 'Flash sale prep', '',
            ]

            log = StockLog(
                product=product,
                change_type=change_type,
                quantity=quantity,
                notes=random.choice(notes_options),
            )
            log.save()
            # Override created_at
            StockLog.objects.filter(pk=log.pk).update(created_at=created)
            log_count += 1

        self.stdout.write(f'✅ Created {log_count} stock log entries\n')
        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Dummy data generation complete!\n'
            f'   • {len(categories)} categories\n'
            f'   • {len(suppliers)} suppliers\n'
            f'   • {product_count} products\n'
            f'   • {log_count} stock logs\n'
        ))
