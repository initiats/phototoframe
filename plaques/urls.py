from django.urls import path
from . import views

urlpatterns = [
    # --- PUBLIC FRONTEND PAGES ---
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),


    # --- SHOP & PRODUCTS ---
    path('shop/', views.shop, name='shop'),
    path('categories/', views.categories_view, name='categories'),
    path('collections/', views.collections_view, name='collections'),
    path('collections/<int:category_id>/', views.category_products, name='category_detail'),
    path('accessories/', views.accessories_view, name='accessories'),

    # --- CUSTOMIZATION & CONFIGURATOR ---
    path('customize/', views.customize_plaque, name='customize'),
    path('product/<int:pk>/customize/', views.product_customize, name='product_customize'),
    path('product/<int:pk>/customize/save/', views.product_customize_save, name='product_customize_save'),
    path('customization/edit/<int:pk>/', views.customization_edit, name='customization_edit'),
    path('customization/delete/<int:pk>/', views.customization_delete, name='customization_delete'),

    # --- CART & CHECKOUT (Single Set of URLs) ---
    path('cart/', views.cart_page, name='cart_page'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<str:cart_key>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # --- USER ACCOUNT ---
    path('my_account/', views.my_account_view, name='my_account'),


    # --- ADMIN AUTHENTICATION ---
    path('adminlogin/', views.admin_login_view, name='adminlogin'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # --- ADMIN MANAGEMENT: PRODUCTS & BANNERS ---
    path('banner/', views.banner_list, name='banner_list'),
    path('banner/add/', views.banner_add, name='banner_add'),
    path('banner/edit/<int:pk>/', views.banner_edit, name='banner_edit'),
    path('banner/delete/<int:pk>/', views.banner_delete, name='banner_delete'),

    path('product/', views.product_list, name='product_list'),
    path('product/add/', views.product_add, name='product_add'),
    path('product/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('product/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('product/save/', views.product_save, name="product_save"),

    # --- ADMIN MANAGEMENT: ATTRIBUTES ---
    path('admin-categories/', views.category_list, name='category_list'),
    path('admin-categories/save/', views.category_add_edit, name='category_save'),
    path('admin-categories/delete/<int:pk>/', views.category_delete, name='category_delete'),

    path('materials/', views.material_list, name='material_list'),
    path('materials/save/', views.material_save, name='material_save'),
    path('materials/delete/<int:pk>/', views.material_delete, name='material_delete'),

    path('fastenings/', views.fastening_list, name='fastening_list'),
    path('fastenings/save/', views.fastening_save, name='fastening_save'),
    path('fastenings/delete/<int:pk>/', views.fastening_delete, name='fastening_delete'),

    path('shapes/', views.shape_list, name='shape_list'),
    path('shapes/add/', views.shape_add, name='shape_add'),
    path('shapes/edit/<int:pk>/', views.shape_edit, name='shape_edit'),
    path('shapes/delete/<int:pk>/', views.shape_delete, name='shape_delete'),

    path('dimensions/', views.dimension_list, name='dimension_list'),
    path('dimensions/save/', views.dimension_save, name='dimension_save'),
    path('dimensions/delete/<int:pk>/', views.dimension_delete, name='dimension_delete'),

    path('thickness/', views.thickness_list, name='thickness_list'),
    path('thickness/save/', views.thickness_save, name='thickness_save'),
    path('thickness/delete/<int:pk>/', views.thickness_delete, name='thickness_delete'),

    path('base/', views.base_list, name='base_list'),
    path('base/save/', views.base_save, name='base_save'),
    path('base/delete/<int:pk>/', views.base_delete, name='base_delete'),

    path('stickers/', views.sticker_list, name='sticker_list'),
    path('stickers/save/', views.sticker_save, name='sticker_save'),
    path('stickers/delete/<int:pk>/', views.sticker_delete, name='sticker_delete'),

    # --- ADMIN MANAGEMENT: ORDERS & COLLECTIONS ---
    path('orders/', views.order_list, name='order_list'),
    path('orders/update/<int:pk>/', views.order_status_update, name='order_status_update'),

    path('collection/', views.collection_list, name='collection_list'),
    path('collection/add/', views.collection_add, name='collection_add'),
    path('collection/edit/<int:pk>/', views.collection_edit, name='collection_edit'),
    path('collection/delete/<int:pk>/', views.collection_delete, name='collection_delete'),

    path('accessories/admin/', views.accessory_list, name='accessory_list'),
    path('accessory/add/', views.accessory_add, name='accessory_add'),
    path('accessory/edit/<int:pk>/', views.accessory_edit, name='accessory_edit'),
    path('accessory/delete/<int:pk>/', views.accessory_delete, name='accessory_delete'),



]