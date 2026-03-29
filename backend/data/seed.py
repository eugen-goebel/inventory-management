"""
Seed script for the Inventory Management database.
Run from the backend directory: python -m data.seed
"""

import random
from datetime import datetime, timezone, timedelta

from db.database import SessionLocal, init_db
from models.orm import Supplier, Product, StockMovement

# ---------------------------------------------------------------------------
# Seed data definitions
# ---------------------------------------------------------------------------

SUPPLIERS = [
    {"name": "TechDistribution GmbH", "contact_email": "einkauf@techdist.de", "phone": "+49 89 1234567", "country": "Deutschland"},
    {"name": "Buerowelt AG", "contact_email": "vertrieb@buerowelt.de", "phone": "+49 30 9876543", "country": "Deutschland"},
    {"name": "MoebelProfi KG", "contact_email": "info@moebelprofi.de", "phone": "+49 40 5551234", "country": "Deutschland"},
    {"name": "SoftwareLand GmbH", "contact_email": "lizenzen@softwareland.de", "phone": "+49 211 3334455", "country": "Deutschland"},
    {"name": "NetzwerkPartner OHG", "contact_email": "sales@netzwerkpartner.de", "phone": "+49 69 7778899", "country": "Deutschland"},
    {"name": "PeripherieShop GmbH", "contact_email": "bestellung@peripherieshop.de", "phone": "+49 711 2223344", "country": "Deutschland"},
    {"name": "ElektroGrosshandel AG", "contact_email": "kontakt@elektrogross.de", "phone": "+49 221 6667788", "country": "Deutschland"},
    {"name": "IT-Bedarf Schmidt e.K.", "contact_email": "info@itbedarf-schmidt.de", "phone": "+49 511 4445566", "country": "Deutschland"},
]

PRODUCTS = [
    # Elektronik
    {"name": "Laptop ThinkPad T14s", "sku": "EL-001", "category": "Elektronik", "supplier_idx": 0, "unit_price": 1299.99, "reorder_level": 5},
    {"name": "Desktop-PC OptiPlex 7010", "sku": "EL-002", "category": "Elektronik", "supplier_idx": 0, "unit_price": 899.00, "reorder_level": 3},
    {"name": "Monitor 27 Zoll 4K", "sku": "EL-003", "category": "Elektronik", "supplier_idx": 6, "unit_price": 449.99, "reorder_level": 8},
    {"name": "Smartphone Galaxy S24", "sku": "EL-004", "category": "Elektronik", "supplier_idx": 6, "unit_price": 799.00, "reorder_level": 5},
    {"name": "Tablet iPad Air", "sku": "EL-005", "category": "Elektronik", "supplier_idx": 0, "unit_price": 699.00, "reorder_level": 4},

    # Bueromaterial
    {"name": "Druckerpapier A4 500 Blatt", "sku": "BM-001", "category": "Bueromaterial", "supplier_idx": 1, "unit_price": 4.99, "reorder_level": 100},
    {"name": "Kugelschreiber 50er Pack", "sku": "BM-002", "category": "Bueromaterial", "supplier_idx": 1, "unit_price": 12.50, "reorder_level": 30},
    {"name": "Ordner A4 breit", "sku": "BM-003", "category": "Bueromaterial", "supplier_idx": 1, "unit_price": 2.99, "reorder_level": 50},
    {"name": "Haftnotizen 12er Pack", "sku": "BM-004", "category": "Bueromaterial", "supplier_idx": 1, "unit_price": 8.49, "reorder_level": 40},
    {"name": "Tintenpatronen Multipack", "sku": "BM-005", "category": "Bueromaterial", "supplier_idx": 7, "unit_price": 34.99, "reorder_level": 20},

    # Moebel
    {"name": "Schreibtisch hoehenverstellbar", "sku": "MO-001", "category": "Moebel", "supplier_idx": 2, "unit_price": 599.00, "reorder_level": 3},
    {"name": "Buerostuhl ergonomisch", "sku": "MO-002", "category": "Moebel", "supplier_idx": 2, "unit_price": 449.00, "reorder_level": 5},
    {"name": "Aktenschrank 4 Schubladen", "sku": "MO-003", "category": "Moebel", "supplier_idx": 2, "unit_price": 289.00, "reorder_level": 2},
    {"name": "Besprechungstisch 240cm", "sku": "MO-004", "category": "Moebel", "supplier_idx": 2, "unit_price": 799.00, "reorder_level": 1},
    {"name": "Rollcontainer 3 Schubladen", "sku": "MO-005", "category": "Moebel", "supplier_idx": 2, "unit_price": 179.00, "reorder_level": 5},

    # Software-Lizenzen
    {"name": "Microsoft 365 Business", "sku": "SW-001", "category": "Software-Lizenzen", "supplier_idx": 3, "unit_price": 12.90, "reorder_level": 50},
    {"name": "Adobe Creative Cloud", "sku": "SW-002", "category": "Software-Lizenzen", "supplier_idx": 3, "unit_price": 59.99, "reorder_level": 10},
    {"name": "Antivirus Enterprise", "sku": "SW-003", "category": "Software-Lizenzen", "supplier_idx": 3, "unit_price": 29.99, "reorder_level": 30},
    {"name": "Projektmanagement-Tool Lizenz", "sku": "SW-004", "category": "Software-Lizenzen", "supplier_idx": 3, "unit_price": 8.50, "reorder_level": 20},
    {"name": "VPN-Lizenz Pro", "sku": "SW-005", "category": "Software-Lizenzen", "supplier_idx": 3, "unit_price": 6.99, "reorder_level": 25},

    # Netzwerk
    {"name": "Switch 24-Port Managed", "sku": "NW-001", "category": "Netzwerk", "supplier_idx": 4, "unit_price": 349.00, "reorder_level": 3},
    {"name": "WLAN Access Point", "sku": "NW-002", "category": "Netzwerk", "supplier_idx": 4, "unit_price": 189.00, "reorder_level": 5},
    {"name": "Patchkabel Cat6 3m 10er", "sku": "NW-003", "category": "Netzwerk", "supplier_idx": 4, "unit_price": 24.99, "reorder_level": 20},
    {"name": "Firewall Appliance", "sku": "NW-004", "category": "Netzwerk", "supplier_idx": 4, "unit_price": 1299.00, "reorder_level": 2},
    {"name": "Server-Rack 42HE", "sku": "NW-005", "category": "Netzwerk", "supplier_idx": 4, "unit_price": 899.00, "reorder_level": 1},

    # Peripherie
    {"name": "Tastatur mechanisch", "sku": "PE-001", "category": "Peripherie", "supplier_idx": 5, "unit_price": 79.99, "reorder_level": 15},
    {"name": "Maus ergonomisch kabellos", "sku": "PE-002", "category": "Peripherie", "supplier_idx": 5, "unit_price": 49.99, "reorder_level": 20},
    {"name": "Headset USB-C", "sku": "PE-003", "category": "Peripherie", "supplier_idx": 5, "unit_price": 89.00, "reorder_level": 10},
    {"name": "Webcam Full HD", "sku": "PE-004", "category": "Peripherie", "supplier_idx": 5, "unit_price": 69.99, "reorder_level": 10},
    {"name": "Docking Station USB-C", "sku": "PE-005", "category": "Peripherie", "supplier_idx": 7, "unit_price": 199.00, "reorder_level": 8},
]

