from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import ProductForm, ProductImagesForm, ReviewForm, ReviewCommentForm, CommunityForm, CommunityImagesForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, F, Avg, Count, Subquery, OuterRef, Sum
from django.http import JsonResponse
import random


def index(request):
    gender_products = Product.objects.annotate(wish_men_cnt=Count('like_user',filter=Q(like_user__gender=True)), wish_women_cnt=Count('like_user', filter=Q(like_user__gender=False)), wish_cnt=Count('like_user'))

    if request.user.is_authenticated:
        if request.user:
            gender_products = gender_products.order_by("-wish_men_cnt")[:20]
        else:
            gender_products = gender_products.order_by("-wish_women_cnt")[:20]
    else:
        gender_products = gender_products.order_by("-wish_cnt")[:20],

    context = {
        "gender_products": gender_products,
        "categories": Product.category_choice,
    }
    return render(request, "articles/index.html", context)


def product_list(request, category_pk):
    context = {
        "products": Product.objects.filter(category=category_pk)
        .annotate(review_avg=Avg("review__rating"))
        .order_by("-review_avg")
    }
    return render(request, "articles/product_list.html", context)


def product_create(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)
        product_images_form = ProductImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")
        print(images)
        if product_form.is_valid() and product_images_form.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            product.save()
            if images:  # 다중이미지를 저장하기 위한 로직.
                for image in images:
                    image_instance = ProductImages(product=product, images=image)
                    image_instance.save()
            messages.success(request, "글 생성 완료")
            return redirect("articles:index")
    else:
        product_form = ProductForm()
        product_images_form = ProductImagesForm()
    context = {"product_form": product_form, "product_images_form": product_images_form}
    return render(request, "articles/product_create.html", context)


