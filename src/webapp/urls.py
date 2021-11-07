from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('orderplaced/',views.orderplaced),
    path('vendor/',views.vendor,name='vendor'),
    path('register/user/',views.customerRegister,name='register'),
    path('login/user/',views.customerLogin,name='login'),
    path('login/vendor/',views.vendorLogin,name='rlogin'),
    path('register/vendor/',views.vendorRegister,name='rregister'),
    path('profile/vendor/',views.vendorProfile,name='rprofile'),
    path('profile/user/',views.customerProfile,name='profile'),
    path('user/create/',views.createCustomer,name='ccreate'),
    path('user/update/<int:id>/',views.updateCustomer,name='cupdate'),
    path('vendor/create/',views.createVendor,name='rcreate'),
    path('vendor/update/<int:id>/',views.updateVendor,name='rupdate'),
    path('vendor/orderlist/',views.orderlist,name='orderlist'),
    path('vendor/menu/',views.menuManipulation,name='mmenu'),
    path('logout/',views.Logout,name='logout'),
    path('vendor/<int:pk>/',views.vendorMenu,name='menu'),
    path('checkout/',views.checkout,name='checkout'),
    path('orders/',views.orders,name='orders'),

]