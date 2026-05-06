from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.db import models
from django.db.models import FloatField
from django.db.models.functions import Cast
from decimal import Decimal, InvalidOperation
from types import MethodType
from .models import Color, StoneSize, ScotchRoll, Design, DesignColor


DESIGN_LIST_PREVIEW_WIDTH = 100
DESIGN_FORM_PREVIEW_WIDTH = 420
DESIGN_FORM_PREVIEW_HEIGHT = 'auto'


MODEL_ADMIN_ORDER = {
    'designs': ['Design', 'Color', 'StoneSize', 'ScotchRoll'],
}


def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    app_list = sorted(app_dict.values(), key=lambda app: app['name'].lower())

    for app in app_list:
        model_order = MODEL_ADMIN_ORDER.get(app['app_label'])
        if model_order:
            order_map = {model_name: index for index, model_name in enumerate(model_order)}
            app['models'].sort(
                key=lambda model: (
                    order_map.get(model['object_name'], len(order_map)),
                    model['name'].lower(),
                )
            )
        else:
            app['models'].sort(key=lambda model: model['name'].lower())

    return app_list


admin.site.get_app_list = MethodType(get_app_list, admin.site)


def clean_number(value):
    if isinstance(value, str):
        return value.replace(' ', '')
    return value


def format_number(value, decimal_places=None):
    if value is None:
        return '-'

    if decimal_places is None:
        return f'{int(value):,}'.replace(',', ' ')

    try:
        value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return value
    return f'{value:,.{decimal_places}f}'.replace(',', ' ')


class SpacedDecimalInput(forms.TextInput):
    input_type = 'text'

    def __init__(self, attrs=None, decimal_places=2):
        attrs = attrs or {}
        attrs['class'] = f"{attrs.get('class', '')} spaced-number-input".strip()
        attrs['data-decimal-places'] = decimal_places
        super().__init__(attrs)
        self.decimal_places = decimal_places

    def format_value(self, value):
        value = clean_number(value)
        if value is None or value == '':
            return ''
        return format_number(value, self.decimal_places)


class SpacedIntegerInput(forms.TextInput):
    input_type = 'text'

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs['class'] = f"{attrs.get('class', '')} spaced-number-input".strip()
        attrs['data-decimal-places'] = 0
        super().__init__(attrs)

    def format_value(self, value):
        value = clean_number(value)
        if value is None or value == '':
            return ''
        return format_number(value)


class SpacedDecimalField(forms.DecimalField):
    def to_python(self, value):
        return super().to_python(clean_number(value))


class SpacedIntegerField(forms.IntegerField):
    def to_python(self, value):
        return super().to_python(clean_number(value))


class FormattedNumberAdminMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.DecimalField):
            kwargs['form_class'] = SpacedDecimalField
            kwargs['widget'] = SpacedDecimalInput(decimal_places=db_field.decimal_places)
        elif isinstance(db_field, models.IntegerField):
            kwargs['form_class'] = SpacedIntegerField
            kwargs['widget'] = SpacedIntegerInput()
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class ColorSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        color = getattr(value, 'instance', None)
        if color and color.label:
            option['attrs']['data-image-url'] = color.label.url
        return option


class DesignColorForm(forms.ModelForm):
    class Meta:
        model = DesignColor
        fields = '__all__'
        widgets = {
            'color': ColorSelect(attrs={'class': 'color-image-select'}),
        }


class DesignColorInline(FormattedNumberAdminMixin, admin.TabularInline):
    model = DesignColor
    form = DesignColorForm
    extra = 0
    fields = ['color', 'color_label_preview', 'stone_count', 'stone_size']
    readonly_fields = ['color_label_preview']

    class Media:
        css = {
            'all': ('designs/css/color_autocomplete.css',)
        }
        js = (
            'designs/js/color_autocomplete.js',
            'designs/js/number_format.js',
        )

    def color_label_preview(self, obj):
        if obj and obj.color and obj.color.label:
            return format_html(
                '<span class="color-label-preview"><img src="{}" width="206" height="56" /></span>',
                obj.color.label.url
            )
        return format_html('<span class="color-label-preview">No label</span>')
    color_label_preview.short_description = 'Label'


