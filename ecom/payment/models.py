from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
import datetime
# Create your models here.

class ShippingAddress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255,null=True,blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255,null=True,blank=True)
    zipcode = models.CharField(max_length=255,null=True,blank=True)
    country = models.CharField(max_length=255)

    #Dont pluralize address
    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'
#create a user shipping adreess by default when user is sighn up

def create_shipping(sender,instance,created,**kwargs):
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()

post_save.connect(create_shipping,sender=User)

#create order model

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    full_name =  models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(max_digits=7,decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped =  models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f'Order - {str(self.id)}'

#auto add shipping_date
@receiver(pre_save, sender =Order)
def set_shipped_date_on_update(sender,instance,**kwargs):
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now


#create order item

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7,decimal_places=2)

    def __str__(self):
        return f'Order Item - {str(self.id)}'
