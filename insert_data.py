import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pjt_OJD.settings")

import django
django.setup()

import json
from articles.models import Product, ProductImages

for idx in range(1, 12):
    with open(f'crawling_data/category{idx}.json', encoding='utf-8') as f:
        json_objects = json.load(f)

    if json_objects:
        for x in json_objects:
            product = Product(title=json_objects[x]['name'], category=json_objects[x]['category'], price=int(json_objects[x]['price'].replace('원', '').replace(',', '')))
            productimages = ProductImages(product=product, images=json_objects[x]['img'])
            product.save()
            productimages.save()