@admin.register(Design)
class DesignAdmin(FormattedNumberAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'image_list_preview', 'skotch', 'skotch_length_display', 'colors_count', 'total_stones', 'updated_at', 'created_at']
    inlines = [DesignColorInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'image', 'image_form_preview')
        }),
        ('Scotch Roll Information', {
            'fields': ('skotch', 'skotch_length')
        }),
    )
    readonly_fields = ['image_form_preview', 'colors_count', 'total_stones', 'total_stone_cost', 'total_skotch_cost']

    class Media:
        js = ('designs/js/image_preview.js', 'designs/js/number_format.js')

    def image_list_preview(self, obj):
        if obj.image:
            return format_html(
                '<span class="design-list-preview"><img src="{}" width="{}" height="auto" /></span>',
                obj.image.url,
                DESIGN_LIST_PREVIEW_WIDTH,
            )
        return format_html('<span class="design-list-preview">No image</span>')
    image_list_preview.short_description = 'Preview'

    def image_form_preview(self, obj):
        attrs = format_html(
            'id="image-preview" data-preview-width="{}" data-preview-height="{}"',
            DESIGN_FORM_PREVIEW_WIDTH,
            DESIGN_FORM_PREVIEW_HEIGHT,
        )
        if obj and obj.image:
            return format_html(
                '<span {}><img src="{}" style="max-width: {}px; max-height: {}px; width: auto; height: auto;" /></span>',
                attrs,
                obj.image.url,
                DESIGN_FORM_PREVIEW_WIDTH,
                DESIGN_FORM_PREVIEW_HEIGHT,
            )
        return format_html('<span {}>No image</span>', attrs)
    image_form_preview.short_description = 'Preview'

    def skotch_length_display(self, obj):
        return format_number(obj.skotch_length, 2)
    skotch_length_display.short_description = 'Skotch length'
    skotch_length_display.admin_order_field = 'skotch_length'

    def colors_count(self, obj):
        if not obj:
            return format_number(0)
        return format_number(obj.colors.count())
    colors_count.short_description = 'Colors'

    def total_stones(self, obj):
        if not obj:
            return format_number(0)
        return format_number(obj.total_stones())
    total_stones.short_description = 'Total stones'

    def total_stone_cost(self, obj):
        if not obj:
            return format_number(0, 2)
        return format_number(obj.total_stone_cost(), 2)
    total_stone_cost.short_description = 'Total stone cost'

    def total_skotch_cost(self, obj):
        if not obj:
            return format_number(0, 2)
        return format_number(obj.total_skotch_cost(), 2)
    total_skotch_cost.short_description = 'Total skotch cost'


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_thumbnail', 'updated_at', 'created_at']
    readonly_fields = ['label_preview']
    fields = ['name', 'label', 'label_preview']

    class Media:
        js = ('designs/js/image_preview.js',)

    def image_thumbnail(self, obj):
        if obj.label:
            return format_html('<img src="{}" width="100" height="20" />', obj.label.url)
        return 'No image'
    image_thumbnail.short_description = 'Label'

    def label_preview(self, obj):
        if obj.label:
            return format_html(
                '<span id="label-preview"><img src="{}" width="100" height="20" /></span>',
                obj.label.url
            )
        return format_html('<span id="label-preview">No label</span>')
    label_preview.short_description = 'Preview'


@admin.register(StoneSize)
class StoneSizeAdmin(FormattedNumberAdminMixin, admin.ModelAdmin):
    list_display = ['size', 'price_display', 'updated_at', 'created_at']

    class Media:
        js = ('designs/js/number_format.js',)

    def price_display(self, obj):
        return format_number(obj.price, 2)
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            size_num=Cast('size', FloatField())
        ).order_by('size_num')


@admin.register(ScotchRoll)
class ScotchRollAdmin(FormattedNumberAdminMixin, admin.ModelAdmin):
    list_display = ['width_display', 'price_per_meter_display', 'updated_at', 'created_at']

    class Media:
        js = ('designs/js/number_format.js',)

    def width_display(self, obj):
        return format_number(obj.width, 2)
    width_display.short_description = 'Width'
    width_display.admin_order_field = 'width'

    def price_per_meter_display(self, obj):
        return format_number(obj.price_per_meter, 2)
    price_per_meter_display.short_description = 'Price per meter'
    price_per_meter_display.admin_order_field = 'price_per_meter'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('width')
