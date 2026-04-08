
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

# Make sure the names here match the classes in models.py
# If your import looks like this:
from .models import Order

import json
import uuid
from django.db.models import Q  # Useful if you add search later

def index(request):
    # 1. Fetch Banners
    banners = Banner.objects.all()

    # 2. Fetch Categories and their related products (Optimized)
    categories = Category.objects.prefetch_related('product_set').all()

    # 3. Fetch all products (if you need them globally)
    products = Product.objects.select_related('category').prefetch_related(
        'productcustomization_set'
    ).all()

    # 4. Return everything in ONE dictionary
    return render(request, "index.html", {
        "banners": banners,
        "categories": categories,
        "products": products
    })
# def accessories_view(request):
#     # This is the function that fetches the data for the frontend
#     accessories_data = Accessory.objects.all().order_by('-created_at')
#     return render(request, 'accessories.html', {'accessories': accessories_data})

def category_detail(request, slug):
    # View to show products inside a specific category
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'shop.html', {
        'category': category,
        'products': products
    })

# Import your model at the top


# 1. Make sure you import your model at the top


def shop(request):
    product_id = request.GET.get("product")

    if not product_id:
        return redirect('index')

    product = get_object_or_404(Product, id=product_id)

    # Fetch customizations and prefetch related attributes for performance
    customizations = ProductCustomization.objects.filter(product=product).prefetch_related(
        "shape", "thickness", "material", "fastening", "dimension"
    )

    configs = []
    allowed_shape_ids = set()
    allowed_thickness_ids = set()
    allowed_material_ids = set()
    allowed_fastening_ids = set()

    for c in customizations:
        if not c.base_image or not c.dimension:
            continue

        # Collect IDs for the sidebar selectors
        for s in c.shape.all(): allowed_shape_ids.add(s.id)
        for t in c.thickness.all(): allowed_thickness_ids.add(t.id)
        for m in c.material.all(): allowed_material_ids.add(m.id)
        for f in c.fastening.all(): allowed_fastening_ids.add(f.id)

        configs.append({
            "id": c.id,
            "shapes": [s.id for s in c.shape.all()],
            "base_image": c.base_image.url,
            "portrait_sample": c.portrait_image.url if c.portrait_image else "",
            "dimension": {
                "id": c.dimension.id,
                "w": float(c.dimension.width),
                "h": float(c.dimension.height),
                "label": f"{c.dimension.width} x {c.dimension.height}"
            },
            "thickness": [{"id": t.id, "name": t.size} for t in c.thickness.all()],
            "materials": [{"id": m.id, "name": m.name} for m in c.material.all()],
            "fastenings": [{"id": f.id, "name": f.name} for f in c.fastening.all()],
            "price": float(c.price or 0),
            "image": {
                "x": float(c.image_x or 0),
                "y": float(c.image_y or 0),
                "w": float(c.image_w or 150),
                "h": float(c.image_h or 200),
            },
            "texts": [
                {
                    "x": float(c.text_x or 0),
                    "y": float(c.text_y or 0),
                    "w": float(c.text_w or 100),
                    "h": float(c.text_h or 40),
                    "value": c.text_value or ""
                }
            ] if c.text_value else []
        })

    # Fetch the actual objects for the template loops
    product_shapes = PlaqueShape.objects.filter(id__in=allowed_shape_ids, status=True)
    product_thickness = Thickness.objects.filter(id__in=allowed_thickness_ids, status=True)
    product_materials = Material.objects.filter(id__in=allowed_material_ids, status=True)
    product_fastenings = Fastening.objects.filter(id__in=allowed_fastening_ids, status=True)

    return render(request, "shop.html", {
        "product": product,
        "shape": product_shapes,
        "thickness": product_thickness,    # Now passed to template
        "materials": product_materials,    # Now passed to template
        "fastenings": product_fastenings,  # Now passed to template
        "config_json": json.dumps(configs),
    })

def about(request): return render(request, 'about.html')
def contact(request): return render(request, 'contact.html')
def customization(request): return render(request, 'customize.html')
def account(request): return render(request, 'account.html')
def cart(request): return render(request, 'cart.html')
def checkout(request): return render(request, 'checkout.html')
def faq(request): return render(request, 'faq.html')
def privacy(request): return render(request, 'privacy.html')
def terms(request): return render(request, 'terms.html')
def refund(request): return render(request, 'refund.html')

