from django.urls import path
from .views import *

urlpatterns = [

    path('rental/', RentalHistoryStatus.as_view()),
    path('enrollment/', EnrollmentHistoryStatus.as_view()),
    path('', RentalHistoryList.as_view())

]