from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, F, Case, When, BigIntegerField
from django.db.models.functions import Coalesce
from apps.merchants.models import Merchant, LedgerEntry
from apps.payouts.models import Payout
from .serializers import LedgerEntrySerializer, MerchantSerializer
from apps.payouts.serializers import PayoutSerializer

class MerchantListView(APIView):
    def get(self, request):
        merchants = Merchant.objects.all()
        serializer = MerchantSerializer(merchants, many=True)
        return Response(serializer.data)

class MerchantBalanceView(APIView):
    def get(self, request, merchant_id):
        # ledger balance
        ledger = LedgerEntry.objects.filter(merchant_id=merchant_id).aggregate(
            balance=Coalesce(Sum(
                Case(
                    When(entry_type='credit', then=F('amount_paise')),
                    When(entry_type='debit', then=-F('amount_paise')),
                    output_field=BigIntegerField()
                )
            ), 0, output_field=BigIntegerField())
        )['balance']

        held = Payout.objects.filter(merchant_id=merchant_id, status__in=['pending', 'processing']).aggregate(
            held=Coalesce(Sum('amount_paise'), 0, output_field=BigIntegerField())
        )['held']

        available = ledger - held
        return Response({
            'ledger_balance': ledger,
            'held_balance': held,
            'available_balance': available,
        })

class MerchantLedgerView(APIView):
    def get(self, request, merchant_id):
        qs = LedgerEntry.objects.filter(merchant_id=merchant_id).order_by('-created_at')
        # simple pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 25))
        start = (page - 1) * page_size
        end = start + page_size
        serializer = LedgerEntrySerializer(qs[start:end], many=True)
        return Response({
            'results': serializer.data,
            'page': page,
            'page_size': page_size,
            'total': qs.count(),
        })

class MerchantPayoutListView(APIView):
    def get(self, request, merchant_id):
        qs = Payout.objects.filter(merchant_id=merchant_id).order_by('-created_at')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 25))
        start = (page - 1) * page_size
        end = start + page_size
        serializer = PayoutSerializer(qs[start:end], many=True)
        return Response({
            'results': serializer.data,
            'page': page,
            'page_size': page_size,
            'total': qs.count(),
        })