def admin_login_view(request):
    """
    Handles administrator authentication for Photoglass.
    Redirects to http://127.0.0.1:8000/dashboard/ on success.
    """
    # 1. Redirect if already logged in as admin
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    if request.method == "POST":
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')

        # 2. Authenticate against Django's user database
        user = authenticate(request, username=user_name, password=pass_word)

        # 3. Security Check: Must be an admin/staff/superuser
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                # Success: Goes to your dashboard URL
                return redirect('dashboard')
            else:
                # User exists but is a regular customer, not an admin
                messages.error(request, "Access Denied: You do not have administrative privileges.")
        else:
            # Wrong username or password
            messages.error(request, "Invalid administrator credentials.")

    return render(request, 'admin_login.html')


def dashboard(request):
    # This counts the actual number of rows in your Product table
    total_products = Product.objects.count()

    # Existing counts
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'products_count': total_products,  # This matches the HTML variable
    }

    return render(request, 'dashboard.html', context)
def dashboard_view(request):
    context = {
        'categories_count': 0,
        'materials_count': 0,
        'dimensions_count': 0,
        'bases_count': 0,
    }
    return render(request, 'admin_dashboard.html', context)

# API endpoint to handle additions/subtractions via AJAX
def update_attribute(request):
    if request.method == "POST":
        attr_type = request.POST.get('type')
        action = request.POST.get('action')
        # Here you would add code to save to your database
        return JsonResponse({'status': 'success'})

def logout_view(request):
    """
    Logs out the admin and returns to the login page.
    """
    logout(request)
    return redirect('adminlogin')


from .models import Banner


def banner_list(request):
    """
    Displays the banner management dashboard.
    Matches: path('banner/', views.banner_list, name='banner_list')
    """
    banners = Banner.objects.all().order_by('-id')
    return render(request, 'banner_management.html', {'banners': banners})


def banner_add(request):
    """
    Handles adding a new banner via POST.
    Matches: path('banner/add/', views.banner_add, name='banner_add')
    """
    if request.method == "POST":
        title = request.POST.get('title')
        link = request.POST.get('link')
        image = request.FILES.get('image')

        if title and image:
            Banner.objects.create(
                title=title,
                link=link,
                image=image
            )
            messages.success(request, "Banner added successfully!")
        else:
            messages.error(request, "Title and Image are required.")

    return redirect('banner_list')


def banner_edit(request, pk):
    """
    Updates an existing banner.
    Matches: path('banner/edit/<int:pk>/', views.banner_edit, name='banner_edit')
    """
    banner = get_object_or_404(Banner, pk=pk)

    if request.method == "POST":
        banner.title = request.POST.get('title')
        banner.link = request.POST.get('link')

        # Update image only if a new file is uploaded
        new_image = request.FILES.get('image')
        if new_image:
            banner.image = new_image

        banner.save()
        messages.success(request, "Banner updated successfully!")

    return redirect('banner_list')


def banner_delete(request, pk):
    """
    Deletes a specific banner.
    Matches: path('banner/delete/<int:pk>/', views.banner_delete, name='banner_delete')
    """
    banner = get_object_or_404(Banner, pk=pk)
    banner.delete()
    messages.success(request, "Banner deleted successfully!")
    return redirect('banner_list')




def product_list(request):

    products = Product.objects.all().order_by("-id")

    context = {
        "products": products,
        "category": Category.objects.all(),
        "shape": PlaqueShape.objects.all(),
        "thickness": Thickness.objects.all(),
        "dimensions": Dimension.objects.all(),
        "materials": Material.objects.all(),
        "fastenings": Fastening.objects.all(),
    }

    return render(request, "admin_product.html", context)


