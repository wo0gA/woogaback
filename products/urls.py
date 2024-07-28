from django.urls import path
from .views import *

urlpatterns = [
    path("", ProductList.as_view()),
    path("<int:product_id>/", ProductDetail.as_view()),
    path("<int:product_id>/reviews/", ReviewList.as_view()),
    path("categories/", CategoryList.as_view()),
    path("<int:product_id>/availability/", RentalAvailability.as_view())
]