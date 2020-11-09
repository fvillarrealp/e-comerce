from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # on_delate CASCADE means that when the User is delated, the Customer too
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    digital = models.BooleanField(default=False, null=True, blank=True) # If a product is digital, we dont neet to put it on the shipping
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    # Property let us access this as an attribute rather than a method
    @property # To avoid error when there's no picture
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        
        return url

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateField(auto_now_add=True) # Select the current date
    complete  = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self): # If at least element of the order is not digital, a shipping exist
        shipping = False
        orderItems = self.orderitem_set.all()

        for item in orderItems:
            if item.product.digital == False:
                shipping = True
                break
        
        return shipping
    
    @property
    def get_cart_total(self): # Show the total price to pay
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self): # Show the amount of items to pay 
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True) # Select the current date

    @property
    def get_total(self): # Show the current price of the row
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateField(auto_now_add=True) # Select the current date

    def __str__(self):
        return self.address

# Create your models here.
