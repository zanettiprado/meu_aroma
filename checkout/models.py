import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.utils import timezone
from products.models import Product
from profiles.models import UserProfile
from decimal import Decimal


class Order(models.Model):
    """
    Represents an order placed by a user.
    """
    order_number = models.UUIDField(primary_key=True,
                                    default=uuid.uuid4,
                                    editable=False)
    user_profile = models.ForeignKey(UserProfile,
                                     on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='orders')
    full_name = models.CharField(max_length=50,
                                 null=False, blank=False)
    email = models.EmailField(max_length=254,
                              null=False, blank=False)
    phone_number = models.CharField(max_length=20,
                                    null=False, blank=False)
    country = models.CharField(max_length=40,
                               null=False, blank=False)
    postcode = models.CharField(max_length=20,
                                null=True, blank=True)
    town_or_city = models.CharField(max_length=40,
                                    null=False, blank=False)
    street_address1 = models.CharField(max_length=80,
                                       null=False, blank=False)
    street_address2 = models.CharField(max_length=80,
                                       null=True, blank=True)
    county = models.CharField(max_length=80, null=True,
                              blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6,
                                        decimal_places=2, null=False,
                                        default=0)
    order_total = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      null=False, default=0)
    grand_total = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      null=False, default=0)
    payment_intent_id = models.CharField(max_length=255,
                                         null=True, blank=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL,
                               null=True, blank=True,
                               related_name='orders')
    
    def update_totals(self):
        lineitem_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum']
        if lineitem_total is None:
            lineitem_total = Decimal('0.00')
        else:
            lineitem_total = Decimal(lineitem_total)

        self.order_total = lineitem_total

        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / 100
        else:
            self.delivery_cost = Decimal('0.00')

        if self.coupon and self.coupon.is_valid():
            discount_percentage = Decimal(str(self.coupon.discount))
            discount_amount = Decimal(round((self.order_total * discount_percentage) / 100, 2))
            self.grand_total = self.order_total + self.delivery_cost - discount_amount
        else:
            self.grand_total = self.order_total + self.delivery_cost

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = uuid.uuid4().hex.upper()

        self.update_totals()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return str(self.order_number)
    
    
class OrderLineItem(models.Model):
    """
    Represents an individual line item within an order.
    """
    
    order = models.ForeignKey('Order', null=False,
                              blank=False, on_delete=models.CASCADE,
                              related_name='lineitems')
    product = models.ForeignKey(Product,
                                null=False, blank=False,
                                on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=False,
                                           blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2,
                                         null=False, blank=False,
                                         editable=False)


    def save(self, *args, **kwargs):

        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_totals()
        self.order.save()

    def __str__(self):
        return f'Item: {self.product.name} on Order: {self.order.order_number}'

class Coupon(models.Model):
    """
    Represents a coupon that can be applied to an order for a discount.
    """
    code = models.CharField(max_length=15, unique=True)
    description = models.TextField(null=True,
                                   blank=True)
    discount = models.DecimalField(max_digits=6,
                                   decimal_places=2,
                                   help_text='Amount of discount this coupon provides')
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
    