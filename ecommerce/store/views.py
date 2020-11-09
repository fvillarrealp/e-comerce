from django.shortcuts import render
from django.http import JsonResponse
import json
from datetime import datetime
from .models import *

# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer= customer, complete=False)
        items = order.orderitem_set.all() # The reason the reverse is a queryset is, ForeignKey is 1-to-many relationship. Hence, the reverse is a queryset.
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)





def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer= customer, complete=False)
        items = order.orderitem_set.all() # The reason the reverse is a queryset, ForeignKey is 1-to-many relationship.
        cartItems = order.get_cart_items

    else: # Inside this else statement we are gonna use thoe cookies because of the user is not logged in
        try:
            cart = json.loads(request.COOKIES['cart']) # We can use the cookie in this way since it's read as a string value
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


    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)




def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all() # The reason the reverse is a queryset is, ForeignKey is 1-to-many relationship. Hence, the reverse is a queryset.
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)




def updateItem(request):
    data = json.loads(request.body) # Parse the string to json
    productId = data['productId']
    action = data['action'] 

    print('productId:', productId)
    print('action:', action)

    customer = request.user.customer # To get the customer fro  the current user
    product = Product.objects.get(id=productId) # Getting element by id
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    
    orderItem , created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('It was added', safe=False)





def processOrder(request):
    data = json.loads(request.body)
    transaction_id = datetime.now().timestamp()

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        Order.transaction_id = transaction_id

        if total == order.get_cart_total:
            print("holaaaaaaa")
            order.complete = True
        
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'] ,
                state=data['shipping']['state'] ,
                zipcode=data['shipping']['zipcode'], 
            )
    
    else:
        print('User is not logged in')

    return JsonResponse('Payment success! congrats', safe=False)