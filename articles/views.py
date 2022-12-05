from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import ProductForm, ProductImagesForm, ReviewForm, ReviewCommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Avg, Count, Subquery, OuterRef
from django.http import JsonResponse

def index(request):
    products = Product.objects.order_by('-pk')
    context = {
        'products': products
    }
    return render(request, "articles/index.html", context)

def product_list(request, category_pk):
    context = {
        'products': Product.objects.filter(category=category_pk).annotate(review_avg=Avg('review__rating')).order_by('-review_avg')
    }
    return render(request, "articles/product_list.html", context)

def product_create(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)
        product_images_form = ProductImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        print(images)
        if product_form.is_valid() and product_images_form.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            product.save()
            if images: # 다중이미지를 저장하기 위한 로직.
                for image in images:
                    image_instance = ProductImages(product=product, images=image)
                    image_instance.save()
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
            if images: # 다중이미지를 저장하기 위한 로직.
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
    return render(request, 'articles/review_update.html', context)

def product_delete(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    product.delete()
    return redirect('articles:index')

def review_index(request):
    reviews = Review.objects.order_by('-pk')
    context = {
        'reviews': reviews,
    }
    return render(request, 'articles/review_index.html', context)


@login_required
def review_create(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    if request.method == "POST":
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, '리뷰가 상공적으로 작성되었습니다.')
            return redirect('articles:product_detail', product_pk)
    else:
        review_form = ReviewForm()
    context = {
        'review_form': review_form,
    }
    return render(request, 'articles/review_create.html', context)

@login_required
def review_update(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    
    if request.user != review.user:
        messages.warning(request, '본인 글만 수정할 수 있습니다.')
        return redirect('articles:product_detail', review.product.pk)
    
    if request.method == "POST":
        review_form = ReviewForm(request.POST, request.FILES, instance=review)
        if review_form.is_valid():
            review_form.save()
            return redirect('articles:product_detail', review.product.pk)
    else:
        review_form = ReviewForm(instance=review)
        context = {
            'review_form': review_form,
        }
    return render(request, 'articles/review_update.html', context)

@login_required
def review_delete(request, product_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == "POST":
        if request.user == review.user:
            review.delete()
            messages.success(request, '리뷰가 성공적으로 삭제되었습니다.')
            return redirect('articles:product_detail', product_pk)
    else:
        return redirect('articles:product_detail', product_pk)

@login_required
def review_like(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if review.like_user.filter(pk=request.user.pk).exists():
        review.like_user.remove(request.user)
    else:
        review.like_user.add(request.user)

    # review_detail 페이지가 모달로 구현되기 위해서는 좋아요 기능이 반드시 비동기처리가 필요함. 
    # 비동기 처리를 구현하기 전까지 임의로 redirect 사용.
    return redirect('articles:product_detail', review.product.pk)

@login_required
def review_comment_create(request, review_pk):
    if request.method == "POST":
        review = get_object_or_404(Review, pk=review_pk)
        review_comment_form = ReviewCommentForm(request.POST)
        if review_comment_form.is_valid():
            comment = review_comment_form.save(commit=False)
            comment.review = review
            comment.user = request.user
            comment.save()
    # 비동기 처리 구현전까지 임의로 redirect 사용
    return redirect('articles:product_detail', review.product.pk)

@login_required
def review_comment_delete(request, comment_pk):
    comment = get_object_or_404(ReviewComment, pk=comment_pk)
    if request.user == comment.user:
        comment.delete()
    # 비동기 처리 구현전까지 임의로 redirect 사용
    return redirect('articles:product_detail', comment.review.product.pk)


def product_rank(request):
    gender = 'all'
    if request.GET.get('gender'):
        gender = request.GET.get('gender')
    if gender == 'all':
        products = Product.objects.all()
    elif gender == 'woman':
        products = Product.objects.all()
        # woman_products = products.annotate(rate_avg=Avg(Review.objects.filter()))
    elif gender == 'man':
        products = Product.objects.all()
    sort_by = 'rating'
    if request.GET.get('sort_by'):
        sort_by = request.GET.get('sort_by')
    if sort_by == 'rating':
        products = Product.objects.annotate(rate_avg=Avg('review__rating')).order_by('-rate_avg')
    elif sort_by == 'like':
        products = Product.objects.annotate(like_cnt=Count('like_user')).order_by('-like_cnt')
    context = {
        'products': products,
    }
    return render(request, 'articles/product_rank.html', context)



def search(request):
    products = None
    # query = 검색값
    query = None
    if request.GET.get('field') != 'all':
        field = request.GET.get('field')
        sort_products = Product.objects.filter(category=field)
    else:
        sort_products = Product.objects.all()

    if "q" in request.GET:
        query = request.GET.get("q")
        if query == "":
            return redirect("articles:search")
        query = query.split("&")[0]
        products = sort_products.order_by("-pk").filter(
            Q(title__contains=query)) # title 로 검색
    
    context = {
        "products": products,
        "query": query,
    }
    return render(request, "articles/search.html", context)

@login_required
def like(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    if request.user in product.like_user.all():
        product.like_user.remove(request.user)
        is_liked = False
    else:
        product.like_user.add(request.user)
        is_liked = True
    context = {'isLiked': is_liked, 'likeCount': product.like_user.count()}
    return JsonResponse(context)