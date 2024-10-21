from .cart import Cart
# craete contxt processor so that our cart can work on all pages
def cart(request): 
    return {'csrt':Cart(request)}