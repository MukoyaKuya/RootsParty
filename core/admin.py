from django.contrib import admin
from .models import Leader, LeaderImage, ManifestoItem, ManifestoEvidence

class LeaderImageInline(admin.TabularInline):
    model = LeaderImage
    extra = 1

@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    inlines = [LeaderImageInline]

class EvidenceInline(admin.TabularInline):
    model = ManifestoEvidence
    extra = 1

@admin.register(ManifestoItem)
class ManifestoAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EvidenceInline]

from .models import GalleryPost, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    max_num = 7

@admin.register(GalleryPost)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    inlines = [PostImageInline]
