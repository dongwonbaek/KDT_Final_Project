from articles.models import *

def variable_to_base(request): 
    context = {
        'categories': Product.category_choice,
    }
    return context