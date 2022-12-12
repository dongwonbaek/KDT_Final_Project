from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import (
    ProductForm,
    ProductImagesForm,
    ReviewForm,
    ReviewCommentForm,
    CommunityForm,
    CommunityImagesForm,
    CommunityCommentForm,
)
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, F, Avg, Count, Subquery, OuterRef, Sum
from django.http import JsonResponse
import random


def index(request):
    gender_products = Product.objects.annotate(wish_men_cnt=Count('like_user', filter=Q(like_user__gender=True) & Q(like_user__age=2)), wish_women_cnt=Count('like_user', filter=Q(like_user__gender=False)), wish_cnt=Count('like_user'))
    if request.user.is_authenticated:
        if request.user.gender:
            gender_products = Product.objects.annotate(wish_men_cnt=Count('like_user', filter=Q(like_user__gender=True) & Q(like_user__age=request.user.age))).order_by("-wish_men_cnt")[:20]
        else:
            gender_products = Product.objects.annotate(wish_women_cnt=Count('like_user', filter=Q(like_user__gender=False) & Q(like_user__age=request.user.age))).order_by("-wish_women_cnt")[:20]
    else:
        gender_products = gender_products.order_by("-wish_cnt")[:20]
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
    reviews = product.review_set.annotate(
        like_cnt=Count("good_user", distinct=True)
        + Count("cool_user", distinct=True)
        + Count("fun_user", distinct=True)
        + Count("sad_user", distinct=True)
    )
    like_reviews = reviews.order_by("-like_cnt")
    recent_reviews = reviews.order_by("-created_at")
    rating_avg = product.review_set.aggregate(rating_avg=Avg("rating"))["rating_avg"]
    random_products = Product.objects.filter(category=product.category).order_by("?")[
        :10
    ]
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
        "product": product,
        "rating_avg": rating_avg,
        "quotient_list": quotient_list,
        "rest_list": rest_list,
        "half_list": half_list,
        "like_reviews": like_reviews,
        "recent_reviews": recent_reviews,
        "random_products": random_products,
        "rating_list": rating_list,
        "review_comment_form": ReviewCommentForm(),
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
            messages.success(request, "글 수정 완료")
            return redirect("articles:product_detail", product_pk)
        else:
            messages.error(request, '유효하지 않은 양식입니다.')
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
            messages.success(request, "등록되었습니다.")
            return redirect("articles:product_detail", product_pk)
        else:
            messages.error(request, '유효하지 않은 양식입니다.')
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
        messages.error(request, "본인 글만 수정할 수 있습니다.")
        return redirect("articles:product_detail", review.product.pk)
    if request.method == "POST":
        review_form = ReviewForm(request.POST, request.FILES, instance=review)
        if review_form.is_valid():
            review_form.save()
            messages.success(request, '수정되었습니다.')
            return redirect("articles:product_detail", review.product.pk)
        else:
            messages.error(request, '유효하지 않은 양식입니다.')
            return redirect("articles:product_detail", review.product.pk)
    else:
        review_form = ReviewForm(instance=review)
        context = {
            'review': review,
            "review_form": review_form,
        }
    return render(request, "articles/review_update.html", context)


