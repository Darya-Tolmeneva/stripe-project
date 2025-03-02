import json

from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Item, Discount, Tax, Order
from django.shortcuts import redirect
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import Counter

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            total = data.get('total', 0)
            print(data)

            line_items = []
            for item in items:
                print(item)
                product_id = int(item['id'])
                items_info = get_object_or_404(Item, id=product_id)
                price = stripe.Price.create(
                    unit_amount=int(items_info.price * 100),
                    currency='rub',
                    product_data={
                        'name': items_info.name,
                    },
                )

                line_items.append({
                    'price': price.id,
                    'quantity': item['quantity'],
                })

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cart/'),
            )
            return JsonResponse({
                'session_id': session.id,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY
            })
        except Exception as e:
            error_response = {'error': str(e)}
            print(error_response)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)

class ItemListView(View):
    def get(self, request):
        items = Item.objects.all()
        cart = request.session.get('cart', [])
        return render(request, 'list.html', {'items': items, 'cart': cart})


class ItemDetailView(View):
    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        cart = request.session.get('cart', [])
        return render(request, 'item.html', {'item': item, 'cart': cart})


class CartView(View):
    def get(self, request):
        cart = request.session.get('cart', [])
        print(cart)
        items = Item.objects.filter(id__in=cart)
        cart_counts = Counter(cart)

        item_with_count = [
            {
                'item': item,
                'quantity': cart_counts.get(item.id, 0),
                'price': item.price*cart_counts.get(item.id, 0)
            }
            for item in items
        ]
        items_price = sum(item.price * cart_counts.get(item.id, 0) for item in items)

        discount = Discount.objects.first()
        tax = Tax.objects.first()

        discount_amount = (discount.percentage / 100) * items_price if discount else 0
        subtotal = items_price
        tax_amount = (tax.percentage / 100) * (subtotal - discount_amount) if tax else 0
        total_price = subtotal + tax_amount

        return render(request, 'cart.html', {
            'items': item_with_count,
            'total_price': total_price,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'tax_amount': tax_amount,
            'cart': cart
        })

    def post(self, request):
        item_id = request.POST.get('item_id')
        if item_id:
            cart = request.session.get('cart', [])
            cart.append(int(item_id))
            request.session['cart'] = cart
        return redirect('cart')

def success_view(request):
    return render(request, 'success.html')
