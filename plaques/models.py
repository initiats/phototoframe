from django.db import models
from django.utils.text import slugify

from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # ... your other fields
class Category(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# PRODUCT MODEL

class Product(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    cover_image = models.ImageField(upload_to="products/", null=True, blank=True)

    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)

    shape = models.ForeignKey("PlaqueShape", on_delete=models.SET_NULL, null=True)
    material = models.ForeignKey("Material", on_delete=models.SET_NULL, null=True)
    thickness = models.ForeignKey("Thickness", on_delete=models.SET_NULL, null=True)
    dimension = models.ForeignKey("Dimension", on_delete=models.SET_NULL, null=True)
    fastening = models.ForeignKey("Fastening", on_delete=models.SET_NULL, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Check this line!
    base_image = models.ImageField(upload_to="product_base/", null=True, blank=True)

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# PRODUCT CUSTOMIZATION
class ProductCustomization(models.Model):
    MASK_CHOICES = [
        ('square', 'Square'),
        ('circle', 'Circle'),
        ('heart', 'Heart'),
        ('oval', 'Oval'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shape = models.ManyToManyField("PlaqueShape", blank=True)
    thickness = models.ManyToManyField("Thickness", blank=True)
    material = models.ManyToManyField("Material", blank=True)
    fastening = models.ManyToManyField("Fastening", blank=True)
    dimension = models.ForeignKey("Dimension", on_delete=models.SET_NULL, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    base_image = models.ImageField(upload_to="product_frames/", null=True, blank=True)
    portrait_image = models.ImageField(upload_to="portrait_dummy/", null=True, blank=True)

    # --- ADD THESE TWO FIELDS TO FIX THE TYPEERROR ---
    base_shape = models.CharField(max_length=50, default="")
    mask_shape = models.CharField(max_length=50, default="")

    # Coordinates
    image_x = models.IntegerField(default=0)
    image_y = models.IntegerField(default=0)
    image_w = models.IntegerField(default=0)
    image_h = models.IntegerField(default=0)

    text_x = models.IntegerField(default=0)
    text_y = models.IntegerField(default=0)
    text_w = models.IntegerField(default=0)
    text_h = models.IntegerField(default=0)
    text_value = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.product.title} customization"

# BANNER

class Banner(models.Model):

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    link = models.CharField(max_length=200, blank=True, null=True, default="#")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# MATERIAL

class Material(models.Model):

    name = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# FASTENING

class Fastening(models.Model):

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='fastenings/', blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# STICKER

class Sticker(models.Model):

    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='stickers/')
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# BASE

class Base(models.Model):

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='bases/', blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ORDER

class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Production', 'Production'),
        ('Packaging', 'Packaging'),
        ('Ready for Dispatch', 'Ready for Dispatch'),
        ('Shipped', 'Shipped'),
    )

    order_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    address = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)


# PLAQUE SHAPE

class PlaqueShape(models.Model):

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='shapes/', blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# FEATURES

class Feature(models.Model):

    title = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50)
    description = models.CharField(max_length=255)


# DIMENSION

class Dimension(models.Model):

    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.width}cm × {self.height}cm"


# THICKNESS

class Thickness(models.Model):

    size = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.size


class Collection(models.Model):
    title = models.CharField(max_length=200)
    # Adding null=True here prevents the database from complaining
    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True
    )
    cover_image = models.ImageField(upload_to="collections/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Accessory(models.Model):
        title = models.CharField(max_length=200)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        description = models.TextField(blank=True, null=True)
        # CHANGE 'upload_image' TO 'upload_to'
        cover_image = models.ImageField(upload_to='accessories/')
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.title