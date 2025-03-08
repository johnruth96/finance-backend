from django.conf.urls import include
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('v1/transactions/', include('transactions.urls', namespace='transactions')),
    path('v1/', include('finance.urls', namespace='finance')),
]
