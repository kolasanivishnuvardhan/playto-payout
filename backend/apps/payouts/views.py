from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from .models import Payout
from .serializers import PayoutSerializer
from .services import create_payout_idempotent
from .tasks import process_payout

class CreatePayoutView(APIView):
    def post(self, request):
        merchant_id = request.data.get('merchant_id')
        amount_paise = request.data.get('amount_paise')
        bank_account_id = request.data.get('bank_account_id')
        idempotency_key = request.headers.get('Idempotency-Key')
        if not idempotency_key:
            return Response({'detail': 'Idempotency-Key header required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount_paise = int(amount_paise)
        except (ValueError, TypeError):
            return Response({'detail': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        if amount_paise <= 0:
            return Response({'detail': 'Amount must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payout, created = create_payout_idempotent(
                merchant_id=merchant_id,
                amount_paise=amount_paise,
                bank_account_id=bank_account_id,
                idempotency_key=idempotency_key
            )
        except Exception as e:
            if 'InsufficientFunds' in type(e).__name__ or 'InsufficientFunds' in str(e):
                return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Trigger async processing if newly created
        if created:
            process_payout.apply_async(args=[str(payout.id)], countdown=1)

        serializer = PayoutSerializer(payout)
        return Response(serializer.data, status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK))

class PayoutDetailView(APIView):
    def get(self, request, payout_id):
        payout = get_object_or_404(Payout, id=payout_id)
        serializer = PayoutSerializer(payout)
        return Response(serializer.data)
