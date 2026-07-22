from django.test import TestCase
from inventory.models import Category, Product
from inventory.compatibility import check_compatibility


class CompatibilityTests(TestCase):
    """Tests for the three compatibility rules."""

    def setUp(self):
        cpu_cat = Category.objects.create(name="CPU")
        mb_cat = Category.objects.create(name="Motherboard")
        ram_cat = Category.objects.create(name="RAM")
        gpu_cat = Category.objects.create(name="GPU")
        psu_cat = Category.objects.create(name="PSU")

        def make(cat, brand, name, attrs):
            return Product.objects.create(
                category=cat, brand=brand, name=name,
                price=1000, stock_quantity=5, attributes=attrs,
            )

        self.cpu_am5 = make(cpu_cat, "AMD", "Ryzen 5 7600",
                            {"socket": "AM5", "wattage": 65})
        self.cpu_big = make(cpu_cat, "AMD", "Ryzen 9 7950X",
                            {"socket": "AM5", "wattage": 170})
        self.mb_am5 = make(mb_cat, "ASUS", "B650-A",
                           {"socket": "AM5", "ddr_gen": "DDR5"})
        self.mb_intel = make(mb_cat, "Gigabyte", "Z790",
                             {"socket": "LGA1700", "ddr_gen": "DDR5"})
        self.ram_ddr5 = make(ram_cat, "Corsair", "Vengeance DDR5",
                             {"ddr_gen": "DDR5", "wattage": 10})
        self.ram_ddr4 = make(ram_cat, "Kingston", "Fury DDR4",
                             {"ddr_gen": "DDR4", "wattage": 8})
        self.gpu_big = make(gpu_cat, "AMD", "RX 7900 XT", {"wattage": 315})
        self.psu_850 = make(psu_cat, "Corsair", "RM850x", {"wattage": 850})
        self.psu_450 = make(psu_cat, "Antec", "VP450", {"wattage": 450})

    def test_compatible_build_passes(self):
        result = check_compatibility(
            [self.cpu_am5, self.mb_am5, self.ram_ddr5, self.psu_850]
        )
        self.assertTrue(result["compatible"])
        self.assertEqual(result["errors"], [])

    def test_socket_mismatch_is_caught(self):
        result = check_compatibility([self.cpu_am5, self.mb_intel, self.psu_850])
        self.assertFalse(result["compatible"])
        self.assertIn("Socket mismatch", result["errors"][0])

    def test_ram_generation_mismatch_is_caught(self):
        result = check_compatibility(
            [self.cpu_am5, self.mb_am5, self.ram_ddr4, self.psu_850]
        )
        self.assertFalse(result["compatible"])
        self.assertIn("RAM mismatch", result["errors"][0])

    def test_insufficient_power_is_caught(self):
        result = check_compatibility(
            [self.cpu_big, self.mb_am5, self.gpu_big, self.psu_450]
        )
        self.assertFalse(result["compatible"])
        self.assertIn("Insufficient power", result["errors"][0])

    def test_incomplete_selection_does_not_error(self):
        """Only a CPU selected — nothing to compare, so no complaints."""
        result = check_compatibility([self.cpu_am5])
        self.assertTrue(result["compatible"])