@login_required
def review_delete(request, product_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == "POST":
        if request.user == review.user:
            review.delete()
            messages.success(request, "삭제되었습니다.")
            return redirect("articles:product_detail", product_pk)
    else:
        messages.error(request, '유효하지 않은 접근입니다.')
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
                    isimage = a.user.image.url
                else:
                    isimage = '/static/img/no-avatar.jpg'
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
                        isimage, #8
                        a.created_at.month, #9
                        a.created_at.day, #10
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
    else:
        messages.error(request, '본인 댓글만 삭제할 수 있습니다.')
    return redirect("articles:product_detail", comment.review.product.pk)


def product_rank(request):
    products = Product.objects.filter(Q(price__gte=0)&Q(price__lte=20000)).annotate(wish_cnt=Count("like_user", filter=Q(like_user__age__in=list(range(16))))).order_by('-wish_cnt')[:20]
    context = {
        "products": products,
    }
    return render(request, "articles/product_rank.html", context)

def product_rank_redirect(request):
    query_dict = {
        '1': list(range(16)),
        '2': [0, 1],
        '3': [2, 3],
        '4': [4, 5, 6],
        '5': list(range(7, 16)),
        'max20000': [0, 20000],
        'max50000': [20000, 50000],
        'max10000000': [50000, 10000000],
        'all': [True, False],
        'True': [True],
        'False': [False],
    }
    age = request.GET.get("age")
    gender = request.GET.get("gender")
    typeof = request.GET.get("sort")
    price = request.GET.get("price")
    products = Product.objects.filter(Q(price__gte=query_dict[price][0])&Q(price__lte=query_dict[price][1]))
    if typeof == 'wish':
        products = products.annotate(wish_cnt=Count("like_user", filter=Q(like_user__gender__in=query_dict[gender]) & Q(like_user__age__in=query_dict[age]))).order_by('-wish_cnt')[:20]
    elif typeof == 'rating':
        products = products.annotate(rating_avg=Avg("review__rating", filter=Q(review__user__gender__in=query_dict[gender]) & Q(review__user__age__in=query_dict[age]))).order_by('-rating_avg')[:20]
    elif typeof == 'review':
        products = products.annotate(review_cnt=Count("review", filter=Q(review__user__gender__in=query_dict[gender]) & Q(review__user__age__in=query_dict[age]))).order_by('-review_cnt')[:20]
    product_list = []
    for a in range(len(products)):
        image = str(products[a].productimages_set.all()[0].images)
        forloop = a + 1
        product_list.append([
            image, #0
            products[a].title, #1
            products[a].price, #2
            products[a].pk, #3
            forloop, #4
            products[a].brand, #5
            ])
    context = {
        'products':product_list,
    }
    return JsonResponse(context)
    

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
    if request.user.is_authenticated:
        if request.user in product.like_user.all():
            product.like_user.remove(request.user)
            is_liked = False
        else:
            product.like_user.add(request.user)
            is_liked = True
        context = {"isLiked": is_liked, "likeCount": product.like_user.count()}
        return JsonResponse(context)
    else:
        messages.error(request, '로그인 후 이용하실 수 있습니다.')
        return redirect('articles:product_detail', product_pk)


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
    context = {"isCooled": is_cooled, "coolCount": review.cool_user.count()}
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
    context = {"isFuned": is_funed, "funCount": review.fun_user.count()}
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

    context = {"isSaded": is_saded, "sadCount": review.sad_user.count()}
    return JsonResponse(context)


def community_index(request):
    communities = Community.objects.order_by("-pk")
    context = {
        "communities": communities,
        }
    return render(request, "articles/community_index.html", context)


def community_create(request):
    if request.method == "POST":
        community_form = CommunityForm(request.POST, request.FILES)
        community_images_form = CommunityImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")
        if community_form.is_valid() and community_images_form.is_valid():
            community = community_form.save(commit=False)
            community.user = request.user
            community.save()
            if images:
                for image in images:
                    image_instance = CommunityImages(community=community, images=image)
                    image_instance.save()
            messages.success(request, "등록되었습니다.")
            return redirect('articles:community_index')

    else:
        community_form = CommunityForm()
        community_images_form = CommunityImagesForm()
    context = {
        "community_form": community_form,
        "community_images_form": community_images_form,
    }
    return render(request, "articles/community_form.html", context)


def community_update(request, community_pk):
    community = get_object_or_404(Community, pk=community_pk)
    if request.method == "POST":
        community_form = CommunityForm(request.POST, request.FILES, instance=community)
        community_images_form = CommunityImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")
        if community_form.is_valid() and community_images_form.is_valid():
            community = community_form.save(commit=False)
            community.user = request.user
            if images:
                for image in images:
                    image_instance = CommunityImages(community=community, images=image)
                    image_instance.save()
            community.save()
            messages.success(request, "수정되었습니다.")
        else:
            messages.error(request, '유효하지 않은 양식입니다.')
        return redirect('articles:community_detail', community_pk)

    else:
        community_form = CommunityForm(instance=community)
        community_images_form = CommunityImagesForm()
    context = {
        "community_form": community_form,
        "community_images_form": community_images_form,
    }
    return render(request, "articles/community_form.html", context)


def community_delete(request, community_pk):
    community = get_object_or_404(Community, pk=community_pk)
    community.delete()
    messages.success(request, '삭제되었습니다.')
    return redirect('articles:community_index')


def community_detail(request, community_pk):
    community = get_object_or_404(Community, pk=community_pk)
    community_comment_form = CommunityCommentForm()
    context = {
         'community': community,
         'comments': community.communitycomment_set.all(),
         'community_comment_form': community_comment_form,

    }
    return render(request, 'articles/community_detail.html', context)


@login_required
def community_comment_create(request, community_pk):
    print(request.POST)
    community = get_object_or_404(Community, pk=community_pk)
    community_comment_form = CommunityCommentForm(request.POST)
    if community_comment_form.is_valid():
        comment = community_comment_form.save(commit=False)
        comment.community = community
        comment.user = request.user
        comment.save()
        context = {
            'userImg': comment.user.image.url,
            'content': comment.content,
            'userName': comment.user.username
        }
        return JsonResponse(context)


def md_jsm(request):
    context = {
        "one": Product.objects.get(title='최고 인기 선물 밀크앤허니 호두파이'),
        "two": Product.objects.get(title='쫀득쫀득, 달콤하게 사르르 녹는 소프트 초콜릿'),
        "three": Product.objects.get(title='최고 인기 선물 밀크앤허니 호두파이'),
        "four": Product.objects.get(title='쫀득쫀득, 달콤하게 사르르 녹는 소프트 초콜릿'),
        "five": Product.objects.get(title='최고 인기 선물 밀크앤허니 호두파이'),
        "six": Product.objects.get(title='쫀득쫀득, 달콤하게 사르르 녹는 소프트 초콜릿'),
        "seven": Product.objects.get(title='최고 인기 선물 밀크앤허니 호두파이'),
        "eight": Product.objects.get(title='쫀득쫀득, 달콤하게 사르르 녹는 소프트 초콜릿'),
    }
    return render(request, "articles/md_jsm.html", context)


def md_kbw(request):
    context = {
        "one": Product.objects.get(title='[2타입/4색상] 에이블팩토리 허그미 윈터 슈즈 털슬리퍼 겨울 실내화 슬리퍼'),
        "two": Product.objects.get(title='[15%할인][홀리데이][선물포장] 향기보습 핸드크림 & 립밤 기프트 세트'),
        "three": Product.objects.get(title='NEW "겨울 핫템" 카카오프렌즈 얼굴형 손난로 보조배터리 5000mAh'),
        "four": Product.objects.get(title='불멍 캠핑 화로 난로 불무드 에탄올램프 (에탄올+캔들라이터 증정)'),
        "five": Product.objects.get(title='[따뜻한 선물] "따듯한 치즈덕이쥬" 부들 포근 치즈덕 극세사 담요 (톡별)'),
        "six": Product.objects.get(title='완도전복죽'),
        "seven": Product.objects.get(title='"오늘도 따뜻할 거예요" 히트템 핫팩 30매+메세지박스+손소독제 5개입 (톡별) (heattem)'),
        "eight": Product.objects.get(title='"매일 예쁘고 포근해" 수면 파자마 상하의 16종 택1/남녀커플 상품 추가'),
    }
    return render(request, "articles/md_kbw.html", context)


def md_kkh(request):
    context = {
        "one": Product.objects.get(title='최고 인기 선물 밀크앤허니 호두파이'),
        "two": Product.objects.get(title='쫀득쫀득, 달콤하게 사르르 녹는 소프트 초콜릿'),
        "three": Product.objects.get(title='최고 인기 선물 밀크앤허니 호두파이'),
        "four": Product.objects.get(title='쫀득쫀득, 달콤하게 사르르 녹는 소프트 초콜릿'),
        "five": Product.objects.get(title='최고 인기 선물 밀크앤허니 호두파이'),
        "six": Product.objects.get(title='쫀득쫀득, 달콤하게 사르르 녹는 소프트 초콜릿'),
        "seven": Product.objects.get(title='최고 인기 선물 밀크앤허니 호두파이'),
        "eight": Product.objects.get(title='쫀득쫀득, 달콤하게 사르르 녹는 소프트 초콜릿'),
    }
    return render(request, "articles/md_kkh.html", context)