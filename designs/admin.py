from django.contrib import admin
from django.utils.html import format_html
from django.db.models import FloatField
from django.db.models.functions import Cast
from .models import Color, StoneSize, ScotchRoll, Design, DesignColor


class DesignColorInline(admin.TabularInline):
    model = DesignColor
    extra = 1
    fields = ['color', 'stone_count', 'stone_size']
    autocomplete_fields = ['color', 'stone_size']


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_thumbnail', 'skotch', 'skotch_length', 'mold_price_auto', 'total_stones', 'total_cost', 'created_at']
    list_filter = ['skotch', 'created_at']
    search_fields = ['name']
    inlines = [DesignColorInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'image', 'image_thumbnail')
        }),
        ('Scotch Roll Information', {
            'fields': ('skotch', 'skotch_length')
        }),
        ('Pricing', {
            'fields': ('mold_price_auto',)
        }),
    )
    readonly_fields = ['image_thumbnail', 'total_stones', 'total_stone_cost', 'total_skotch_cost', 'total_cost']

    class Media:
        js = ('designs/js/image_preview.js',)

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return 'No image'
    image_thumbnail.short_description = 'Preview'


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_thumbnail', 'created_at']
    search_fields = ['name']
    class Media:
        js = ('designs/js/image_preview.js',)

    def image_thumbnail(self, obj):
        if obj.label:
            return format_html('<img src="{}" width="100" height="20" />', obj.label.url)
        return 'No image'
    image_thumbnail.short_description = 'Image'


@admin.register(StoneSize)
class StoneSizeAdmin(admin.ModelAdmin):
    list_display = ['size', 'price', 'created_at']
    search_fields = ['size']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            size_num=Cast('size', FloatField())
        ).order_by('size_num')


@admin.register(ScotchRoll)
class ScotchRollAdmin(admin.ModelAdmin):
    list_display = ['width', 'price_per_meter', 'created_at']
    search_fields = ['width']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('width')
