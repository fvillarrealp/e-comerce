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
