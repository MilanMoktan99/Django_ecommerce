from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Product

def product_list(request):
    products = Product.objects.filter(
        is_available=True
    )

    categories = Category.objects.all()

    # Search
    search = request.GET.get('search', '').strip()

    if search:
        products = products.filter(
            name__icontains=search
        )

    # Category filter
    category_id = request.GET.get('category')

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    context = {
        'products': products,
        'categories': categories,
        'search': search,
    }

    return render(
        request,
        'products/product_list.html',
        context
    )

def product_detail(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk
    )

    return render(
        request,
        'products/product_detail.html',
        {'product': product}
    )

@login_required
def product_create(request):
    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to create products.'
        )
        return redirect('product_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')

        category = get_object_or_404(
            Category,
            id=category_id
        )

        Product.objects.create(
            name=name,
            category=category,
            description=description,
            price=price,
            stock=stock,
            image=image,
        )

        messages.success(
            request,
            'Product created successfully.'
        )

        return redirect('product_list')

    categories = Category.objects.all()

    return render(
        request,
        'products/product_form.html',
        {'categories': categories}
    )

@login_required
def product_update(request, pk):
    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to edit products.'
        )
        return redirect('product_list')

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category_id = request.POST.get('category')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()

        messages.success(
            request,
            'Product updated successfully.'
        )

        return redirect(
            'product_detail',
            pk=product.pk
        )

    categories = Category.objects.all()

    return render(
        request,
        'products/product_form.html',
        {
            'product': product,
            'categories': categories,
        }
    )

@login_required
def product_delete(request, pk):
    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to delete products.'
        )
        return redirect('product_list')

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == 'POST':
        product.delete()

        messages.success(
            request,
            'Product deleted successfully.'
        )

        return redirect('product_list')

    return render(
        request,
        'products/product_confirm_delete.html',
        {'product': product}
    )