def product_add(request):

    if request.method == "POST":

        product = Product.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            cover_image=request.FILES.get("cover_image"),
            shape_id=request.POST.get("shape"),
            material_id=request.POST.get("material"),
            thickness_id=request.POST.get("thickness"),
            dimension_id=request.POST.get("dimension"),
            fastening_id=request.POST.get("fastening"),
            price=request.POST.get("price"),
            base_image=request.FILES.get("base_image"),
            is_featured='is_featured' in request.POST
        )

        # multiple categories
        product.category_id = request.POST.get("category")
        product.save()

        # customization sets
        ix = request.POST.getlist("ix[]")
        iy = request.POST.getlist("iy[]")
        iw = request.POST.getlist("iw[]")
        ih = request.POST.getlist("ih[]")

        tx = request.POST.getlist("tx[]")
        ty = request.POST.getlist("ty[]")
        tw = request.POST.getlist("tw[]")
        th = request.POST.getlist("th[]")

        texts = request.POST.getlist("custom_text[]")

        for i in range(len(texts)):

            ProductCustomization.objects.create(
                product=product,
                image_x=ix[i],
                image_y=iy[i],
                image_w=iw[i],
                image_h=ih[i],
                text_x=tx[i],
                text_y=ty[i],
                text_w=tw[i],
                text_h=th[i],
                text_value=texts[i]
            )

        return redirect("product_list")

from .models import Category


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.category_id = request.POST.get('category')
        product.title = request.POST.get('title')
        product.description = request.POST.get('description')
        product.base_price = request.POST.get('base_price')
        product.customization_allowed = 'customization_allowed' in request.POST
        product.is_featured = 'is_featured' in request.POST

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()

        # Update Customization Sets
        if product.customization_allowed:
            # Clear old sets first
            ProductCustomization.objects.filter(product=product).delete()

            # Get lists from form
            materials = request.POST.getlist('material[]')
            prices = request.POST.getlist('price[]')
            ix = request.POST.getlist('ix[]')
            iy = request.POST.getlist('iy[]')
            iw = request.POST.getlist('iw[]')
            ih = request.POST.getlist('ih[]')

            for i in range(len(materials)):
                if materials[i]: # Only save if material is chosen
                    ProductCustomization.objects.create(
                        product=product,
                        material=materials[i],
                        price=prices[i] if prices[i] else 0,
                        img_pos_x=ix[i] if ix[i] else 0,
                        img_pos_y=iy[i] if iy[i] else 0,
                        img_width=iw[i] if iw[i] else 0,
                        img_height=ih[i] if ih[i] else 0
                    )

        messages.success(request, "Product updated successfully!")
        return redirect('product_list')
    return redirect('product_list')


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect('product_list')



# def category_list(request):
#     categories = Category.objects.all().order_by('-id')
#     return render(request, 'admin_category_list.html', {'categories': categories})

def category_add_edit(request):
    if request.method == "POST":
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        status = 'status' in request.POST

        if category_id:
            category = get_object_or_404(Category, id=category_id)
            category.name = name
            category.status = status
            category.save()
        else:
            Category.objects.create(
                name=name,
                status=status
            )

    return redirect('category_list')

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted.")
    return redirect('category_list')




def material_list(request):
    materials = Material.objects.all().order_by('name')
    return render(request, 'admin_materials.html', {'materials': materials})

def material_save(request):
    if request.method == "POST":
        material_id = request.POST.get('material_id')
        name = request.POST.get('name')
        status = request.POST.get('status') == 'active'

        if material_id:  # Edit existing
            material = get_object_or_404(Material, id=material_id)
            material.name = name
            material.status = status
            material.save()
            messages.success(request, "Material updated successfully!")
        else:  # Add new
            Material.objects.create(name=name, status=status)
            messages.success(request, "Material created successfully!")

    return redirect('material_list')

def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    material.delete()
    messages.success(request, "Material deleted.")
    return redirect('material_list')


def fastening_list(request):
    fastenings = Fastening.objects.all().order_by('-id')
    return render(request, 'admin_fastenings.html', {'fastenings': fastenings})

def fastening_save(request):
    if request.method == "POST":
        fastening_id = request.POST.get('fastening_id')
        name = request.POST.get('name')
        image = request.FILES.get('image')
        status = request.POST.get('status') == 'active'

        if fastening_id:
            fastening = get_object_or_404(Fastening, id=fastening_id)
            fastening.name = name
            fastening.status = status
            if image:
                fastening.image = image
            fastening.save()
        else:
            # Removed 'price=price' from here
            Fastening.objects.create(name=name, image=image, status=status)

    return redirect('fastening_list')
