import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views import View
from requests import session

from .models import Item, Discount, Tax, Order
from django.shortcuts import redirect
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    order, created = Order.objects.get_or_create(is_confirmed=False)
    return order.create_stripe_payment(request)

class ItemListView(View):
    def get(self, request):
        order, created = Order.objects.get_or_create(is_confirmed=False)
        items = Item.objects.all()
        print(order.items)
        return render(request, 'list.html', {'items': items})


class ItemDetailView(View):
    def get(self, request, pk):
        order, created = Order.objects.get_or_create(is_confirmed=False)
        item = get_object_or_404(Item, pk=pk)
        return render(request, 'item.html', {'item': item})


class CartView(View):
    def get(self, request):
        order, created = Order.objects.get_or_create(is_confirmed=False)

        item_with_count = []
        items_price = 0
        discount_amount = 0
        tax_amount = 0

        for item in order.items.all():
            quantity = item.quantity
            item_with_count.append({
                'item': item,
                'quantity': quantity,
                'price': item.price * quantity
            })
            items_price += item.price * quantity

        discount = Discount.objects.first()
        tax = Tax.objects.first()

        if discount:
            discount_amount = (discount.percentage / 100) * items_price

        subtotal = items_price

        if tax:
            tax_amount = (tax.percentage / 100) * (subtotal - discount_amount)

        total_price = subtotal + tax_amount - discount_amount

        return render(request, 'cart.html', {
            'items': item_with_count,
            'total_price': total_price,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'tax_amount': tax_amount,
            'cart': order
        })

    def post(self, request):
        order, created = Order.objects.get_or_create(is_confirmed=False)
        item_id = request.POST.get('item_id')
        if item_id:
            cart = request.session.get('cart', [])
            order.add_item(item_id)
            request.session['cart'] = cart
        return redirect('cart')

def success_view(request):
    order = Order.objects.filter(is_confirmed=False).order_by('-id').first()

    if order:
        order.is_confirmed = True
        order.save()
    return render(request, 'success.html')
