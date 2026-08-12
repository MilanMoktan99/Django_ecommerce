from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .models import Cart, CartItem

@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True
    )

    if product.stock <= 0:
        messages.error(
            request,
            f'{product.name} is out of stock.'
        )
        return redirect(
            'product_detail',
            pk=product.id
        )

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:

        if cart_item.quantity >= product.stock:
            messages.error(
                request,
                'You cannot add more than the available stock.'
            )

            return redirect(
                'cart:cart_detail'
            )

        cart_item.quantity += 1
        cart_item.save()

    messages.success(
        request,
        f'{product.name} added to cart.'
    )

    return redirect(
        'cart:cart_detail'
    )

@login_required
def cart_detail(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        'cart/cart_detail.html',
        {
            'cart': cart,
            'items': cart.items.all(),
            'total': cart.get_total(),
        }
    )
    
@login_required
def increase_quantity(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart:cart_detail')

@login_required
def decrease_quantity(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart:cart_detail')

@login_required
def remove_from_cart(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    cart_item.delete()

    messages.success(
        request,
        'Item removed from cart.'
    )

    return redirect('cart:cart_detail')