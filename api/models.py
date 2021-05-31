from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Абстрактный базовый клас
class CommonInfo(models.Model):
    """
    Абстрактный базовый клас
    """
    class Meta:
        abstract = True

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)


# Модель для выбора статуса заказа
class OrderStatusChoices(models.TextChoices):
    """
    Модель для поля status в моделе Order
    """
    NEW = "NEW", "Новый"
    IN_PROGRESS = "IN_PROGRESS", "В обработке"
    DONE = "DONE", "Завершен"


# Товар
class Product(CommonInfo):
    """
    Модель для товаров
    """
    def __str__(self):
        return f"id: {self.id}  name: {self.name}"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["id"]

    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    price = models.FloatField(validators=[MinValueValidator(0)])


# Отзыв к товару
class ProductReview(CommonInfo):
    """
    Модель для отзывов
    """
    def __str__(self):
        return f"id: {self.id}  author: {self.user}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-updated_at", "-created_at"]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


# Заказы
class Order(CommonInfo):
    """
    Модель для заказов
    """

    def __str__(self):
        return f"id: {self.id} user: {self.user} status: {self.status} positions: {len(self.positions.all())}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-updated_at', '-created_at']

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user', on_delete=models.DO_NOTHING)
    products = models.ManyToManyField(Product, through='ProductOrder')
    status = models.CharField(max_length=20, choices=OrderStatusChoices.choices, default=OrderStatusChoices.NEW)
    order_sum = models.FloatField(validators=[MinValueValidator(0)])


# Подборки
class Collection(CommonInfo):
    """
    Модель для подборок товаров
    """

    def __str__(self):
        return f'id: {self.id} title: {self.title}'

    class Meta:
        verbose_name = 'Подборка'
        verbose_name_plural = 'Подборки'
        ordering = ['-updated_at', '-created_at']

    title = models.CharField(max_length=100, blank=False)
    text = models.TextField()
    products = models.ManyToManyField(Product, through='ProductCollection')


# Модели для создания связей многие-ко-многим
class ProductOrder(models.Model):
    """
    Модель для связи многие-ко-многим Product и Order
    """

    class Meta:
        db_table = 'api_product_order'

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='positions', on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(1)])


class ProductCollection(models.Model):
    """
    Модель для связи многие-ко-многим Product и Collection
    """

    class Meta:
        db_table = 'api_product_collections'

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, related_name='products_list', on_delete=models.CASCADE)


# Избранные
class Favorites(models.Model):
    product = models.ForeignKey(Product, related_name='product', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
