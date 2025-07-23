from django.shortcuts import render, redirect
from .models import Product, Category, Order, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.db.models import Q
import json
from cart.cart import Cart
# Create your views here.


def search(request):
    #Determine if user filled the form
    if request.method == 'POST':
        searched = request.POST['searched']
        #Query the product in the db model
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        #Test for null
        if not searched:
            messages.success(request, 'Sorry the requested product could not be found')
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched':searched})
    else:
        return render(request, 'search.html', {})

def update_info(request):
    if request.user.is_authenticated:
        #get current user
        current_user = Profile.objects.get(user__id=request.user.id)
        #get current user's shipping info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #Get original user form
        form = UserInfoForm(request.POST or None, instance=current_user)
        #Get user's shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() and shipping_form.is_valid():
          form.save()
          shipping_form.save()
          messages.success(request, 'Your info has been updated successfully')
          return redirect('home')
        return render(request, 'update_info.html', {'form':form, 'shipping_form':shipping_form})
    else:
        messages.success(request, 'You must be logged in before you can access this page')
        return redirect('home')

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been updated')
                # login(request, current_user)
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
          form = ChangePasswordForm(current_user)
          return render(request, 'update_password.html', {'form':form})
    else:
        messages.success(request, 'You must be logged in before you can access this page')
        return redirect('home')


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, 'User profile has been updated successfully')
            return redirect('home')
        return render(request, 'update_user.html', {'user_form':user_form})
    else:
        messages.success(request, 'You must be logged in before you can access this page')
        return redirect('home')

def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories':categories})

def category(request, tab):
    # replace hyphen with space in the tab variable
    tab = tab.replace('-', ' ')
    # Grab the category from the url
    try:
        category = Category.objects.get(name=tab)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'category': category, 'products': products})
    except Category.DoesNotExist:
        messages.error(request, 'Category not found.')
        return redirect('home')

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def about(request):
    return render(request, 'about.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            #Get the saved cart from he database
            saved_cart = current_user.old_cart
            #Convert db string to python dictionary
            if saved_cart:
                #Convert to dictionary using python
                converted_cart = json.loads(saved_cart)
                #Add the loaded cart dictionary to our session
                #Get the cart
                cart = Cart(request)
                #Loop through the cart and add the items from the db
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)



            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return render(request, 'logout.html')

def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Registration successful! Please fill out your user info below')
            return redirect('update_info')
        else:
            messages.error(request, 'Registration failed. Please try again.')
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})
    
