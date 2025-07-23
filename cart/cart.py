
from Store.models import Product, Profile

class Cart():
    def __init__(self, request):
        self.session = request.session
        #get request
        self.request = request
       
       #Get the current session key if it exists or create a new one
        cart = self.session.get('session_key')
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
            # Make sure cart is available on all pages of the site
        self.cart = cart

    def db_add(self, product, quantity):
        # Add a product to the cart
        product_id = str(product)
        product_qty = str(quantity)
        # Check if the product is already in the cart
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)    
        self.session.modified = True
        #Deal with logged in user
        if self.request.user.is_authenticated:
            #Get the current user's profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #Convert to json format {"4":3, "5":2}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #save carty to the Profile Model
            current_user.update(old_cart=str(carty))

    def add(self, product, quantity):
        # Add a product to the cart
        product_id = str(product.id)
        product_qty = str(quantity)
        # Check if the product is already in the cart
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)    
        self.session.modified = True
        #Deal with logged in user
        if self.request.user.is_authenticated:
            #Get the current user's profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #Convert to json format {"4":3, "5":2}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #save carty to the Profile Model
            current_user.update(old_cart=str(carty))

    def cart_total(self):
        #Get product ids
        product_ids = self.cart.keys()
        # lookup those keys in our products database model
        products = Product.objects.filter(id__in=product_ids)
        #Get quantities
        quantities = self.cart
        #Start counting at 0
        total = 0
        for key, value in quantities.items():
            #Convert key str in int so we can do math
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total = total + (product.sale_price * value)
                    else:
                        total = total + (product.price * value)
        return total

    def __len__(self):
        # Return the number of items in the cart
        return len(self.cart)
    
    def get_prods(self):
        # Get ids from the cart
        product_ids = self.cart.keys()
        # Use ids to look up products in the database
        products = Product.objects.filter(id__in=product_ids)
        # Return the products
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def update(self, product, quantity):
        # Update the quantity of a product in the cart
        product_id = str(product)
        product_qty = int(quantity)
        # Update our cart/dictionary
        self.cart[product_id] = product_qty
        self.session.modified = True
         #Deal with logged in user
        if self.request.user.is_authenticated:
            #Get the current user's profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #Convert to json format {"4":3, "5":2}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #save carty to the Profile Model
            current_user.update(old_cart=str(carty))
        return self.cart
    
    def delete(self, product):
        product_id = str(product)
        #delete from dictionary/cart
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True
         #Deal with logged in user
        if self.request.user.is_authenticated:
            #Get the current user's profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #Convert to json format {"4":3, "5":2}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #save carty to the Profile Model
            current_user.update(old_cart=str(carty))
