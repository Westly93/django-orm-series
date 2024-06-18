from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse


def validate_restaurant_name_begins_with_a(value):
    if not value.startswith('a'):
        raise ValidationError('Restaurant name must begin with "a"')


class Staff(models.Model):
    name = models.CharField(max_length=255, unique=True)
    restaurants = models.ManyToManyField(
        "Restaurant", through="StaffRestaurant")

    def __str__(self):
        return self.name


class StaffRestaurant(models.Model):
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    staff = models.ForeignKey("Staff", on_delete=models.CASCADE)
    salary = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.staff} {self.restaurant} {self.salary}"


class Restaurant(models.Model):
    class TypeChoices(models.TextChoices):
        INDIAN = 'IN', 'Indian'
        CHINESE = 'CH', 'Chinese'
        ITALIAN = 'IT', 'Italian'
        GREEK = 'GR', 'Greek'
        MEXICAN = 'MX', 'Mexican'
        FASTFOOD = 'FF', 'Fast Food'
        OTHER = 'OT', 'Other'

    name = models.CharField(max_length=100, validators=[
                            validate_restaurant_name_begins_with_a])
    website = models.URLField(default='')
    date_opened = models.DateField()
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)])
    restaurant_type = models.CharField(
        max_length=2, choices=TypeChoices.choices)
    capacity = models.PositiveSmallIntegerField(null=True, blank=True)
    nickname = models.CharField(max_length=255, default='')
    comments = GenericRelation("Comment", related_query_name="restaurant")

    class Meta:
        ordering = [Lower('name')]

    # django property methods
    @property
    def restaurant_name(self):
        return self.nickname or self.name

    # model methods
    def is_opened_after(self, date_opened) -> bool:
        return self.date_opened > date_opened

    # absolute url
    def get_absolute_url(self):
        return reverse("restaurant-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        print(self._state.adding)
        super().save(*args, **kwargs)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comments = GenericRelation("Comment")

    def __str__(self):
        return f"Rating: {self.rating}"


class Sale(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.SET_NULL, null=True, related_name='sales')
    income = models.DecimalField(max_digits=8, decimal_places=2)
    expenditure = models.PositiveSmallIntegerField(default=0)
    datetime = models.DateTimeField()

    # generated fields
    """ profit = models.GeneratedField(
        expression=models.F('income') - models.F('expenditure'),
        output_field=models.DecimalField(max_digits=8, decimal_places=2),
        db_persist=True
    ) """


class Product(models.Model):
    name = models.CharField(max_length=128)
    number_in_stock = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    number_of_items = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.product} * {self.number_of_items}'


class Comment(models.Model):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveSmallIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
# prox models


class TaskStatus(models.IntegerChoices):
    TODO = 1
    IN_PROGRESS = 2
    COMPLETED = 3


class Task(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateField(auto_now_add=True)
    status = models.IntegerField(choices=TaskStatus.choices)

    def __str__(self):
        return self.name


# Todo task proxy model
class TodoTask(Task):
    class Meta:
        proxy = True
        ordering = ('created_at',)

    class Manager(models.Manager):
        def get_queryset(self) -> models.QuerySet:
            return super().get_queryset().filter(status=TaskStatus.TODO)

    objects = Manager()
# Proxy model that filters all tasks in progress


class InProgressTask(Task):
    class Meta:
        proxy = True

    class Manager(models.Manager):
        def get_queryset(self) -> models.QuerySet:
            return super().get_queryset().filter(status=TaskStatus.IN_PROGRESS)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.status = TaskStatus.IN_PROGRESS
        super().save(*args, **kwargs)
    objects = Manager()
# completed tasks proxy model


class CompletedTask(Task):
    class Meta:
        proxy = True

    class Manager(models.Manager):
        def get_queryset(self) -> models.QuerySet:
            return super().get_queryset().filter(status=TaskStatus.COMPLETED)
    objects = Manager()
