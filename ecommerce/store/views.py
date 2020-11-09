from django.shortcuts import render
from django.http import JsonResponse
import json
from datetime import datetime
from .models import *
from.utils import cookieCart, cartData

# Create your views here.
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)



def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)



def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

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