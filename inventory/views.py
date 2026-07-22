from django.shortcuts import render
from .models import Product, Category
from django.contrib.auth.decorators import login_required
from .compatibility import check_compatibility

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
    if request.GET.get("check") and selected_products:
        result = check_compatibility(selected_products)

    return render(request, "inventory/compatibility.html", {
        "groups": groups,
        "selected_products": selected_products,
        "result": result,
    })