from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Restaurant, Order


class ProductStockException(Exception):
    pass


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ('name', 'restaurant_type')


class ProductOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("product", "number_of_items")

    def save(self, commit=True):
        order = super().save(commit=False)
        if order.product.number_in_stock < order.number_of_items:
            raise ProductStockException(
                f"Not Enough Items in stock for the product {order.product}"
            )
        if commit:
            order.save()
        return order
