
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import HomeVideo, BlogPost

print("--- HOME VIDEO ---")
video = HomeVideo.objects.filter(is_active=True).first()
if video:
    print(f"Title: {video.title}")
    print(f"Thumbnail (DB): {video.thumbnail}")
    print(f"Video File (DB): {video.video_file}")
    print(f"Video URL (DB): {video.video_url}")
    
    if video.thumbnail and not os.path.exists(video.thumbnail.path):
        print(f"MISSING THUMBNAIL FILE: {video.thumbnail.path}")
    else:
        print(f"Thumbnail file exists: {video.thumbnail.path if video.thumbnail else 'None'}")

    if video.video_file and not os.path.exists(video.video_file.path):
        print(f"MISSING VIDEO FILE: {video.video_file.path}")
    else:
        print(f"Video file exists: {video.video_file.path if video.video_file else 'None'}")
else:
    print("No active video found.")

print("\n--- NEWS POSTS ---")
posts = BlogPost.objects.filter(is_published=True)[:5]
for p in posts:
    print(f"Post: {p.title} (Category: {p.category})")
