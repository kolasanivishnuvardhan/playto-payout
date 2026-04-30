from django.urls import path
from . import views

urlpatterns = [
    path('payouts/', views.CreatePayoutView.as_view(), name='create-payout'),
    path('payouts/<uuid:payout_id>/', views.PayoutDetailView.as_view(), name='payout-detail'),
]
