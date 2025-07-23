from django.shortcuts import render, get_object_or_404
from .cart import Cart
from Store.models import Product
from django.http import JsonResponse
from django.contrib import messages


# Create your views here.

def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    return render(request, 'cart_summary.html', {'cart_products': cart_products, 'quantities': quantities, 'totals':totals})

def cart_add(request):
    # get the cart
    cart = Cart(request)
    # Test for post
    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')
        product_qty = request.POST.get('product_qty')
        # Look up the product in the database
        product = get_object_or_404(Product, pk=product_id)
        # Save to session
        cart.add(product=product, quantity= product_qty)
        # get cart qauntity
        cart_quantity = cart.__len__()
        # Return a JsonResponse
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, 'Product Added to cart.')
        return response
        
   

def cart_delete(request):
    # Logic to delete item from cart
    cart = Cart(request)
    if request.POST.get('action') == 'post':
     product_id = int(request.POST.get('product_id'))
     cart.delete(product=product_id)
     response =  JsonResponse({'product':product_id})
     messages.success(request, 'Product deleted from cart.')
     return response

def cart_update(request):
    # Logic to update item in cart
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        cart.update(product=product_id, quantity=product_qty)
        response = JsonResponse({'qty': product_qty})
        messages.success(request, 'Your cart has been updated successfully.')
        return response

