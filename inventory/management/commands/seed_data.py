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
            ("CPU", "AMD", "Ryzen 5 7600", 25000, 5, {"socket": "AM5", "wattage": 65}),
            ("CPU", "AMD", "Ryzen 7 7800X3D", 48000, 3, {"socket": "AM5", "wattage": 120}),
            ("CPU", "Intel", "Core i5-13600K", 32000, 4, {"socket": "LGA1700", "wattage": 125}),
            ("CPU", "Intel", "Core i7-13700K", 45000, 2, {"socket": "LGA1700", "wattage": 125}),
            ("CPU", "AMD", "Ryzen 9 7950X", 72000, 2, {"socket": "AM5", "wattage": 170}),

            # --- Motherboards ---
            ("Motherboard", "ASUS", "ROG STRIX B650-A", 30000, 4,
             {"socket": "AM5", "ddr_gen": "DDR5", "form_factor": "ATX"}),
            ("Motherboard", "MSI", "MAG B650 TOMAHAWK", 27000, 3,
             {"socket": "AM5", "ddr_gen": "DDR5", "form_factor": "ATX"}),
            ("Motherboard", "Gigabyte", "Z790 AORUS ELITE", 35000, 3,
             {"socket": "LGA1700", "ddr_gen": "DDR5", "form_factor": "ATX"}),
            ("Motherboard", "ASRock", "B760M PRO RS", 18000, 5,
             {"socket": "LGA1700", "ddr_gen": "DDR4", "form_factor": "mATX"}),
            ("Motherboard", "MSI", "PRO B550-VC", 15000, 2,
             {"socket": "AM4", "ddr_gen": "DDR4", "form_factor": "ATX"}),

            # --- RAM ---
            ("RAM", "Corsair", "Vengeance 16GB DDR5-5600", 9000, 8,
             {"ddr_gen": "DDR5", "wattage": 10}),
            ("RAM", "G.Skill", "Trident Z5 32GB DDR5-6000", 18000, 4,
             {"ddr_gen": "DDR5", "wattage": 12}),
            ("RAM", "Kingston", "Fury Beast 16GB DDR4-3200", 6500, 6,
             {"ddr_gen": "DDR4", "wattage": 8}),

            # --- GPUs ---
            ("GPU", "NVIDIA", "RTX 4060", 42000, 3, {"wattage": 115}),
            ("GPU", "NVIDIA", "RTX 4070 SUPER", 78000, 2, {"wattage": 220}),
            ("GPU", "AMD", "Radeon RX 7900 XT", 105000, 2, {"wattage": 315}),

            # --- PSUs ---
            ("PSU", "Corsair", "RM850x 850W", 18000, 4, {"wattage": 850}),
            ("PSU", "Cooler Master", "MWE 650W", 9500, 5, {"wattage": 650}),
            ("PSU", "Antec", "VP450 450W", 6000, 3, {"wattage": 450}),

            # --- Storage ---
            ("Storage", "Samsung", "970 EVO Plus 1TB NVMe", 12000, 6, {"wattage": 8}),
            ("Storage", "Seagate", "Barracuda 2TB HDD", 7000, 2, {"wattage": 10}),
        ]

        created_products = 0
        created_serials = 0

        for category, brand, name, price, stock, attrs in parts:
            product, made = Product.objects.get_or_create(
                name=name,
                brand=brand,
                defaults={
                    "category": cat[category],
                    "price": price,
                    "stock_quantity": stock,
                    "low_stock_threshold": 3,
                    "attributes": attrs,
                },
            )
            if made:
                created_products += 1

            # give every unit in stock its own serial number
            existing = product.serial_numbers.count()
            for i in range(existing, product.stock_quantity):
                prefix = "".join(w[0] for w in product.name.split()[:3]).upper()
                code = f"{prefix}-{product.id:03d}-{i + 1:04d}"
                SerialNumber.objects.get_or_create(
                    serial_code=code,
                    defaults={"product": product, "status": SerialNumber.IN_STOCK},
                )
                created_serials += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {created_products} new products, "
            f"{created_serials} new serial numbers."
        ))