def fastening_delete(request, pk):
    item = get_object_or_404(Fastening, pk=pk)
    item.delete()
    messages.success(request, "Fastening item removed.")
    return redirect('fastening_list')


from .models import Sticker


def sticker_list(request):
    stickers = Sticker.objects.all().order_by('-id')
    return render(request, 'admin_stickers.html', {'stickers': stickers})

def sticker_save(request):
    if request.method == "POST":
        sticker_id = request.POST.get('sticker_id')
        name = request.POST.get('name')
        image = request.FILES.get('image')
        status = request.POST.get('status') == 'active'

        if sticker_id:  # Edit existing
            item = get_object_or_404(Sticker, id=sticker_id)
            item.name = name
            item.status = status
            if image:
                item.image = image
            item.save()
            messages.success(request, "Sticker updated successfully!")
        else:  # Add new
            Sticker.objects.create(name=name, image=image, status=status)
            messages.success(request, "New sticker added!")

    return redirect('sticker_list')

def sticker_delete(request, pk):
    item = get_object_or_404(Sticker, pk=pk)
    item.delete()
    messages.success(request, "Sticker removed.")
    return redirect('sticker_list')



def order_list(request):
    """Lists all orders in the dashboard."""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_orders.html', {'orders': orders})

def order_status_update(request, pk):
    """Updates the order status and redirects back."""
    if request.method == "POST":
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.order_number} moved to {new_status}")
    return redirect('order_list')



import json



def customize_plaque(request):
    shapes = PlaqueShape.objects.all()
    # Build a dictionary of { "ShapeName": "/media/url.png" }
    shape_data = {shape.name: shape.image.url for shape in shapes}

    return render(request, 'customize.html', {
        'shape_data_json': json.dumps(shape_data)
    })
from .models import Category # Make sure to import your model

def about(request):
    # Fetch categories so the header dropdown has items
    categories = Category.objects.all()
    return render(request, 'about.html', {'categories': categories})


from .models import Category  # Ensure this is at the top of your file


def contact(request):
    # Fetch all categories so the header dropdown works
    categories = Category.objects.all()

    # If you have a contact form, you would handle it here
    return render(request, 'contact.html', {'categories': categories})

def categories_view(request):
    return render(request, 'categories.html')


from .models import Base
def base_list(request):
    # Fetch data using the Model class
    bases = Base.objects.all()
    # Ensure this matches the file name in your templates folder
    return render(request, 'admin_base_list.html', {'bases': bases})

def base_save(request):
    if request.method == "POST":
        base_id = request.POST.get('base_id')
        name = request.POST.get('name')
        status = True if request.POST.get('status') == 'active' else False
        image = request.FILES.get('image')

        if base_id:  # Edit existing record
            # Fix: Use the Model class 'Base'
            item = get_object_or_404(Base, id=base_id)
            item.name = name
            item.status = status
            if image:
                item.image = image
            item.save()
        else:  # Create new record
            # Fix: Use the Model class 'Base'
            Base.objects.create(name=name, image=image, status=status)

    return redirect('base_list')

def base_delete(request, pk):
    # Fix: Use the Model class 'Base'
    item = get_object_or_404(Base, pk=pk)
    item.delete()
    return redirect('base_list')


from .models import Dimension

# Finalized list view
def dimension_list(request):
    dimensions = Dimension.objects.all().order_by('width')
    return render(request, 'dimensions_list.html', {'dimensions': dimensions})


def dimension_save(request):
    if request.method == "POST":
        dim_id = request.POST.get('dim_id')
        width = request.POST.get('width')
        height = request.POST.get('height')
        status = request.POST.get('status') == 'active'

        if dim_id:
            item = get_object_or_404(Dimension, id=dim_id)
            item.width = width
            item.height = height
            item.status = status
            item.save()
        else:
            Dimension.objects.create(
                width=width,
                height=height,
                status=status
            )

    return redirect('dimension_list')



def dimension_delete(request, pk):
    item = get_object_or_404(Dimension, pk=pk)
    item.delete()
    messages.success(request, "Dimension removed.")
    return redirect('dimension_list')

