import uuid
from django.db import models


class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    label = models.ImageField(upload_to='colors/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'


class StoneSize(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.size} - ${self.price} so'm"

    class Meta:
        verbose_name = 'Stone Size'
        verbose_name_plural = 'Stone Sizes'


class ScotchRoll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_meter = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.width}cm - ${self.price_per_meter}/m"

    class Meta:
        verbose_name = 'Scotch Roll'
        verbose_name_plural = 'Scotch Rolls'


class Design(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='designs/', blank=True, null=True)
    skotch = models.ForeignKey(ScotchRoll, on_delete=models.SET_NULL, null=True, blank=True, related_name='designs')
    skotch_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mold_price_auto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def total_stones(self):
        return sum(dc.stone_count for dc in self.colors.all())

    def total_stone_cost(self):
        total = 0
        for dc in self.colors.all():
            if dc.stone_size:
                total += dc.stone_count * dc.stone_size.price
        return total

    def total_skotch_cost(self):
        if self.skotch and self.skotch_length:
            return self.skotch_length * self.skotch.price_per_meter
        return 0

    def total_cost(self):
        stone_cost = self.total_stone_cost()
        skotch_cost = self.total_skotch_cost()
        mold_price = self.mold_price_auto or 0
        return stone_cost + skotch_cost + mold_price

    class Meta:
        verbose_name = 'Design'
        verbose_name_plural = 'Designs'
        ordering = ['-created_at']


class DesignColor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='colors')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    stone_count = models.IntegerField(default=0)
    stone_size = models.ForeignKey(StoneSize, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.design.name} - {self.color.name}"

    def total_cost(self):
        if self.stone_size:
            return self.stone_count * self.stone_size.price
        return 0

    class Meta:
        verbose_name = 'Design Color'
        verbose_name_plural = 'Design Colors'
        unique_together = ['design', 'color']
