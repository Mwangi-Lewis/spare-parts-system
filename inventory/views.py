from django.shortcuts import render
from .models import Product, Category


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
