import uuid
from django.db import models
from django.db.models import Sum, F, DecimalField
import stripe
from django.http import JsonResponse
from stripe_project import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Discount(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class Tax(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    items = models.ManyToManyField('Item')
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
    tax = models.ForeignKey(Tax, null=True, blank=True, on_delete=models.SET_NULL)
    is_confirmed = models.BooleanField(default=False)

    @property
    def total_price(self):
        items_price = self.items.aggregate(total=Sum('price', output_field=DecimalField()))['total'] or 0
        discount_percentage = self.discount.percentage if self.discount else 0
        tax_percentage = self.tax.percentage if self.tax else 0

        discount_amount = (discount_percentage / 100) * items_price
        subtotal = items_price - discount_amount
        tax_amount = (tax_percentage / 100) * subtotal

        return subtotal + tax_amount

    def add_item(self, item_id, quantity=1):
        item = Item.objects.get(id=item_id)
        if item in self.items.all():
            item.quantity += quantity
            item.save()
        else:
            item.quantity = quantity
            item.save()
            self.items.add(item)

    def create_stripe_payment(self, request):
        line_items = []
        for item in self.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'rub',
                    'product_data': {
                        'name': item.name,
                    },
                    'unit_amount': int(item.price * 100),
                },
                'quantity': item.quantity,
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
