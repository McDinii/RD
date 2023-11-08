from django.db import models
from django.db.models import Max
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.core.validators import ValidationError
from django.contrib.auth.models import User



class Node(MPTTModel):
    FACTORY = "factory"
    DISTRIBUTOR = "distributor"
    DEALER = "dealer"
    BIG_RETAIL = "big_retail"
    INDIVIDUAL = "individual"

    TYPE_LEVELS = {
        FACTORY: 0,
        DISTRIBUTOR: 1,
        DEALER: 2,
        BIG_RETAIL: 3,
        INDIVIDUAL: 4,
    }

    TYPE_CHOICES = [
        (FACTORY, "Завод"),
        (DISTRIBUTOR, "Дистрибьютор"),
        (DEALER, "Дилерский центр"),
        (BIG_RETAIL, "Крупная розничная сеть"),
        (INDIVIDUAL, "Индивидуальный предприниматель"),
    ]

    name = models.CharField(max_length=200, verbose_name="Название")
    # contacts = models.ForeignKey('Contact', on_delete=models.SET_NULL, null=True, verbose_name="Контакты")
    # employees = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, verbose_name="Сотрудники")
    # products = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, verbose_name="Продукты")
    type = models.CharField(choices=TYPE_CHOICES,
                            max_length=50,
                            verbose_name="Тип")
    level = models.IntegerField(verbose_name="Уровень иеррархии", editable=False)
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='dependent',
                            verbose_name="Поставщик")
    debt = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Задолженность", default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        type_label = dict(self.TYPE_CHOICES).get(self.type)
        return f"{type_label}: {self.name} (уровень:{self.level})"

    def clean(self):
        if not self.name:
            raise ValidationError("Необходимо задать имя.")
        if not self.type:
            raise ValidationError("Необходимо выбрать тип.")
        if self.type == Node.FACTORY and self.debt != 0:
            raise ValidationError("Задолженность для типа 'Завод' должна быть равна 0.")
        if self.type != Node.FACTORY and not self.parent:
            raise ValidationError("Некорректный поставщик для этого типа элемента.\n"
                                  "Только тип 'Завод' может не иметь поставищка\n"
                                  "Попробуйте сперва создать узел с типом 'Завод'")
        if self.parent and self.parent.type == self.type:
            raise ValidationError(f"Узел типа '{self.get_type_display()}' не может иметь поставщика с таким же типом.")
        if self.parent:
            parent_level = self.TYPE_LEVELS[self.parent.type]
            current_level = self.TYPE_LEVELS[self.type]
            if parent_level >= current_level:
                raise ValidationError(
                    "Ошибка уровня иерархии. Порядок иерархии не может быть изменен.")
        if self.parent:
            last_parent = self.parent
            while last_parent.parent:
                last_parent = last_parent.parent

            if last_parent.type != Node.FACTORY:
                raise ValidationError(
                    "Некорректный тип родительского узла. 'Завод' всегда 0 уровень иерархии.")
        if self.type == Node.FACTORY and self.parent:
            raise ValidationError("Тип 'Завод' не должен иметь поставщика.")


        super().clean()

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=200, verbose_name="Имя")
    last_name = models.CharField(max_length=200, verbose_name="Фамилия")
    active = models.BooleanField(default=True, verbose_name="Активный")
    # node_network = models.OneToOneField('Node', on_delete=models.CASCADE, related_name='employee', null=True,
    #                                     blank=True)
    node_network = models.ForeignKey(Node, on_delete=models.CASCADE, null=False, related_name="employees")

    def __str__(self):
        return f"{self.first_name} {self.last_name} Работает на: {self.node_network}"

class Address(models.Model):
    country = models.CharField(max_length=200, verbose_name="Страна")
    city = models.CharField(max_length=200, verbose_name="Город")
    street = models.CharField(max_length=200, verbose_name="Улица")
    house_number = models.CharField(max_length=20, verbose_name="Номер дома")
    def __str__(self):
        return f"Адрес: {self.country}, г. {self.city}, ул.{self.street}, {self.house_number}"

class Contact(models.Model):
    email = models.EmailField(max_length=200, verbose_name="Электронная почта")
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, verbose_name="Адрес")
    node  = models.OneToOneField(Node, on_delete=models.CASCADE, null=False, related_name='contacts')
    def __str__(self):
        return f"E-mail: {self.email}, {self.address} – {self.node}"

class Product(models.Model):
    nodes = models.ManyToManyField(Node,
                             related_name='products')
    name = models.CharField(max_length=200, verbose_name="Название")
    model = models.CharField(max_length=200, verbose_name="Модель")
    release_date = models.DateField(verbose_name="Дата выхода продукта на рынок")

    def __str__(self):
        # made_by = self.node.parent
        # if made_by is not None:
        #     while made_by.parent:
        #         made_by = made_by.parent
        # else:
        #     made_by = self.node
        return f"Название: {self.name} Модель: {self.model}" # , сделано на {made_by}
