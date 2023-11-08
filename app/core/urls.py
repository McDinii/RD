from django.urls import path
from core.views.network_views import (
    NodeListAPIView,
    NodeDetailAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
    ClearDebtAPIView,
    CountryNodeListAPIView,
    HighDebtNodesAPIView,
    ProductNodesAPIView,
)
from core.views.register_views import registration_view
from core.views.email_views import NodeQRCodeView
urlpatterns = [
    path('nodes/', NodeListAPIView.as_view(), name='node-list'),
    path('nodes/<int:node_id>/', NodeDetailAPIView.as_view(), name='node-detail'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:product_id>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('nodes/clear_debt/', ClearDebtAPIView.as_view(), name='clear-debt'),
    path('nodes/country/<str:country>/', CountryNodeListAPIView.as_view(), name='country-node-list'),
    path('nodes/high_debt/', HighDebtNodesAPIView.as_view(), name='high-debt-nodes'),
    path('products/nodes/<int:product_id>/', ProductNodesAPIView.as_view(), name='product-nodes'),
    path('register/',registration_view, name="register"),
    path('node/email/qr-code/',NodeQRCodeView.as_view(), name='contact-qr-code')
]