def category_list(request):
    categories = Category.objects.all()
    # Change 'categories' to 'category'
    return render(request, 'category_management.html', {'category': categories})


def category_add_edit(request):
    if request.method == "POST":
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        image = request.FILES.get('image')

        # Check if 'status' exists in POST; if not, it's False (unchecked)
        status = 'status' in request.POST

        if category_id:  # Edit existing
            category = get_object_or_404(Category, id=category_id)
            category.name = name
            category.status = status  # Update the status
            if image:
                category.image = image
            category.save()
        else:  # Add new
            Category.objects.create(
                name=name,
                image=image,
                status=status  # Save the status
            )

        return redirect('category_list')
    return None
    return None
    return None
    return None


# 3. Delete Logic
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('category_list')


def shape_list(request):
    # Fetch data
    shapes_data = PlaqueShape.objects.all().order_by('-id')
    # Use the key 'shape' to match your {% for s in shape %} loop
    return render(request, 'admin_shape.html', {'shape': shapes_data})


def shape_add(request):
    if request.method == "POST":
        name = request.POST.get('name')
        image = request.FILES.get('image')
        status = 'status' in request.POST

        if name and image:
            PlaqueShape.objects.create(
                name=name,
                image=image,
                status=status
            )
            messages.success(request, "Shape added successfully!")

    return redirect('shape_list')

def shape_edit(request, pk):
    shape = get_object_or_404(PlaqueShape, pk=pk)

    if request.method == "POST":
        shape.name = request.POST.get('name')
        shape.status = 'status' in request.POST

        if request.FILES.get('image'):
            shape.image = request.FILES.get('image')

        shape.save()
        messages.success(request, "Shape updated!")

    return redirect('shape_list')

def shape_delete(request, pk):
    shape = get_object_or_404(PlaqueShape, pk=pk)
    shape.delete()
    messages.success(request, "Shape deleted successfully.")
    return redirect('shape_list')


def thickness_list(request):
    thickness = Thickness.objects.all().order_by('-id')
    return render(request, 'admin_thickness.html', {'thickness': thickness})


def thickness_save(request):
    if request.method == "POST":
        thickness_id = request.POST.get('thickness_id')
        size = request.POST.get('size')
        status = request.POST.get('status') == 'active'

        if thickness_id:
            item = get_object_or_404(Thickness, id=thickness_id)
            item.size = size
            item.status = status
            item.save()
        else:
            Thickness.objects.create(
                size=size,
                status=status
            )

    return redirect('thickness_list')


def thickness_delete(request, pk):
    item = get_object_or_404(Thickness, pk=pk)
    item.delete()
    return redirect('thickness_list')


