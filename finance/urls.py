from rest_framework import routers

from finance.views import ContractViewSet, RecordViewSet, CategoryViewSet, AccountViewSet

app_name = 'finance'

router = routers.DefaultRouter()
router.register('records', RecordViewSet)
router.register('contracts', ContractViewSet)
router.register('categories', CategoryViewSet)
router.register('accounts', AccountViewSet)

urlpatterns = router.urls
