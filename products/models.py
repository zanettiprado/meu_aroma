from django.conf import settings
from django.db import models

class Category(models.Model):
    """
    Model representing a product category.

    Attributes:
        name (str): The name of the category.
        description (str, optional): A description of the category (optional).

    Meta:
        verbose_name (str): The singular name for the category in the admin interface.
        verbose_name_plural (str): The plural name for the category in the admin interface.

    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    

class Product(models.Model):
    """
    Model representing a product.

    Attributes:
        category (Category): The category to which the product belongs.
        name (str): The name of the product.
        description (str): A description of the product.
        price (Decimal): The price of the product.
        image (ImageField): An image of the product.

    Methods:
        __str__(): Returns a string representation of the product.

    """
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.name


class Inventory(models.Model):
    """
    Model representing inventory for a product.

    Attributes:
        product (Product): The product associated with the inventory.
        quantity_in_stock (int): The quantity of the product in stock.
        quantity_allocated (int): The quantity of the product allocated for purchase.

    Methods:
        allocate_stock(quantity): Allocates stock for a purchase, reducing quantity_in_stock.
        deallocate_stock(quantity): Deallocates stock that is no longer needed.
        restock(quantity): Adds stock to quantity_in_stock.
        __str__(): Returns a string representation of the inventory.

    """
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity_in_stock = models.PositiveIntegerField(default=0)
    quantity_allocated = models.PositiveIntegerField(default=0)

    def allocate_stock(self, quantity):
        """
        Allocates stock for a purchase, reducing the quantity_in_stock.
        """
        if self.quantity_in_stock >= quantity:
            self.quantity_in_stock -= quantity
            self.quantity_allocated += quantity
            self.save()
        else:
            raise ValueError('Not enough stock available')

    def deallocate_stock(self, quantity):
        """
        Deallocates stock that was held for a purchase but is no longer needed.
        """
        if self.quantity_allocated >= quantity:
            self.quantity_allocated -= quantity
            self.quantity_in_stock += quantity
            self.save()
        else:
            raise ValueError('Not enough stock allocated')

    def restock(self, quantity):
        """
        Adds stock, increasing the quantity_in_stock.
        """
        self.quantity_in_stock += quantity
        self.save()

    def __str__(self):
        return f'Inventory for {self.product.name}'

class Feedback(models.Model):
    """
    Model representing feedback for a product.

    Attributes:
        product (Product): The product associated with the feedback.
        user (User): The user who provided the feedback.
        comment (str): The feedback comment.
        created_at (DateTime): The timestamp when the feedback was created.

    Methods:
        __str__(): Returns a string representation of the feedback.

    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback by {self.user.username} on {self.product.name}'