def product_save(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        cover_image = request.FILES.get("cover_image")

        # Capture the price from the form
        price_val = request.POST.get('price', 0)

        # --------------------------------
        # EDIT PRODUCT
        # --------------------------------
        if product_id:
            product = Product.objects.get(id=product_id)
            product.title = title
            product.description = description
            product.price = price_val  # FIXED: Assigning the price here
            product.category_id = category if category else None

            if cover_image:
                product.cover_image = cover_image

            product.save()
            return redirect("product_list")

        # --------------------------------
        # ADD NEW PRODUCT
        # --------------------------------
        product = Product.objects.create(
            title=title,
            description=description,
            price=price_val,  # FIXED: Adding price to create
            category_id=category if category else None,
            cover_image=cover_image
        )

        # --------------------------------
        # SAVE CUSTOMIZATION BLOCKS (Optional Logic below)
        # --------------------------------
        if 'is_customizable' in request.POST:
            idx = 0
            while True:
                shape_id = request.POST.get(f"shape_{idx}")
                if shape_id is None:
                    break

                thickness_id = request.POST.get(f"thickness_{idx}")
                dimension_id = request.POST.get(f"dimension_{idx}")
                cust_price = request.POST.get(f"price_{idx}", 0)
                base_image = request.FILES.get(f"base_image_{idx}")
                # ... [Rest of your customization logic remains unchanged] ...
                idx += 1

        return redirect("product_list")


from .models import Product, PlaqueShape, Thickness, Material, Fastening


def product_customize(request, pk):
    """
    This view loads the main page. 
    It must provide the list of all available shapes to the modal.
    """
    product = get_object_or_404(Product, pk=pk)

    context = {
        "product": product,
        # Ensure this key is 'shapes' to match your template loop
        "shapes": PlaqueShape.objects.filter(status=True), 
        "dimensions": Dimension.objects.all(),
        "thickness": Thickness.objects.filter(status=True),
        "materials": Material.objects.filter(status=True),
        "fastenings": Fastening.objects.filter(status=True),
    }

    return render(request, "product_customize.html", context)



def product_customize_save(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        # 1. Create the main record
        custom = ProductCustomization.objects.create(
            product=product,
            dimension_id=request.POST.get("dimension"),
            price=request.POST.get("price") or 0,
            image_x=request.POST.get("ix") or 0,
            image_y=request.POST.get("iy") or 0,
            image_w=request.POST.get("iw") or 0,
            image_h=request.POST.get("ih") or 0,
            text_value=request.POST.get("custom_text[]") or "",
            text_x=request.POST.get("tx[]") or 0,
            text_y=request.POST.get("ty[]") or 0,
            text_w=request.POST.get("tw[]") or 0,
            text_h=request.POST.get("th[]") or 0,
            base_image=request.FILES.get("base_image"),
            portrait_image=request.FILES.get("portrait_image")
        )

        # 2. Save the Multiple Selections (Checkboxes)
        custom.shape.set(request.POST.getlist("shapes[]"))
        custom.thickness.set(request.POST.getlist("thickness[]"))
        custom.material.set(request.POST.getlist("materials[]"))
        custom.fastening.set(request.POST.getlist("fastenings[]"))

        messages.success(request, "Configuration created successfully!")
        return redirect("product_customize", pk=pk)


from .models import ProductCustomization


def customization_delete(request, pk):
    custom = get_object_or_404(ProductCustomization, pk=pk)
    product_id = custom.product.id
    custom.delete()
    messages.warning(request, "Configuration removed.")
    return redirect("product_customize", pk=product_id)




def customization_edit(request, pk):
    custom = get_object_or_404(ProductCustomization, pk=pk)
    product = custom.product

    if request.method == "POST":
        # Update basic fields
        custom.dimension_id = request.POST.get("dimension")
        custom.price = request.POST.get("price") or 0
        custom.image_x = request.POST.get("ix") or 0
        custom.image_y = request.POST.get("iy") or 0
        custom.image_w = request.POST.get("iw") or 0
        custom.image_h = request.POST.get("ih") or 0

        # Update Text Zone (First one)
        texts = request.POST.getlist("custom_text[]")
        if texts:
            custom.text_value = texts[0]
            custom.text_x = request.POST.getlist("tx[]")[0] or 0
            custom.text_y = request.POST.getlist("ty[]")[0] or 0
            custom.text_w = request.POST.getlist("tw[]")[0] or 0
            custom.text_h = request.POST.getlist("th[]")[0] or 0

        # Update Images only if new ones are uploaded
        if request.FILES.get("base_image"):
            custom.base_image = request.FILES.get("base_image")
        if request.FILES.get("portrait_image"):
            custom.portrait_image = request.FILES.get("portrait_image")

        custom.save()

        # Update Many-to-Many Checkboxes
        custom.shape.set(request.POST.getlist("shapes[]"))
        custom.thickness.set(request.POST.getlist("thickness[]"))
        custom.material.set(request.POST.getlist("materials[]"))
        custom.fastening.set(request.POST.getlist("fastenings[]"))

        messages.success(request, "Configuration updated!")
        return redirect("product_customize", pk=product.id)

    # For the GET request, we send all data to the template
    context = {
        "product": product,
        "edit_custom": custom,
        "shapes": PlaqueShape.objects.all(),
        "dimensions": Dimension.objects.all(),
        "thickness": Thickness.objects.all(),
        "materials": Material.objects.all(),
        "fastenings": Fastening.objects.all(),
    }
    return render(request, "product_customize.html", context)


import json

from .models import Product

from .models import Collection, Product  # Ensure Collection is imported

import uuid  # Add this import at the top


import json
import uuid

from .models import Product, Category, Order

# --- 1. ADD TO CART (Configurator Logic) ---
import uuid
import json

from .models import Product

import uuid
import json
 # Optional: only if you have CSRF issues

import uuid
import json


def add_to_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not isinstance(cart, dict):
            cart = {}

        # --- Case A: Request comes from the Configurator (JSON) ---
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                product_id = data.get('product_id')
                product = get_object_or_404(Product, id=product_id)

                cart_key = f"custom_{product_id}_{uuid.uuid4().hex[:6]}"
                cart[cart_key] = {
                    'cart_key': cart_key,
                    'product_id': product_id,
                    'product_name': product.title,
                    'price': float(data.get('price', 0)),
                    'custom_image': data.get('custom_image_base64'),
                    'quantity': 1,
                    'shape': data.get('shape', 'Standard'),
                    'dimension': data.get('dimension', 'Standard'),
                    'text': data.get('text', 'None'),
                }
                request.session['cart'] = cart
                request.session.modified = True
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        # --- Case B: Request comes from Collections Page (Standard Form POST) ---
        else:
            product_id = request.POST.get('product_id')
            # Check if it's a Collection item or a Product item
            # We try to get it from Collection model first
            try:
                item = Collection.objects.get(id=product_id)
                name = item.title
                price = float(item.price)
                image = item.cover_image.url if item.cover_image else ""
            except Collection.DoesNotExist:
                item = get_object_or_404(Product, id=product_id)
                name = item.title
                price = float(item.price)
                image = item.cover_image.url if item.cover_image else ""

            # Standard items use the product_id as key so they don't duplicate unnecessarily
            cart_key = f"std_{product_id}"

            if cart_key in cart:
                cart[cart_key]['quantity'] += 1
            else:
                cart[cart_key] = {
                    'cart_key': cart_key,
                    'product_id': product_id,
                    'product_name': name,
                    'price': price,
                    'custom_image': image,
                    'quantity': 1,
                    'shape': 'Standard',
                    'dimension': 'Standard',
                    'text': 'None',
                }

            request.session['cart'] = cart
            request.session.modified = True
            return redirect('cart_page')  # Redirect to cart page after clicking Buy Now

    return JsonResponse({'status': 'error', 'message': 'Invalid Request'}, status=405)

def update_cart_quantity(request):
    """Updates quantity of a specific item in the cart via AJAX"""
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            cart_key = data.get('index')  # This matches the 'index' key sent in JS
            new_qty = int(data.get('quantity'))

            cart = request.session.get('cart', {})

            if cart_key in cart and new_qty > 0:
                cart[cart_key]['quantity'] = new_qty
                request.session['cart'] = cart
                request.session.modified = True
                return JsonResponse({'status': 'success'})

            return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'fail'}, status=400)

