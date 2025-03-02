from django.db import models
from django.db.models import Sum, F, DecimalField

class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

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
    items = models.ManyToManyField(Item)
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
    tax = models.ForeignKey(Tax, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def total_price(self):
        items_price = self.items.aggregate(total=Sum('price', output_field=DecimalField()))['total'] or 0
        discount_percentage = self.discount.percentage if self.discount else 0
        tax_percentage = self.tax.percentage if self.tax else 0

        discount_amount = (discount_percentage / 100) * items_price
        subtotal = items_price - discount_amount
        tax_amount = (tax_percentage / 100) * subtotal

        return subtotal + tax_amount

    def __str__(self):
        return f"Order {self.id} - Total: {self.total_price:.2f}"
