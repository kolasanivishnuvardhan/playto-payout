from django.urls import path
from . import views

urlpatterns = [
    path('merchants/', views.MerchantListView.as_view(), name='merchant-list'),
    path('merchants/<uuid:merchant_id>/balance/', views.MerchantBalanceView.as_view(), name='merchant-balance'),
    path('merchants/<uuid:merchant_id>/ledger/', views.MerchantLedgerView.as_view(), name='merchant-ledger'),
    path('merchants/<uuid:merchant_id>/payouts/', views.MerchantPayoutListView.as_view(), name='merchant-payouts'),
]
