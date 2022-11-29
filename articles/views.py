from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import ProductForm, ProductImagesForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse

def index(request):
    return render(request, "articles/index.html")

def product_create(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)
        product_images_form = ProductImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist('image')
        if product_form.is_valid() and product_images_form.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            if images:
                for image in images:
                    image_instance = ProductImages(product=product, image=image)
                    image_instance.save()
            product.save()
            messages.success(request, '글 생성 완료')
            return redirect('articles:index')
    else:
        product_form = ProductForm()
        product_images_form = ProductImagesForm()
    context = {
        'product_form': product_form,
        'product_images_form': product_images_form
    }
    return render(request, 'articles/product_create.html', context)

def product_detail(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    context = {
        'product': product,
    }
    return render(request, 'articles/product_detail.html', context)

def product_update(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        product_images_form = ProductImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist('image')
        if product_form.is_valid() and product_images_form.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            if images:
                for image in images:
                    image_instance = ProductImages(product=product, image=image)
                    image_instance.save()
            product.save()
            messages.success(request, '글 생성 완료')
            return redirect('articles:product_detail', product_pk)
    else:
        product_form = ProductForm(instance=product)
        product_images_form = ProductImagesForm()
    context = {
        'product_form': product_form,
        'product_images_form': product_images_form
    }
    return render(request, 'articles/product_create.html', context)

def product_delete(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    product.delete()
    return redirect('articles:index')