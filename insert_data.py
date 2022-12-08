import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pjt_OJD.settings")

import django
django.setup()

import json
from articles.models import Product, ProductImages, ProductContentImages
# range(1, 12)
for idx in range(1, 12):
    if idx != 10:
        with open(f'crawling_data/category{idx}.json', encoding='utf-8') as f:
            json_objects = json.load(f)

        if json_objects:
            for x in json_objects:
                product = Product(title=json_objects[x]['name'], product_url=json_objects[x]['url'], brand=json_objects[x]['brand'].replace('\n바로가기', ''), category=json_objects[x]['category'], price=int(json_objects[x]['price'].replace('원', '').replace(',', '')))
                product.save()
                for thumbnail_image in json_objects[x]['thumbnail_images']:
                    productimages = ProductImages(product=product, images=thumbnail_image)
                    productimages.save()
                if json_objects[x]['content_images']:
                    for content_image in json_objects[x]['content_images']:
                        productcontentimages = ProductContentImages(product=product, images=content_image)
                        productcontentimages.save()