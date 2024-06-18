from django.contrib.auth.models import User
from core.models import Restaurant, Rating, Sale, Staff, StaffRestaurant, Comment, Task, TaskStatus, InProgressTask, CompletedTask, TodoTask
from django.utils import timezone
from django.db import connection
from pprint import pprint
import random
from django.db.models import F, Count, Q, Sum, Avg, Case, When, Value, Exists, OuterRef, Subquery
from django.db.models.functions import Coalesce, TruncMonth


def run():
    # select * from resaturant where restaurant_type=="CH" AND name startswith "c"
    """ restaurant = Restaurant.objects.filter(
        restaurant_type=Restaurant.TypeChoices.CHINESE, name__startswith="c")
    print(restaurant) """
    # select resstaurants where restaurant_type in chinese, indean and italian and name starts with P
    """  restaurants = Restaurant.objects.filter(restaurant_type__in=[
                                            Restaurant.TypeChoices.CHINESE, Restaurant.TypeChoices.INDIAN, Restaurant.TypeChoices.ITALIAN], name__startswith="P")
    print(restaurants) """

    # select restaurants where restaurant_type not in chinese, indean, italian

    """ restaurants = Restaurant.objects.exclude(restaurant_type__in=[
        Restaurant.TypeChoices.CHINESE, Restaurant.TypeChoices.INDIAN, Restaurant.TypeChoices.ITALIAN])
    print(restaurants) """
    # All ratings made to the restaurant that starts with c
    """ ratings = Rating.objects.filter(restaurant__name__startswith="c")

    print([rating.restaurant.name for rating in ratings]) """
    # sales for the chineese  restaurants
    """ sales = Sale.objects.filter(
        restaurant__restaurant_type=Restaurant.TypeChoices.CHINESE, income__range=(50, 80))
    print([sale.restaurant for sale in sales]) """
    # working with manytomany  relationships

    # staff, created = Staff.objects.get_or_create(name="John Doe")
    # set the many to many relation filed
    """ staff.restaurants.set(Restaurant.objects.all()[:10], through_defaults={
                          'salary': random.randint(1_000, 25_000)}) """

    # clear the many to many relationship
    # staff.restaurants.clear()

    # add a restaurant to the staff
    """ staff.restaurants.add(Restaurant.objects.first(),
                          through_defaults={"salary": 25_000}) """
    # get all staff for a single restaurant
    # restaurant = Restaurant.objects.first()
    # print(restaurant.staff_set.count())
    # Staff.objects.all().delete()
    # staff.restaurants.clear()

    # print(staff.restaurants.all())

    """ staff.restaurants.set(Restaurant.objects.all()[:10], through_defaults={
        "salary": random.randint(1000, 10000)
    })

    print(staff.restaurants.count()) """

    # F expressions

    """ rating = Rating.objects.first()
    rating.rating = F('rating') + 1
    rating.save()
    rating.refresh_from_db()
    print(rating.rating) """

    # get all sales that has profits
    """ sales = Sale.objects.all()
    for sale in sales:
        sale.expenditure = random.uniform(5, 100)

    Sale.objects.bulk_update(sales, ["expenditure"]) """

    """ sales = Sale.objects.filter(expenditure__gt=F('income'))
    print(sales) """
    # number of profite and losses
    """ sales = Sale.objects.aggregate(
        profit=Count("id", filter=Q(expenditure__lt=F('income'))),
        loss=Count("id", filter=Q(expenditure__gt=F('income')))
    )
    print(sales) """
    # calculate the profites
    """ sales = Sale.objects.annotate(
        profit=F('income') - F("expenditure")
    ).order_by('-profit')
    print(sales[0].profit) """
    # Q Expressions
    # we want to get the sales whre income is greater that expenditure or restaurant name contains a number
    """ profited = Q(income__gt=F('expenditure'))
    contains_number = Q(restaurant__name__regex=r"[0-9]+")
    sales1 = Sale.objects.select_related(
        'restaurant').filter(profited | contains_number)
    sales2 = Sale.objects.select_related('restaurant').filter(
        profited & contains_number
    )
    print(sales1.count())
    print(sales2.count()) """
    # print(restaurants)

    # COALESCE FUNCTION
    """  restaurant = Restaurant.objects.first()
    restaurant.capacity = 20
    restaurant.save()
    restaurant = Restaurant.objects.last()
    restaurant.capacity = 40
    restaurant.save()"""
    # sort the query through the nullable field using the nulls_last
    """ print(Restaurant.objects.order_by(F(
        'capacity').asc(nulls_last=True)).values_list('capacity', flat=True)) """
    # sorting the query through the nullable fields by merely removing the null values from the list
    """ print(Restaurant.objects.filter(capacity__isnull=False).order_by(
        '-capacity').values_list('capacity', flat=True)) """
    # use the coalesce to get the total capacity
    """ Restaurant.objects.update(capacity=None)
    print(Restaurant.objects.aggregate(
        total_capacity=Coalesce(Sum('capacity'), 0)
    )['total_capacity'])

    print(Rating.objects.filter(rating__lt=1).aggregate(
        avg_rating=Coalesce(Avg('rating'), 0.0)
    )['avg_rating'])
    r = Restaurant.objects.first()
    r.nickname = "westonmf"
    r.save()

    print(Restaurant.objects.annotate(
        username=Coalesce(F('nickname'), F('name'))
    ).values_list('username', flat=True))"""

    # CASE AND WHEN OBJECTS
    italian = Restaurant.TypeChoices.ITALIAN
    """ restaurants = Restaurant.objects.annotate(
        is_italian=Case(
            When(restaurant_type=italian, then=True),
            default=False
        )
    )
    print([r.restaurant_type for r in restaurants.filter(is_italian=True)]) """
    # list of all restaurants that has more than 8 sales
    """ print(
        Restaurant.objects.prefetch_related('sales').annotate(
            nsales=Count('sales')
        ).filter(nsales__gt=8).values_list('nsales', flat=True)
    ) """
    """ restaurants = Restaurant.objects.prefetch_related('sales').annotate(
        nsales=Count('sales')
    )
    restaurants = restaurants.annotate(
        most_popular=Case(
            When(nsales__gt=8, then=True),
            default=False
        )
    )
    print(restaurants.values('nsales', "most_popular")) """

    # get all restaurants that has avg rating greater than 3.5  and that has more than one rating
    """ restuarants = Restaurant.objects.prefetch_related('ratings').annotate(
        avg_rating=Avg('ratings__rating'),
        num_ratings=Count('ratings__pk')
    )
    restuarants = restuarants.annotate(
        highly_rated=Case(
            When(avg_rating__gt=3.5, num_ratings__gt=1, then=True),
            default=False
        )
    )

    print(restuarants.values('avg_rating', 'num_ratings', 'highly_rated')) """
    """ restuarants = Restaurant.objects.prefetch_related('ratings').annotate(
        avg_rating=Avg('ratings__rating')
    )
    restaurants = restuarants.annotate(
        rating_bucket=Case(
            When(avg_rating__gt=3.5, then=Value("Highly Rated")),
            When(avg_rating__range=(2.5, 3.5), then=Value("Average Rating")),
            When(avg_rating__lt=2.5, then=Value("Badly Rated"))
        )
    )
    print(restaurants.filter(rating_bucket="Highly Rated")) """
    """ types = Restaurant.TypeChoices
    european = Q(restaurant_type=types.GREEK) | Q(
        restaurant_type=types.ITALIAN) | Q(restaurant_type=types.INDIAN)
    america = Q(restaurant_type=types.CHINESE) | Q(
        restaurant_type=types.MEXICAN)
    restaurants = Restaurant.objects.annotate(
        continent=Case(
            When(european, then=Value("Europe")),
            When(america, then=Value("North America")),
            default=Value("N/A")
        )
    )

    print(restaurants.filter(continent="Europe")) """
    year = 2024

    # Query to calculate the monthly sales
    """ monthly_sales = (
        Sale.objects.filter(datetime__year=year)
        .annotate(month=TruncMonth('datetime'))
        .values('month')
        .annotate(total_sales=Sum('income'))
        .order_by('month')
    )
    print(monthly_sales.values('month', 'total_sales')) """
    # subquery outerref and exists fanctions
    # list all restaurants that has any sales with income greater than 85
    """restaurants = Restaurant.objects.prefetch_related('sales').filter(
        Exists(
            Sale.objects.filter(restaurant=OuterRef("pk"), income__gt=85)
        )
    )
    print([r.sales.all()[0].income for r in restaurants]) """

    # sales = Sale.objects.filter(restaurant__restaurant_type__in=['CH', 'IT'])
    """ restaurants = Restaurant.objects.filter(restaurant_type__in=['CH', 'IT'])
    sales = Sale.objects.filter(
        restaurant__in=Subquery(restaurants.values_list('pk', flat=True))
    ) """

    # print(sales.values_list("restaurant__restaurant_type").distinct())
    # print(restaurants.values_list("pk"))
    # annotate each restaurant from the income generated from its most recent sale
    """  sales = Sale.objects.filter(restaurant=OuterRef(
        'pk')).order_by('-datetime')
    restaurants = Restaurant.objects.annotate(
        last_income=Subquery(sales.values('income')[:1]),
        last_expenditure=Subquery(sales.values_list('expenditure')[:1]),
        profit=F('last_income') - F('last_expenditure')
    )
    print(restaurants.values_list('last_income', "last_expenditure", 'profit')) """

    # Generic Foreign Key content type models
    """  comment = Comment.objects.first()
    ctype = comment.content_type
    print(ctype)
    model = ctype.get_object_for_this_type(pk=comment.object_id)
    print(model)
    print(type(model)) """
    """ restaurant = Restaurant.objects.first()
    comment = Comment.objects.create(
        text="The food was awfull!",
        content_object=restaurant
    )
    print(comment)
    print(comment.__dict__) """

    """ restaurant = Restaurant.objects.get(pk=3)
    restaurant.comments.add(
        Comment.objects.create(
            text="text 1",
            content_object=restaurant
        )
    )
    print(restaurant.comments.all())
    print(restaurant.restaurant_type) """
    # all comments for the chinese restaurant
    """ comments = Comment.objects.filter(
        restaurant__restaurant_type=Restaurant.TypeChoices.CHINESE
    )
    print(comments) """
    # Prox models
    """ task = InProgressTask.objects.create(
        name="Going to work"
    )
    print("In Progress ")
    in_progress = InProgressTask.objects.all()
    print(in_progress)

    print("----------------")
    print("Todo ")
    todo = TodoTask.objects.all()
    print(todo)

    print("----------------")
    print("Completed ")
    completed = CompletedTask.objects.all()
    print(completed) """

    # Property, Model Methods and get_absolute_url method
    restaurant = Restaurant.objects.first()
    restaurant.date_opened = timezone.now().date()
    restaurant.save()
    five_days_ago = timezone.now().date() - timezone.timedelta(days=5)
    print(restaurant.is_opened_after(five_days_ago))

    # print(connection.queries)
