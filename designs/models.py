import uuid
from django.db import models


class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    label = models.ImageField(upload_to='colors/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'


class StoneSize(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    size = models.CharField(max_length=50)
    glass_stone_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Shisha tosh narxi')
    plastic_stone_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Plastik tosh narxi')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.size}"

    class Meta:
        verbose_name = 'Stone Size'
        verbose_name_plural = 'Stone Sizes'


class MoldPrice(models.Model):
    """
    Qolip tortish narxi — global sozlama, faqat bitta yozuv bo'ladi.
    p1 = ranglar_soni * qolip_tortish_narxi
    """
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Qolip tortish narxi (bir rang uchun)')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Qolip tortish narxi: {self.price}'

    @classmethod
    def get_current(cls):
        """Hozirgi aktiv narxni qaytaradi (eng oxirgi yozuv)."""
        return cls.objects.order_by('-created_at').first()

    def save(self, *args, **kwargs):
        # Faqat bitta yozuv bo'lishi uchun — yangi saqlashda eskisini o'chirmaymiz,
        # lekin admin faqat bittasini ko'radi (get_current orqali).
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Mold Price'
        verbose_name_plural = 'Mold Price'
        ordering = ['-created_at']


class ScotchRoll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_meter = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.width}"

    class Meta:
        verbose_name = 'Scotch Roll'
        verbose_name_plural = 'Scotch Rolls'


class Design(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='designs/', blank=True, null=True)
    scotch = models.ForeignKey(ScotchRoll, on_delete=models.SET_NULL, null=True, blank=True, related_name='designs')
    scotch_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_printable = models.BooleanField(default=False, help_text='Chop etish')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def color_count(self):
        """Ranglar soni — qo'shilgan DesignColor yozuvlari soni."""
        return self.colors.count()

    def total_stones(self):
        return sum(dc.stone_count for dc in self.colors.all())

    def total_stone_cost(self, stone_type='glass'):
        """
        p2 = tosh_soni * tosh_narxi
        stone_type: 'glass' (shisha) yoki 'plastic' (plastik)
        Tosh kattaligi buyurtmada tanlanadi — bu yerda o'rtacha narx hisoblanadi.
        Agar StoneSize mavjud bo'lmasa 0 qaytaradi.
        """
        from designs.models import StoneSize
        sizes = StoneSize.objects.all()
        if not sizes.exists():
            return 0
        # O'rtacha tosh narxini ishlatamiz (yoki birinchi mavjud narxni)
        if stone_type == 'plastic':
            avg_price = sum(s.plastic_stone_price for s in sizes) / sizes.count()
        else:
            avg_price = sum(s.glass_stone_price for s in sizes) / sizes.count()
        return self.total_stones() * avg_price

    def total_scotch_cost(self):
        """p3 = skotch_uzunligi * skotch_metri_narxi / 100"""
        if self.scotch and self.scotch_length:
            return self.scotch_length * self.scotch.price_per_meter / 100
        return 0

    def total_mold_cost(self):
        """p1 = ranglar_soni * qolip_tortish_narxi"""
        mold = MoldPrice.get_current()
        if self.color_count and mold:
            return self.color_count * mold.price
        return 0

    def qolip_narxi(self, stone_type='glass'):
        """
        QOLIP_NARXI = p1 + p2 + p3
        p1 = ranglar_soni * qolip_tortish_narxi
        p2 = tosh_soni * tosh_narxi (stone_type ga qarab)
        p3 = skotch_uzunligi * skotch_metri_narxi / 100
        """
        return self.total_mold_cost() + self.total_stone_cost(stone_type) + self.total_scotch_cost()

    class Meta:
        verbose_name = 'Design'
        verbose_name_plural = 'Designs'
        ordering = ['-created_at']


class DesignColor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='colors')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    stone_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.design.name} - {self.color.name}"

    class Meta:
        verbose_name = 'Design Color'
        verbose_name_plural = 'Design Colors'
        unique_together = ['design', 'color']
