from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment initiation
    path('pay/<int:appointment_id>/', views.initiate_payment, name='initiate'),
    path('qr/<int:payment_id>/', views.show_qr_code, name='qr_code'),
    path('detail/<int:payment_id>/', views.payment_detail, name='detail'),
    
    # Payment confirmation
    path('confirm/<int:payment_id>/', views.confirm_payment, name='confirm'),
    path('upload-proof/<int:payment_id>/', views.upload_payment_proof, name='upload_proof'),
    
    # Payment history
    path('history/', views.payment_history, name='history'),
    path('qr-paid/', views.qr_paid_list, name='qr_paid'),
    # Cash commitments listing (separate page)
    path('cash-commitments/', views.cash_commitments, name='cash_commitments'),
]