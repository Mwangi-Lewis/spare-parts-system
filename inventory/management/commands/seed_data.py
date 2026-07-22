from django.core.management.base import BaseCommand
from inventory.models import Category, Product, SerialNumber


class Command(BaseCommand):
    help = "Seeds the database with demo hardware parts and serial numbers."

    def handle(self, *args, **options):
        categories = ["CPU", "GPU", "RAM", "Motherboard", "Storage", "PSU"]
        cat = {}
        for name in categories:
            obj, _ = Category.objects.get_or_create(name=name)
            cat[name] = obj

        # (category, brand, name, price, stock, attributes)
        parts = [
            # --- CPUs ---
            ("CPU", "AMD", "Ryzen 5 7600", 25000, 8, {"socket": "AM5", "wattage": 65}),
            ("CPU", "AMD", "Ryzen 7 7800X3D", 48000, 6, {"socket": "AM5", "wattage": 120}),
            ("CPU", "Intel", "Core i5-13600K", 32000, 7, {"socket": "LGA1700", "wattage": 125}),
            ("CPU", "Intel", "Core i7-13700K", 45000, 5, {"socket": "LGA1700", "wattage": 125}),
            ("CPU", "AMD", "Ryzen 9 7950X", 72000, 2, {"socket": "AM5", "wattage": 170}),

            # --- Motherboards ---
            ("Motherboard", "ASUS", "ROG STRIX B650-A", 30000, 6,
             {"socket": "AM5", "ddr_gen": "DDR5", "form_factor": "ATX", "wattage": 60}),
            ("Motherboard", "MSI", "MAG B650 TOMAHAWK", 27000, 5,
             {"socket": "AM5", "ddr_gen": "DDR5", "form_factor": "ATX", "wattage": 60}),
            ("Motherboard", "Gigabyte", "Z790 AORUS ELITE", 35000, 5,
             {"socket": "LGA1700", "ddr_gen": "DDR5", "form_factor": "ATX", "wattage": 65}),
            ("Motherboard", "ASRock", "B760M PRO RS", 18000, 7,
             {"socket": "LGA1700", "ddr_gen": "DDR4", "form_factor": "mATX", "wattage": 50}),
            ("Motherboard", "MSI", "PRO B550-VC", 15000, 4,
             {"socket": "AM4", "ddr_gen": "DDR4", "form_factor": "ATX", "wattage": 50}),

            # --- RAM ---
            ("RAM", "Corsair", "Vengeance 16GB DDR5-5600", 9000, 12,
             {"ddr_gen": "DDR5", "wattage": 10}),
            ("RAM", "G.Skill", "Trident Z5 32GB DDR5-6000", 18000, 8,
             {"ddr_gen": "DDR5", "wattage": 12}),
            ("RAM", "Kingston", "Fury Beast 16GB DDR4-3200", 6500, 10,
             {"ddr_gen": "DDR4", "wattage": 8}),

            # --- GPUs ---
            ("GPU", "NVIDIA", "RTX 4060", 42000, 6, {"wattage": 115}),
            ("GPU", "NVIDIA", "RTX 4070 SUPER", 78000, 4, {"wattage": 220}),
            ("GPU", "AMD", "Radeon RX 7900 XT", 105000, 2, {"wattage": 315}),

            # --- PSUs ---
            ("PSU", "Corsair", "RM850x 850W", 18000, 7, {"wattage": 850}),
            ("PSU", "Cooler Master", "MWE 650W", 9500, 8, {"wattage": 650}),
            ("PSU", "Antec", "VP450 450W", 6000, 5, {"wattage": 450}),

            # --- Storage ---
            ("Storage", "Samsung", "970 EVO Plus 1TB NVMe", 12000, 10, {"wattage": 8}),
            ("Storage", "Seagate", "Barracuda 2TB HDD", 7000, 2, {"wattage": 10}),
        ]

        updated_products = 0
        created_serials = 0

        for category, brand, name, price, stock, attrs in parts:
            product, made = Product.objects.get_or_create(
                name=name,
                brand=brand,
                defaults={"category": cat[category], "price": price},
            )

            # keep existing records in step with the seed definitions
            product.category = cat[category]
            product.price = price
            product.low_stock_threshold = 3
            product.attributes = attrs
            product.stock_quantity = stock
            product.save()
            updated_products += 1

            # top up serial numbers so in-stock units match stock_quantity
            in_stock = product.serial_numbers.filter(
                status=SerialNumber.IN_STOCK
            ).count()
            total_serials = product.serial_numbers.count()
            needed = product.stock_quantity - in_stock

            prefix = "".join(w[0] for w in product.name.split()[:3]).upper()
            for i in range(needed):
                index = total_serials + i + 1
                code = f"{prefix}-{product.id:03d}-{index:04d}"
                SerialNumber.objects.get_or_create(
                    serial_code=code,
                    defaults={"product": product, "status": SerialNumber.IN_STOCK},
                )
                created_serials += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {updated_products} products synced, "
            f"{created_serials} new serial numbers."
        ))