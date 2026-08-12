from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Cart
from .models import Order, OrderItem

@login_required
@transaction.atomic
def checkout(request):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    items = list(
        cart.items.select_related('product')
    )

    if not items:
        messages.error(
            request,
            'Your cart is empty.'
        )
        return redirect('cart_detail')

    for item in items:
        if (
            not item.product.is_available
            or item.product.stock < item.quantity
        ):
            messages.error(
                request,
                f'Not enough stock for {item.product.name}.'
            )
            return redirect('cart_detail')

    total = cart.get_total()

    if request.method == 'POST':

        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )

        for item in items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            item.product.stock -= item.quantity
            item.product.save()

        cart.items.all().delete()

        messages.success(
            request,
            'Order placed successfully.'
        )

        return redirect(
            'order_detail',
            pk=order.pk
        )

    return render(
        request,
        'orders/checkout.html',
        {
            'cart': cart,
            'items': items,
            'total': total,
        }
    )
    
@login_required
def order_list(request):

    orders = Order.objects.filter(
        user=request.user
    )

    return render(
        request,
        'orders/order_list.html',
        {
            'orders': orders
        }
    )
    
@login_required
def order_detail(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk,
        user=request.user
    )

    return render(
        request,
        'orders/order_detail.html',
        {
            'order': order
        }
    )