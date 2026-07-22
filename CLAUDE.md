# Computer Spare Parts Management System

## Project context
Undergraduate group project. Django 6.0 + Python 3.14 + SQLite.
Hard deadline: 2 weeks. Methodology: Crystal Clear (Agile).
This is a SMALL academic project. Prefer the simplest thing that works.
Django's built-in admin and auth are used deliberately to save time.

## What the system does
An inventory system for a shop selling PC parts. It tracks stock down to
individual serial-numbered units, and — the key feature — checks whether
selected components are physically compatible before a sale.

## App structure
Project: sparepartsystem
App: inventory  (all models, views and logic live here)

## Data model (exact — do not rename or add fields)
Use Django's built-in User model for auth. Roles: Admin and Cashier,
implemented with Django Groups or a simple role field. Do not build a custom
user system.

Category:   category_id (PK), name
Product:    product_id (PK), name, category (FK to Category), brand, price,
            stock_quantity, low_stock_threshold, attributes (JSONField)
SerialNumber: serial_id (PK), product (FK to Product), serial_code,
            status ("In Stock" / "Sold")
Sale:       sale_id (PK), serial_number (FK to SerialNumber),
            user (FK to User), sale_date, sale_price

Relationships:
- Category 1-to-many Product
- Product 1-to-many SerialNumber
- SerialNumber 1-to-1 Sale
- User 1-to-many Sale

## Categories
CPU, GPU, RAM, Motherboard, Storage, PSU

## JSON attribute keys (stored in Product.attributes)
CPU:         socket, wattage
Motherboard: socket, ddr_gen, form_factor
RAM:         ddr_gen, wattage
GPU:         wattage
PSU:         wattage
Storage:     wattage

## Compatibility rules (exactly three — no more)
1. Socket match:  CPU.socket == Motherboard.socket
2. RAM match:     RAM.ddr_gen == Motherboard.ddr_gen
3. Power check:   sum(component wattage) <= PSU.wattage * 0.85

Return either "Compatible" or a list of explicit error messages
(e.g. "CPU socket AM5 does not match motherboard socket LGA1700").

## Features in scope
- Catalogue CRUD for parts (six categories above)
- Technical spec attributes per part
- Stock level tracking
- Search / filter on the catalogue
- Low-stock flag
- Compatibility checker (the three rules above)
- Serialized inventory: unique serial number per physical unit
- Checkout: consume a serial number, mark it Sold, decrement stock, record Sale
- Login with Admin / Cashier roles
- Dashboard: total stock, low-stock items, recent sales

## OUT OF SCOPE - DO NOT IMPLEMENT
- EOQ, demand forecasting, safety stock, ABC analysis, or any inventory maths
- PCIe lane checks, case/GPU length, cooler height clearance
- Multi-warehouse or bin locations
- Barcode / RFID scanning
- Supplier pricing algorithms
- Online payments
- REST API / DRF (unless explicitly asked)
- Docker, CI/CD, celery, redis, or any extra infrastructure

## Working rules
- One feature at a time. Do not build ahead.
- Use Plan mode for anything touching more than one file.
- Keep code readable and commented — the author must be able to explain
  every line to an examiner.
- Do not refactor working code unless asked.
- Do not add third-party packages without asking first.
