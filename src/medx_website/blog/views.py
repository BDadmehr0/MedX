from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, PostView
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        if request.FILES.get('file'):
            image = request.FILES['file']
            image_name = image.name
            save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image_name)
            path = default_storage.save(save_path, ContentFile(image.read()))
            image_url = os.path.join(settings.MEDIA_URL, 'uploads', image_name)
            return JsonResponse({'location': image_url})
    return JsonResponse({'error': 'Image upload failed'}, status=400)

def home(request):
    latest_post = Post.objects.latest('publish_date')

    current_month = timezone.now().month
    current_year = timezone.now().year

    # Checking the availability of posts in the current month
    popular_posts = Post.objects.filter(
        publish_date__year=current_year,
        publish_date__month=current_month
    ).order_by('-views')[:3]

    if not popular_posts:
        popular_posts = Post.objects.order_by('-views')[:3]  # If no post found, based on views

    all_posts = Post.objects.order_by('-publish_date')
    paginator = Paginator(all_posts, 9)


    page_number = request.GET.get('page', 1)

    try:
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    context = {
        'latest_post': latest_post,
        'page_obj': page_obj,
        'popular_posts': popular_posts,
    }
    return render(request, 'main/home.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    latest_posts = Post.objects.order_by('-publish_date')[:3]

    context = {
        'post': post,
        'latest_posts': latest_posts,
    }
    return render(request, 'blog/post_detail.html', context)
