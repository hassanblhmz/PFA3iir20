"""
URL Configuration principale - PFA Gestion Achats
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import AccountsView, GestAchatsLoginView, GestAchatsLogoutView, HomeView
from users.views import CustomTokenObtainPairView

admin.site.site_header = 'GestAchats Administration'
admin.site.site_title = 'GestAchats'
admin.site.index_title = 'Gestion des achats et approvisionnements'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('styles.css', serve, {'path': 'styles.css', 'document_root': settings.BASE_DIR.parent / 'frontend'}),
    path('login/', GestAchatsLoginView.as_view(), name='login'),
    path('logout/', GestAchatsLogoutView.as_view(), name='logout'),
    path('notifications/<int:pk>/open/', views.notification_open, name='notification-open'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications-mark-all-read'),
    path('accounts/', AccountsView.as_view(), name='accounts'),
    path('products/', views.product_list, name='product-list'),
    path('products/new/', views.product_create, name='product-create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product-edit'),
    path('suppliers/', views.supplier_list, name='supplier-list'),
    path('suppliers/new/', views.supplier_create, name='supplier-create'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier-edit'),
    path('requests/', views.request_list, name='request-list'),
    path('requests/new/', views.request_create, name='request-create'),
    path('requests/<int:pk>/', views.request_detail, name='request-detail'),
    path('requests/<int:pk>/add-line/', views.request_add_line, name='request-add-line'),
    path('requests/<int:pk>/submit/', views.request_submit, name='request-submit'),
    path('requests/<int:pk>/validate/', views.request_validate, name='request-validate'),
    path('requests/<int:pk>/reject/', views.request_reject, name='request-reject'),
    path('requests/<int:pk>/create-order/', views.request_create_order, name='request-create-order'),
    path('requests/<int:pk>/open-conversation/', views.request_open_conversation, name='request-open-conversation'),
    path('orders/', views.order_list, name='order-list'),
    path('orders/<int:pk>/', views.order_detail, name='order-detail'),
    path('orders/<int:pk>/send/', views.order_send, name='order-send'),
    path('orders/<int:pk>/supplier-quote/', views.order_supplier_quote, name='order-supplier-quote'),
    path('orders/<int:pk>/supplier-confirm/', views.order_supplier_confirm, name='order-supplier-confirm'),
    path('orders/<int:pk>/supplier-reject/', views.order_supplier_reject, name='order-supplier-reject'),
    path('orders/<int:pk>/supplier-status/', views.order_supplier_status, name='order-supplier-status'),
    path('orders/<int:pk>/receive/', views.order_receive, name='order-receive'),
    path('stock/', views.stock_dashboard, name='stock-dashboard'),
    path('stock/adjust/', views.stock_adjust, name='stock-adjust'),
    path('conversations/', views.conversation_list, name='conversation-list'),
    path('conversations/<int:pk>/', views.conversation_detail, name='conversation-detail'),
    path('conversations/<int:pk>/reply/', views.conversation_reply, name='conversation-reply'),
    path('admin/', admin.site.urls),

    # Auth JWT
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Apps
    path('api/users/', include('users.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    path('api/products/', include('products.urls')),
    path('api/purchases/', include('purchases.urls')),
    path('api/stock/', include('stock.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
