from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from core.models import Restaurant, Sale, Rating, Order, Product, Comment, Task


class CommentInline(GenericTabularInline):
    model = Comment
    max_num = 1


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [
        CommentInline
    ]


class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'rating']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['text', 'content_type', 'object_id', 'content_object']


# Register your models here.
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Sale)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Task)
