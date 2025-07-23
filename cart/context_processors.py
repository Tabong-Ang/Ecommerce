from .cart import Cart

# Create a context processor so our cart cn work on all pages of the site
def cart_context(request):
    # Return the deafault data from our cart
    return {'cart': Cart(request)}