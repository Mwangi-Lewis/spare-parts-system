from django.shortcuts import render
from .models import Product, Category
from django.contrib.auth.decorators import login_required
from .compatibility import check_compatibility
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .models import SerialNumber, Sale
from django.db.models import Sum, Count, F


SOCKETS_WITH_IMAGES = {"AM5", "LGA1700"}

@login_required
def product_list(request):
    """Catalogue page with search and category filtering."""
    products = Product.objects.select_related("category").all()

    query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "")

    if query:
        # match on either the part name or the brand
        products = products.filter(name__icontains=query) | \
                   products.filter(brand__icontains=query)

    if selected_category:
        products = products.filter(category__name=selected_category)

    context = {
        "products": products.order_by("category__name", "brand"),
        "categories": Category.objects.all().order_by("name"),
        "query": query,
        "selected_category": selected_category,
    }
    return render(request, "inventory/product_list.html", context)

@login_required
def compatibility_check(request):
    """Select components and check whether they work together."""
    category_names = ["CPU", "Motherboard", "RAM", "GPU", "Storage", "PSU"]

    groups = []
    selected_products = []

    for name in category_names:
        chosen_id = request.GET.get(name, "")
        groups.append({
            "name": name,
            "products": Product.objects.filter(
                category__name=name
            ).order_by("brand", "name"),
            "selected": chosen_id,
        })
        if chosen_id:
            product = Product.objects.filter(id=chosen_id).first()
            if product:
                selected_products.append(product)

    result = None
    socket_visual = None

    if request.GET.get("check") and selected_products:
        result = check_compatibility(selected_products)

        # Build the visual comparison only for a genuine socket mismatch
        if not result["compatible"]:
            cpu = next(
                (p for p in selected_products if p.category.name == "CPU"), None
            )
            board = next(
                (p for p in selected_products if p.category.name == "Motherboard"),
                None,
            )
            if cpu and board:
                cpu_socket = cpu.attributes.get("socket")
                board_socket = board.attributes.get("socket")
                mismatch = cpu_socket != board_socket
                have_images = (
                    cpu_socket in SOCKETS_WITH_IMAGES
                    and board_socket in SOCKETS_WITH_IMAGES
                )
                if mismatch and have_images:
                    socket_visual = {
                        "cpu": cpu,
                        "board": board,
                        "cpu_socket": cpu_socket,
                        "board_socket": board_socket,
                        "cpu_image": f"inventory/img/cpu_{cpu_socket.lower()}.jpg",
                        "board_image": f"inventory/img/socket_{board_socket.lower()}.jpg",
                    }

    return render(request, "inventory/compatibility.html", {
        "groups": groups,
        "selected_products": selected_products,
        "result": result,
        "socket_visual": socket_visual,
    })
    
@login_required
def checkout(request):
    """Sell parts. Each sale consumes one serial-numbered unit."""
    products = Product.objects.select_related("category").order_by(
        "category__name", "brand"
    )

    rows = []
    for product in products:
        available = product.serial_numbers.filter(
            status=SerialNumber.IN_STOCK
        ).count()
        rows.append({"product": product, "available": available})

    recent_sales = Sale.objects.select_related(
        "serial_number__product", "user"
    ).order_by("-sale_date")[:8]

    return render(request, "inventory/checkout.html", {
        "rows": rows,
        "recent_sales": recent_sales,
    })


@login_required
def sell_product(request, product_id):
    """Consume one serial number, mark it Sold, decrement stock, record the sale."""
    if request.method != "POST":
        return redirect("checkout")

    product = get_object_or_404(Product, id=product_id)

    with transaction.atomic():
        serial = product.serial_numbers.filter(
            status=SerialNumber.IN_STOCK
        ).order_by("serial_code").first()

        if serial is None:
            messages.error(
                request,
                f"No units of {product.brand} {product.name} are available."
            )
            return redirect("checkout")

        serial.status = SerialNumber.SOLD
        serial.save()

        product.stock_quantity = max(0, product.stock_quantity - 1)
        product.save()

        Sale.objects.create(
            serial_number=serial,
            user=request.user,
            sale_price=product.price,
        )

    messages.success(
        request,
        f"Sold {product.brand} {product.name} — serial {serial.serial_code} "
        f"marked as Sold. {product.stock_quantity} left in stock."
    )
    return redirect("checkout")

@login_required
def dashboard(request):
    """Summary of stock levels, low-stock items and recent sales."""
    products = Product.objects.select_related("category")

    # --- headline figures ---
    total_products = products.count()
    total_units = products.aggregate(total=Sum("stock_quantity"))["total"] or 0
    units_sold = SerialNumber.objects.filter(status=SerialNumber.SOLD).count()
    units_available = SerialNumber.objects.filter(
        status=SerialNumber.IN_STOCK
    ).count()

    # --- low stock (threshold comparison done in the database) ---
    low_stock = products.filter(
        stock_quantity__lte=F("low_stock_threshold")
    ).order_by("stock_quantity", "category__name")

    # --- stock grouped by category ---
    by_category = (
        Category.objects
        .annotate(
            part_count=Count("products", distinct=True),
            unit_count=Sum("products__stock_quantity"),
        )
        .order_by("name")
    )

    # --- sales ---
    recent_sales = Sale.objects.select_related(
        "serial_number__product__category", "user"
    ).order_by("-sale_date")[:8]

    revenue = Sale.objects.aggregate(total=Sum("sale_price"))["total"] or 0

    return render(request, "inventory/dashboard.html", {
        "total_products": total_products,
        "total_units": total_units,
        "units_sold": units_sold,
        "units_available": units_available,
        "low_stock": low_stock,
        "by_category": by_category,
        "recent_sales": recent_sales,
        "revenue": revenue,
    })