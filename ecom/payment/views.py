from django.shortcuts import render,redirect
from cart.cart import Cart
from .models import ShippingAddress,Order,OrderItem
from .forms import ShippingForm,PaymentForm
from django.contrib import messages
from django.contrib.auth.models import User
from store.models import Product
import datetime

#import some paypal stuffs

from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid #cretae unique user id for duplicate orders

# Create your views here.
def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order =  Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status =  request.POST['shipping_status']
            if status == 'true':
                #get order no
                order = Order.objects.filter(id=pk)
                #update the status
                now = datetime.datetime.now()
                order.update(shipped=True,date_shipped = now)
            else:
                #get order no
                order = Order.objects.filter(id=pk)
                #update the status
                order.update(shipped=False)

            messages.success(request,"shipping status updated")
            return redirect('home')
        return render(request,'payment/orders.html',{"order":order,"items":items})
    
    else:
        messages.success(request,"Access denied")
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped = False)
        if request.POST:
            status =  request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            order.update(shipped=True,date_shipped = now)

            messages.success(request,"shipping status updated")
            return redirect('home')
        return render(request,'payment/not_shipped_dash.html',{"orders":orders})
    
    else:
        messages.success(request,"Access denied")
        return redirect('home')


def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped = True)
        if request.POST:
            status =  request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            order.update(shipped=False)


            messages.success(request,"shipping status updated")
            return redirect('home')
        return render(request,'payment/shipped_dash.html',{"orders":orders})
    
    else:
        messages.success(request,"Access denied")
        return redirect('home')


def process_order(request):
    if request.POST:
        cart =  Cart(request)
        cart_products = cart.get_prods
        quantities =  cart.get_quant
        totals = cart.cart_total()

        payment_form =  PaymentForm(request.POST or None)
        #get shipping session data
        my_shipping = request.session.get('my_shipping')

        #gather order info
        full_name = my_shipping['full_name']
        email = my_shipping['email']

       #create shipping address from
        shipping_address = f"{my_shipping['address1']}\n{my_shipping['address2']}\n{my_shipping['city']}\n{my_shipping['state']}\n{my_shipping['zipcode']}\n{my_shipping['country']}"
        amount_paid = totals

        if request.user.is_authenticated:
            #loggedin
            user = request.user

            #create order
            create_order = Order(user =user,full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
            create_order.save()

            #get order id
            order_id = create_order.pk

            #get product info
            for product in cart_products():
                #get product id
                product_id = product.id

                #get price
                if product.is_sale:
                    price= product.sale_price
                else:
                    price=product.price
                
                #get quantity

                for key,value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id,product_id=product_id,user=user,quantity=value,price=price)
                        create_order_item.save()
            
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            messages.success(request,"Order placed!!")
            return redirect('home')
        else:
            #not logged
            #create order
            create_order = Order(full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
            create_order.save()
            
            #get order id
            order_id = create_order.pk

            #get product info
            for product in cart_products():
                #get product id
                product_id = product.id

                #get price
                if product.is_sale:
                    price= product.sale_price
                else:
                    price=product.price
                
                #get quantity

                for key,value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id,product_id=product_id,quantity=value,price=price)
                        create_order_item.save()

            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]
                    
            messages.success(request,"Order placed!!")
            return redirect('home')

    else:
        messages.success(request,"Access denied")
        return redirect('home')

def billing_info(request):
    if request.POST:
        cart =  Cart(request)
        cart_products = cart.get_prods
        quantities =  cart.get_quant
        totals = cart.cart_total()

        #create a sesson with shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        #get the host
        host = request.get_host()

        #create paypal form and stuffs
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount':totals,
            'item_name':'Bokk Order',
            'no_shipping':'2',
            'invoice':str(uuid.uuid4()),
            'currency_code': 'USD',
            'notfy_url':'http://{}{}'.format(host,reverse("paypal-ipn")),
            'return_url':'http://{}{}'.format(host,reverse("payment_success")),
            'cancel_return':'http://{}{}'.format(host,reverse("payment_failed")),
        }

        #create actual paypal button
        paypal_form = PayPalPaymentsForm(initial = paypal_dict)

        #check to see if user is loggedin
        if request.user.is_authenticated:
            #get billing info
            billing_form = PaymentForm()
            return render(request,'payment/billing_info.html',{"paypal_form":paypal_form,"cart_products":cart_products , "quantities":quantities,"totals":totals,"shipping_info":request.POST,"billing_form":billing_form})
 
        else:
            billing_form = PaymentForm()
            return render(request,'payment/billing_info.html',{"paypal_form":paypal_form,"cart_products":cart_products , "quantities":quantities,"totals":totals,"shipping_info":request.POST,"billing_form":billing_form})
 

        shipping_form = request.POST
        return render(request,'payment/billing_info.html',{"cart_products":cart_products , "quantities":quantities,"totals":totals,"shipping_form":request.POST,"billing_form":billing_form})
 
    else:
        messages.success(request,"Access denied")
        return redirect('home')

def payment_success(request):
    return render(request,'payment/payment_success.html',{})

def payment_failed(request):
    return render(request,'payment/payment_failed.html',{})

def checkout(request):
    cart =  Cart(request)
    cart_products = cart.get_prods
    quantities =  cart.get_quant
    totals = cart.cart_total()
    if request.user.is_authenticated:
        shipping_user=ShippingAddress.objects.get(user_id = request.user.id)
        shipping_form = ShippingForm(request.POST or None,instance=shipping_user)
        return render(request,'payment/checkout.html',{"cart_products":cart_products , "quantities":quantities,"totals":totals,"shipping_form":shipping_form})
    else:
        shipping_form = ShippingForm(request.POST or None)
        return render(request,'payment/checkout.html',{"cart_products":cart_products , "quantities":quantities,"totals":totals,"shipping_form":shipping_form})

