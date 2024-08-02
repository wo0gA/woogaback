from django.urls import path
from .views import *

urlpatterns = [

    path('rental/', RentalHistoryList.as_view()),
    path('enrollment/<int:product_id>/', EnrollmentHistoryList.as_view()),
    path('', HistoryList.as_view()),
    path('<int:rentalhistory_id>/', HistoryListDetail.as_view()),
]