REFERENCES_IN = [
    "Bestellung", "Nachlieferung", "Retoure-Eingang", "Inventurkorrektur",
]
REFERENCES_OUT = [
    "Ausgabe Mitarbeiter", "Abteilungsbedarf", "Defekt/Entsorgung", "Standortwechsel",
]


def seed():
    """Populate the database with sample data."""
    init_db()
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(StockMovement).delete()
        db.query(Product).delete()
        db.query(Supplier).delete()
        db.commit()

        # --- Suppliers ---
        supplier_objects = []
        for s in SUPPLIERS:
            supplier = Supplier(**s)
            db.add(supplier)
            supplier_objects.append(supplier)
        db.commit()
        for s in supplier_objects:
            db.refresh(s)

        # --- Products ---
        product_objects = []
        for p in PRODUCTS:
            supplier = supplier_objects[p["supplier_idx"]]
            product = Product(
                name=p["name"],
                sku=p["sku"],
                category=p["category"],
                supplier_id=supplier.id,
                unit_price=p["unit_price"],
                reorder_level=p["reorder_level"],
                current_stock=0,
            )
            db.add(product)
            product_objects.append(product)
        db.commit()
        for p in product_objects:
            db.refresh(p)

        # --- Stock Movements ---
        random.seed(42)
        now = datetime.now(timezone.utc)

        for i in range(50):
            product = random.choice(product_objects)
            days_ago = random.randint(0, 30)
            timestamp = now - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            # First 30 movements are always "in" to build up stock
            if i < 30:
                movement_type = "in"
            else:
                movement_type = random.choice(["in", "out"])

            if movement_type == "in":
                quantity = random.randint(5, 50)
                reference = random.choice(REFERENCES_IN)
            else:
                if product.current_stock <= 0:
                    movement_type = "in"
                    quantity = random.randint(5, 50)
                    reference = random.choice(REFERENCES_IN)
                else:
                    quantity = random.randint(1, min(product.current_stock, 20))
                    reference = random.choice(REFERENCES_OUT)

            if movement_type == "in":
                product.current_stock += quantity
            else:
                product.current_stock -= quantity

            movement = StockMovement(
                product_id=product.id,
                movement_type=movement_type,
                quantity=quantity,
                reference=reference,
                notes=f"{reference} - {product.sku}",
                created_at=timestamp,
            )
            db.add(movement)

        db.commit()

        print(f"Seed abgeschlossen:")
        print(f"  {len(supplier_objects)} Lieferanten erstellt")
        print(f"  {len(product_objects)} Produkte erstellt")
        print(f"  50 Bestandsbewegungen erstellt")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
