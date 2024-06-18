from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('order/', views.create_order, name='create-order'),
    path('restaurant-detail/<int:pk>/',
         views.restaurant_detail, name="restaurant-detail"),
]
