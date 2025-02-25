from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
import stripe

from .models import Item

def buy_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': int(item.price * 100),  # Stripe принимает цену в центах
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/success/',
        cancel_url='http://127.0.0.1:8000/cancel/',
    )

    return JsonResponse({'session_id': session.id})

def item_page(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'item.html', {'item': item, 'stripe_public_key': settings.STRIPE_PUBLIC_KEY})