def remove_from_cart(request, cart_key):
    cart = request.session.get('cart', {})
    if cart_key in cart:
        del cart[cart_key]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart_page')


def categories_view(request):
    # Fetch all categories to display on the page
    categories = Category.objects.prefetch_related('product_set').all()

    # Get the specific category ID from the URL if it exists (e.g., ?id=10)
    target_category_id = request.GET.get('id')

    return render(request, 'categories.html', {
        'categories': categories,
        'target_id': target_category_id  # Pass this to the template
    })


def checkout(request):
    cart = request.session.get('cart', {})

    # Use .values() to treat the dictionary like a list for the template
    cart_items = list(cart.values())
    total_price = sum(float(item['price']) * int(item.get('quantity', 1)) for item in cart_items)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


def account_view(request):
    # 1. Get the cart from the session (default to empty dictionary)
    cart_dict = request.session.get('cart', {})

    # 2. Convert dictionary values to a list for the HTML loop
    cart_items = list(cart_dict.values())

    # 3. Calculate Total Price carefully
    total_price = sum(float(item['price']) * int(item.get('quantity', 1)) for item in cart_items)

    # 5. Send everything to the template
    return render(request, 'account.html', {
        'total_price': total_price,
        'cart_items': cart_items,

    })

def my_account_view(request):
    if request.user.is_authenticated:
        email = request.user.email
    else:
        email = "Guest"
    
    return render(request, 'my_account.html', {'email': email})

from .models import Category, Collection


