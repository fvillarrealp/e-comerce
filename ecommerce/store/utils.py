# This file is to follow the D.R.Y principle for don't repeating code

import json
from .models import *

# CTRL + L TO INDENT SELECTED LINES OF CODE


def cookieCart(request):
    try:
        # We can use the cookie in this way since it's read as a string value
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {} # This help us to avoid the bug when we dont have cookies for the moment 
        
    print('Cart:',cart)
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']
        

    # Since we dont have any order, we need to load the variables manually
    for i in cart:
        try: #PUT  try if the item is delated when we're in the cart template
            product = Product.objects.get(id=i)
            total = product.price * cart[i]['quantity']

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product':{
                    'id':i,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL   
                    },
                'quantity':cart[i]['quantity'],
                'get_total':total,
            }
            items.append(item)

            if product.digital == False: # If any item is not digital, then it requiere shipping
                order['shipping'] = True

        except:
            pass

        cartItems = order['get_cart_items']

    return {'items': items, 'order': order, 'cartItems': cartItems}




def cartData(request):
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()  # The reason the reverse is a queryset, ForeignKey is 1-to-many relationship.
        cartItems = order.get_cart_items
    else: # Inside this else statement we are gonna use the cookies because the user is not logged in
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    
    return {'items': items, 'order': order, 'cartItems': cartItems}



def guestOrder(request, data):
    print('User is not logged in')
    print('COOKIES:', request.COOKIES)

    name = data['form']['name']
    email = data['form']['email']
        
    cookieData = cookieCart(request)
    items = cookieData['items']

    # In order to trace a certain user behavior, if someone has made a purchase
    # we just confirm the email because if him/her wants to create a user in our web,
    # we already have their last orders data in our database
    customer, created = Customer.objects.get_or_create(
        email=email # We use it as a 'foreing key' to identify if someone has made a purchase in the past
    )

    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items: # Go to cookieCart function to understand the items dictionary
        product = Product.objects.get(id=item['product']['id'])

        orderitem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],  
        )
    
    return customer, order