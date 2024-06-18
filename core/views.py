from django.shortcuts import render, redirect, get_object_or_404
from .models import Restaurant, Rating, Sale, StaffRestaurant, Product
from .forms import RestaurantForm, ProductOrderForm
from django.db.models import Sum, Prefetch
from django.utils import timezone
from django.db import transaction
from functools import partial


# Create your views here.
def index(request):
    # prefetch_related function
    restaurents = Restaurant.objects.prefetch_related('ratings')
    # select related function
    """ ratings = Rating.objects.only(
        'restaurant__name').select_related('restaurant')
    context = {
        "ratings": ratings
    } """

    # list all 5 star restaurants and the sales
    """ restaurants = Restaurant.objects.prefetch_related("ratings", 'sales')\
        .filter(ratings__rating=5)\
        .annotate(total=Sum("sales__income"))
    print([r.total for r in restaurants]) """
    # get the monthly sales for the 5 star restaurants
    """  month_ago = timezone.now() - timezone.timedelta(days=30)
    monthly_sales = Prefetch(
        'sales',
        queryset=Sale.objects.filter(datetime__gte=month_ago)
    )
    restaurants = Restaurant.objects.prefetch_related('ratings', monthly_sales)\
        .filter(ratings__rating=5)\
        .annotate(total=Sum('sales__income'))
    print("Month sales for the 5 star restuarants",
          [r.total for r in restaurants]) """

    # demonstrating how we can use the prefetch on the many to many fields
    """ jobs = StaffRestaurant.objects.prefetch_related('restaurant', 'staff')
    for job in jobs:
        print(
            f"Restuarant name {job.restaurant.name}, Staff name {job.staff.name}") """

    restaurants = Restaurant.objects.all()

    return render(request, 'index.html', {"restaurants": restaurants})


def email_user(email):
    print(f"Dear {email}, Thank you for your order")


def create_order(request):
    if request.method == 'POST':
        form = ProductOrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # locking the product for update
                product = Product.objects.select_for_update(nowait=True).get(
                    pk=form.cleaned_data['product'].pk
                )

                order = form.save()
                # server crash
                order.product.number_in_stock -= order.number_of_items
                order.product.save()
            # sending the email to the user when the transaction is successfull
            transaction.on_commit(partial(email_user, "westonmf@gmail.com"))
            return redirect('create-order')
        else:
            context = {
                "form": form
            }
            return render(request, 'create_order.html', context)

    form = ProductOrderForm()
    context = {
        "form": form
    }
    return render(request, 'create_order.html', context)


def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    context = {
        'restaurant': restaurant
    }
    return render(request, 'restaurant_detail.html', context)