def collections_view(request):
    categories = Category.objects.all()

    # Get the price filter from the URL (e.g., ?price=1000)
    max_price = request.GET.get('price')

    if max_price:
        # Filter collections where price is less than or equal to max_price
        collections = Collection.objects.filter(price__lte=max_price).order_by('-created_at')
    else:
        collections = Collection.objects.all().order_by('-created_at')

    context = {
        'categories': categories,
        'collections': collections,
        'current_price': max_price, # Send this back to keep the filter selected
    }

    return render(request, 'collections.html', context)

# View for Products within a specific category
def category_products(path, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(path, 'category_products.html', {'category': category, 'products': products})

from .models import Collection

# --- ADMIN VIEW: List All Collections ---
def collection_list(request):
    # Fetching all collections ordered by newest first
    all_collections = Collection.objects.all().order_by('-created_at')
    # Key 'collections' must match your {% for col in collections %} in HTML
    return render(request, 'admin_collection.html', {'collections': all_collections})

# --- ADMIN ACTION: Add New Collection ---
def collection_add(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        cover_image = request.FILES.get('cover_image')

        if title and cover_image:
            # Handle empty price input to prevent Decimal errors
            valid_price = price if price and price.strip() != "" else 0.00

            Collection.objects.create(
                title=title,
                description=description,
                price=valid_price,
                cover_image=cover_image
            )
        return redirect('collection_list')
    return redirect('collection_list')

# --- ADMIN ACTION: Edit Existing Collection ---
def collection_edit(request, pk):
    collection_item = get_object_or_404(Collection, pk=pk)

    if request.method == "POST":
        # Update text fields
        collection_item.title = request.POST.get('title')
        collection_item.description = request.POST.get('description')

        # Handle price update safely
        new_price = request.POST.get('price')
        collection_item.price = new_price if new_price and new_price.strip() != "" else 0.00

        # Update image ONLY if a new file was uploaded
        new_image = request.FILES.get('cover_image')
        if new_image:
            collection_item.cover_image = new_image

        collection_item.save()
        return redirect('collection_list')

    return redirect('collection_list')

# --- ADMIN ACTION: Delete Collection ---
def collection_delete(request, pk):
    collection_item = get_object_or_404(Collection, pk=pk)
    collection_item.delete()
    return redirect('collection_list')


def cart_page(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    if isinstance(cart, dict):
        for key, item in cart.items():
            # Ensure price and quantity are numbers
            price = float(item.get('price', 0))
            qty = int(item.get('quantity', 1))
            total_price += (price * qty)
            cart_items.append(item)

    # Fetch categories so the header dropdown still works on the cart page
    categories = Category.objects.all()

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'categories': categories
    })

from .models import Accessory


def accessory_list(request):
    accessories = Accessory.objects.all().order_by('-created_at')
    return render(request, 'admin_accessory.html', {'accessories': accessories})


def accessory_add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        description = request.POST.get('description')
        cover_image = request.FILES.get('cover_image')

        Accessory.objects.create(
            title=title,
            price=price,
            description=description,
            cover_image=cover_image
        )
        return redirect('accessory_list')
    return redirect('accessory_list')


def accessory_edit(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    if request.method == 'POST':
        accessory.title = request.POST.get('title')
        accessory.price = request.POST.get('price')
        accessory.description = request.POST.get('description')

        if request.FILES.get('cover_image'):
            accessory.cover_image = request.FILES.get('cover_image')

        accessory.save()
        return redirect('accessory_list')
    return redirect('accessory_list')


def accessory_delete(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    accessory.delete()
    return redirect('accessory_list')


from .models import Accessory


# def accessories_view(request):
#     # 1. Fetch data from the Accessory model
#     accessories_list = Accessory.objects.all().order_by('-created_at')
#
#     # 2. Pass it to the template under the name 'accessories'
#     # This MUST match the {% for acc in accessories %} in your HTML
#     return render(request, 'accessories.html', {
#         'accessories': accessories_list
#     })

# In your views.py
def accessories_view(request):
    # 1. Fetch all accessories from the database
    accessories_list = Accessory.objects.all().order_by('-created_at')

    # 2. Fetch categories for the header dropdown (so the menu works)
    categories = Category.objects.all()

    # 3. Return the data to the template
    return render(request, 'accessories.html', {
        'accessories': accessories_list,
        'categories': categories
    })



