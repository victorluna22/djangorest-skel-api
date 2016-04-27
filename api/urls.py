from django.conf.urls import patterns, include, url
from django.conf import settings
from rest_framework import routers
from rest_framework_jwt.views import verify_jwt_token
from django.views.static import serve
from account.views.consumer import ConsumerUserViewSet, AddressUserCreateView, user_delete, UserForgotPasswordView, \
    UserChangePasswordView
from account.views.employee import EmployeeViewSet, EmployeeCreateView
from account.views.adm import AdmUserViewSet
from account.views.common import StateViewSet, CityViewSet, AddressViewSet, GetGeoLocation, GetGeoLocationByLatLon
from product.views import ProductViewSet, ProductListCompany, ProductStatusView, ProductRelatedCreateView, ProductImageView
from company.views import CompanyViewSet, AddressCompanyCreateView, ReviewViewSet, CompanyChangeStatusView, \
 CompanyPaymentsView, CompanyEditView, CompanyDashInfoView
from notification.views import FormMessageViewSet, FormCompanyMessageViewSet
from checkout.views import OrderCreateView, OrderCashCreateView, OrderUserListView, OrderViewSet, ProductItemViewSet, \
 OrderCompanyListView, DischargeListView, DischargeCompanyListView, DischargeCreateView, DischargeChangeStatusView, \
 FinanceDataView, OperationsCompanyListView, OrderLastCompanyListView
from account.views.auth import ObtainAuthToken, RefreshAuthToken, home

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users', ConsumerUserViewSet, 'Users')
router.register(r'employees', EmployeeViewSet, 'Pharmacists')
router.register(r'administrators', AdmUserViewSet, 'Administrators')
router.register(r'states', StateViewSet, 'States')
router.register(r'cities', CityViewSet, 'Cities')
router.register(r'products', ProductViewSet, 'Products')
router.register(r'companies', CompanyViewSet, 'Pharmacies')
router.register(r'addresses', AddressViewSet, 'Addresses')
router.register(r'orders', OrderViewSet, 'Orders')
router.register(r'user/contact-us', FormMessageViewSet, 'User-Contact-Us')
router.register(r'company/contact-us', FormCompanyMessageViewSet, 'Company-Contact-Us')
router.register(r'product-items', ProductItemViewSet, 'Product-Items')
router.register(r'rating', ReviewViewSet, 'Rantings')



urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('account.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/login/$', ObtainAuthToken.as_view()),
    url(r'^api/login/lookup/$', RefreshAuthToken.as_view()),
    url(r'^api/token/verify/$', verify_jwt_token),
    url(r'^api/geocoder/location/$', GetGeoLocation.as_view(), name='geocoder_location'),
    url(r'^api/geocoder/location/latlon/$', GetGeoLocationByLatLon.as_view(), name='geocoder_location_latlon'),

    url(r'^api/', include([
        # Quests View
        url(r'^orders/user/$', OrderUserListView.as_view(), name="orders_user"),
        url(r'^orders/company/$', OrderCompanyListView.as_view(), name="orders_company"),
        url(r'^orders/company/last/$', OrderLastCompanyListView.as_view(), name="orders_company"),
        url(r'^orders/create/$', OrderCreateView.as_view(), name='order_create'),
        url(r'^orders/create/cash/$', OrderCashCreateView.as_view(), name='order_create_cash'),
        url(r'^discharges/$', DischargeListView.as_view(), name="discharges_list"),
        url(r'^discharges/company/$', DischargeCompanyListView.as_view(), name="discharges_company"),
        url(r'^discharges/create/$', DischargeCreateView.as_view(), name="discharge_create"),
        url(r'^discharges/change-status/(?P<pk>\d+)/$', DischargeChangeStatusView.as_view(), name="discharge_status"),
        url(r'^checkouts/info/$', FinanceDataView.as_view(), name="finance_data"),
        url(r'^checkouts/billing/$', OperationsCompanyListView.as_view(), name="billing_data"),
        url(r'^products/change-status/(?P<pk>\d+)/$', ProductStatusView.as_view(), name="product_change_status"),
        url(r'^products/change-image/$', ProductImageView.as_view(), name="product_change_image"),
        url(r'^products/related/(?P<pk>\d+)/$', ProductRelatedCreateView.as_view(), name="product_related_create"),
        url(r'^users/forgot-password/$', UserForgotPasswordView.as_view(), name="user_forgot_password"),
        url(r'^users/change-password/$', UserChangePasswordView.as_view(), name="user_change_password"),
        url(r'^users/address/$', AddressUserCreateView.as_view(), name="user_address_create"),
        url(r'^users/email/(?P<email>.+)/$', user_delete, name="user_delete"),
        url(r'^employees/create/$', EmployeeCreateView.as_view(), name="employees_create"),
        url(r'^companies/dashboard/info/$', CompanyDashInfoView.as_view(), name="company_dash_info"),
        url(r'^companies/payment-types/(?P<pk>\d+)/$', CompanyPaymentsView.as_view(), name="company_payments"),
        url(r'^companies/edit/$', CompanyEditView.as_view(), name="company_edit"),
        url(r'^companies/address/$', AddressCompanyCreateView.as_view(), name="company_address_create"),
        url(r'^companies/change-status/(?P<pk>\d+)/$', CompanyChangeStatusView.as_view(), name="company_change_status"),
        url(r'^companies/products/list/$', ProductListCompany.as_view(), name='companies_products'),
        ])),

    url(r'^api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns.append(url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }))
    urlpatterns.append(url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}))