def product_detail(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    reviews = product.review_set.annotate(like_cnt=Count('good_user', distinct=True)+Count('cool_user', distinct=True)+Count('fun_user', distinct=True)+Count('sad_user', distinct=True))
    like_reviews = reviews.order_by('-like_cnt')
    recent_reviews = reviews.order_by('-created_at')
    rating_avg = product.review_set.aggregate(rating_avg=Avg('rating'))['rating_avg']
    random_products = Product.objects.filter(category=product.category).order_by("?")[:10]
    quotient_list = []
    rest_list = []
    half_list = []
    if rating_avg:
        quotient = int(rating_avg // 1)
        rest = round(rating_avg % 1, 1)
        if 0.7 >= rest >= 0.3:
            half_list.append(1)
        elif rest > 0.7:
            quotient_list.append(1)
        for a in range(quotient):
            quotient_list.append(a)
        for a in range(5 - (len(quotient_list) + len(half_list))):
            rest_list.append(1)
    else:
        rating_avg = 0
    rating_list = []
    total = product.review_set.all().count()
    if total:
      for cnt in range(5, 0, -1):
        rating_count = product.review_set.filter(rating=cnt).count()
        if rating_count:
          rating_list.append(round((rating_count / total) * 100))
        else:
          rating_list.append(0)
    context = {
        'product': product,
        'rating_avg': rating_avg,
        'quotient_list': quotient_list,
        'rest_list': rest_list,
        'half_list': half_list,
        'like_reviews': like_reviews,
        'recent_reviews': recent_reviews,
        'random_products': random_products,
        'rating_list': rating_list,
        'review_comment_form': ReviewCommentForm(),
    }
    return render(request, "articles/product_detail.html", context)


def product_update(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        product_images_form = ProductImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist("image")
        if product_form.is_valid() and product_images_form.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            if images:  # 다중이미지를 저장하기 위한 로직.
                for image in images:
                    image_instance = ProductImages(product=product, image=image)
                    image_instance.save()
            product.save()
            messages.success(request, "글 생성 완료")
            return redirect("articles:product_detail", product_pk)
    else:
        product_form = ProductForm(instance=product)
        product_images_form = ProductImagesForm()
    context = {"product_form": product_form, "product_images_form": product_images_form}
    return render(request, "articles/review_update.html", context)


def product_delete(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    product.delete()
    return redirect("articles:index")


def review_index(request):
    reviews = Review.objects.order_by("-pk")
    context = {
        "reviews": reviews,
    }
    return render(request, "articles/review_index.html", context)


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
            messages.success(request, "리뷰가 상공적으로 작성되었습니다.")
            return redirect("articles:product_detail", product_pk)
    else:
        review_form = ReviewForm()
    context = {
        "review_form": review_form,
    }
    return render(request, "articles/review_create.html", context)


@login_required
def review_update(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)

    if request.user != review.user:
        messages.warning(request, "본인 글만 수정할 수 있습니다.")
        return redirect("articles:product_detail", review.product.pk)

    if request.method == "POST":
        review_form = ReviewForm(request.POST, request.FILES, instance=review)
        if review_form.is_valid():
            review_form.save()
            return redirect("articles:product_detail", review.product.pk)
    else:
        review_form = ReviewForm(instance=review)
        context = {
            "review_form": review_form,
        }
    return render(request, "articles/review_update.html", context)


@login_required
def review_delete(request, product_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == "POST":
        if request.user == review.user:
            review.delete()
            messages.success(request, "리뷰가 성공적으로 삭제되었습니다.")
            return redirect("articles:product_detail", product_pk)
    else:
        return redirect("articles:product_detail", product_pk)


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
            comments = []
            for a in review.reviewcomment_set.all():
                if request.user:
                    islogin = True
                else:
                    islogin = False
                if a.user.image:
                    isimage = True
                else:
                    isimage = False
                comments.append(
                    [
                        a.content,  # 0
                        a.user.nickname,  # 1
                        a.created_at.year,  # 2
                        a.user.pk,  # 3
                        request.user.pk,  # 4
                        a.id,  # 5
                        a.review.pk,  # 6
                        islogin,  # 7
                        a.user.image.url, #8
                        a.created_at.month, #9
                        a.created_at.day, #10
                        isimage,
                    ]
                )
            context = {
                "comments": comments,
                # 'commentCount':review.reviewcomment_set.count()
            }
            return JsonResponse(context)


@login_required
def review_comment_delete(request, comment_pk):
    comment = get_object_or_404(ReviewComment, pk=comment_pk)
    if request.user == comment.user:
        comment.delete()
    return redirect("articles:product_detail", comment.review.product.pk)


def product_rank(request):
    if request.method == "POST":
        products = Product.objects.all()
        products_rating = Product.objects.all()
        products_like = Product.objects.all()
        products_review = Product.objects.all()
        gender = request.POST.get("gender")
        sort_type = request.POST.get("sort_type")
        sort_price = request.POST.get("sort_price")
        if sort_price != "none":
            products = products.filter(price__lte=int(sort_price))
            products_rating = products.filter(price__lte=int(sort_price))
            products_like = products.filter(price__lte=int(sort_price))
            products_review = products.filter(price__lte=int(sort_price))
        if gender == "True":
            # products = products.annotate(review_men=)
            products_rating = products.annotate(
                rating_avg=Avg("review__rating", filter=Q(review__user__gender=True))
            ).order_by("-rating_avg")
            products_like = products.annotate(
                like_cnt=Count("like_user", filter=Q(like_user__gender=True))
            ).order_by("-like_cnt")
            products_review = products.annotate(
                review_cnt=Count("review", filter=Q(review__user__gender=True))
            ).order_by("-review_cnt")
        elif gender == "False":
            products_rating = products.annotate(
                rating_avg=Avg("review__rating", filter=Q(review__user__gender=False))
            ).order_by("-rating_avg")
            products_like = products.annotate(
                like_cnt=Count("like_user", filter=Q(like_user__gender=False))
            ).order_by("-like_cnt")
            products_review = products.annotate(
                review_cnt=Count("review", filter=Q(review__user__gender=False))
            ).order_by("-review_cnt")
        if sort_type == "rating":
            products = products_rating.annotate(
                rating_avg=Avg("review__rating")
            ).order_by("-rating_avg")
        elif sort_type == "like":
            products = products_like.annotate(like_cnt=Count("like_user")).order_by(
                "-like_cnt"
            )
        elif sort_type == "review_cnt":
            products = products_review.annotate(review_cnt=Count("review")).order_by(
                "-review_cnt"
            )
        product_list = []
        for a in products[:20]:
            image = str(a.productimages_set.all()[0].images)
            product_list.append([
                image,
                a.title,
                a.price,
                a.pk
                ])
        context = {
            'products':product_list,
        }
        return JsonResponse(context)
    else:
        context = {
            "products": Product.objects.annotate(like_cnt=Count("like_user")).order_by(
                "-like_cnt"
            )[:20],
            "reviews": Review.objects.filter(user__gender=True),
        }
        return render(request, "articles/product_rank.html", context)


def search(request):
    products = None
    # query = 검색값
    query = None
    if request.GET.get("field") != "all":
        field = request.GET.get("field")
        sort_products = Product.objects.filter(category=field)
    else:
        sort_products = Product.objects.all()

    if "q" in request.GET:
        query = request.GET.get("q")
        if query == "":
            return redirect("articles:search")
        query = query.split("&")[0]
        products = sort_products.order_by("-pk").filter(
            Q(title__contains=query)
        )  # title 로 검색

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
    context = {"isLiked": is_liked, "likeCount": product.like_user.count()}
    return JsonResponse(context)


@login_required
def review_good(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user in review.good_user.all():
        review.good_user.remove(request.user)
        is_gooded = False
    else:
        review.good_user.add(request.user)
        is_gooded = True
    context = {"isGooded": is_gooded, "goodCount": review.good_user.count()}
    return JsonResponse(context)
    # return redirect('articles:product_detail', review.product.pk, context)


@login_required
def review_cool(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user in review.cool_user.all():
        review.cool_user.remove(request.user)
        is_cooled = False
    else:
        review.cool_user.add(request.user)
        is_cooled = True
    context = {'isCooled': is_cooled, 'coolCount': review.cool_user.count()}
    return JsonResponse(context)


@login_required
def review_fun(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user in review.fun_user.all():
        review.fun_user.remove(request.user)
        is_funed = False
    else:
        review.fun_user.add(request.user)
        is_funed = True
    context = {'isFuned': is_funed, 'funCount': review.fun_user.count()}
    return JsonResponse(context)


@login_required
def review_sad(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user in review.sad_user.all():
        review.sad_user.remove(request.user)
        is_saded = False
    else:
        review.sad_user.add(request.user)
        is_saded = True

    context = {'isSaded': is_saded, 'sadCount': review.sad_user.count()}
    return JsonResponse(context)


def community_index(request):
    communities = Community.objects.order_by('-pk')
    context = {
        'communities': communities
    }
    return render(request, 'articles/community_index.html', context)


def community_create(request):
    if request.method == 'POST':
        community_form = CommunityForm(request.POST, request.FILES)
        community_images_form = CommunityImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")
        if community_form.is_valid() and community_images_form.is_valid():
            community = community_form.save(commit=False)
            community.save()
            if images:
                for image in images:
                    image_instance = CommunityImages(community=community, images=image)
                    image_instance.save()
            return redirect('articles:community_index')
    else:
        community_form = CommunityForm()
        community_images_form = CommunityImagesForm()
    context = {
        'community_form': community_form,
        'community_images_form': community_images_form,
    }
    return render(request, "articles/community_form.html", context)


def community_update(request, community_pk):
    community = Community.objects.get(pk=community_pk)
    if request.method == 'POST':
        community_form = CommunityForm(request.POST, request.FILES, instance=community)
        community_images_form = CommunityImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")
        if community_form.is_valid() and community_images_form.is_valid():
            community = community_form.save(commit=False)
            if images:
                for image in images:
                    image_instance = CommunityImages(community=community, images=image)
                    image_instance.save()
            community.save()
            return redirect('articles:community_detail', community_pk)
    else:
        community_form = CommunityForm(instance=community)
        community_images_form = CommunityImagesForm()
    context = {
        'community_form': community_form,
        'community_images_form': community_images_form,
    }
    return render(request, "articles/community_form.html", context)


def community_detail(request, community_pk):
    community = Community.objects.get(pk=community_pk)
    context = {
        'community': community
    }
    return render(request, 'articles/community_detail.html', context)


def community_delete(request, community_pk):
    community = Community.objects.get(pk=community_pk)
    community.delete()
    return redirect('articles:community_index')