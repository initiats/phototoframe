from django.contrib import admin
from .models import (
    Category, Product, ProductCustomization, Banner,
    Material, Fastening,  Order,
    PlaqueShape,  Dimension, Thickness,
    Collection, Accessory
)

# --- CUSTOM DISPLAYS FOR BETTER VISIBILITY ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('status',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'description')

@admin.register(ProductCustomization)
class ProductCustomizationAdmin(admin.ModelAdmin):
    list_display = ('product', 'dimension', 'price', 'base_shape')
    # filter_horizontal = ('shape', 'thickness', 'material', 'fastening') # Better UI for ManyToMany

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'full_name', 'email', 'mobile')
    readonly_fields = ('created_at',)

@admin.register(Dimension)
class DimensionAdmin(admin.ModelAdmin):
    list_display = ('width', 'height', 'status')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'active')

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'created_at')

@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'created_at')

# --- SIMPLE REGISTRATIONS FOR ATTRIBUTE MODELS ---

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')

@admin.register(Fastening)
class FasteningAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')


@admin.register(PlaqueShape)
class PlaqueShapeAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')

@admin.register(Thickness)
class ThicknessAdmin(admin.ModelAdmin):
    list_display = ('size', 'status')

list_display = ('id', 'price', 'some_field', 'base_shape', ...)