from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from Store.models import Product, Profile
import datetime
# Create your views here.


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #Get the order
        order = Order.objects.get(pk=pk)
        #Get the order items
        items = OrderItem.objects.filter(order=pk)
        if request.POST:
            status = request.POST['shipping_status']
            #check if true of false
            if status == 'true':
                order = Order.objects.filter(pk=pk)
                #update status
                now = datetime.datetime.now()
                order.update(is_shipped=True, date_shipped=now)
                messages.success(request, 'Shipping Status Updated Succesfully')
                return redirect('shipped_dash')
            else:
                order = Order.objects.filter(pk=pk)
                #update status
                order.update(is_shipped=False)
                messages.success(request, 'Shipping Status Updated Succesfully')
                return redirect('not_shipped_dash')
        return render(request, 'payment/orders.html', {'order':order, 'items':items})
        
    else:
        messages.success(request, 'You are not allowed to access this page')
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(is_shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(pk=num)
            now = datetime.datetime.now()
            order.update(is_shipped=True, date_shipped=now)
            messages.success(request, 'Shipping Status Updated Succesfully')
            return redirect('shipped_dash')
        return render(request, 'payment/not_shipped_dash.html', {'orders':orders})
    else:
        messages.success(request, 'You are not allowed to access this page')
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(is_shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(pk=num)
            now = datetime.datetime.now()
            order.update(is_shipped=False, date_shipped=now)
            messages.success(request, 'Shipping Status Updated Succesfully')
            return redirect('not_shipped_dash')
        return render(request, 'payment/shipped_dash.html', {'orders':orders})
    else:
        messages.success(request, 'You are not allowed to access this page')
        return redirect('home')

def payment_success(request):
    return render(request, 'payment/payment_success.html', {})

def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        #Get Billing Info from the last page
        payment_form = PaymentForm(request.POST or None)
        #Get Shipping Session data
        my_shipping = request.session.get('my_shipping')
        #Gather order model
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        #Create shipping Address for session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['country']}"
        amount_paid = totals
        #create an order
        if request.user.is_authenticated:
            #logged in 
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid) 
            create_order.save()
            #Add Order Items
            #Get the order id
            order_id = create_order.pk
            #Get product info
            for product in cart_products():
                #Get product id
                product_id = product.id
                #Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                #Get quantity
                for key,value in quantities.items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()
            #Delete cart session info after purchase
            for key in list(request.session.keys()):
                if key == 'session_key':
                    del request.session[key]

            #Deleate cart from db(old_cart_field)
            current_user = Profile.objects.filter(user__id=request.user.id)
            #Delete shopping cart in database (old_cart_field)
            current_user.update(old_cart='')


            messages.success(request, 'Order processed succesfully')
            return redirect('home')
            
        else:
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid) 
            create_order.save()
             #Add Order Items
            #Get the order id
            order_id = create_order.pk
            #Get product info
            for product in cart_products():
                #Get product id
                product_id = product.id
                #Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                #Get quantity
                for key,value in quantities.items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
             #Delete cart session info after purchase
            for key in list(request.session.keys()):
                if key == 'session_key':
                    del request.session[key]
            messages.success(request, 'Order processed succesfully')
            return redirect('home')
    else:
        messages.success(request, 'Access Denied! You must be logged in before accessing this page')
        return redirect('home')

def billing_info(request):
    if request.POST:    
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        #Create a session with Shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        #Check to see if user is logged in
        if request.user.is_authenticated:
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals':totals, 'shipping_info':request.POST, 'billing_form':billing_form})
        else:
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals':totals, 'shipping_info':request.POST, 'billing_form':billing_form})
    else:
        messages.success(request, 'Access Denied! You must be logged in before accessing this page')
        return redirect('home')

# def billing_info(request):
#     cart = Cart(request)
#     cart_products = cart.get_prods()
#     quantities = cart.get_quants()
#     totals = cart.cart_total()

#     # If it's a POST request, store shipping info in session
#     if request.method == "POST":
#         request.session['my_shipping'] = request.POST

#     billing_form = PaymentForm()

#     return render(request, 'payment/billing_info.html', {
#         'cart_products': cart_products,
#         'quantities': quantities,
#         'totals': totals,
#         'shipping_info': request.session.get('my_shipping', {}),
#         'billing_form': billing_form
#     })



def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #Checkout as logged in user
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals':totals, 'shipping_form':shipping_form})
    else:
        #Checkout as a guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals':totals, 'shipping_form':shipping_form})




