from django.core import exceptions
from rest_framework import serializers
from .models import Employee, Address, Contact, Product, Node
from datetime import date, datetime
def validate_product_name(value):
    if len(value) > 25:
        raise serializers.ValidationError("Product name length should not exceed 25 characters.")
    return value

def validate_node_name(value):
    if len(value) > 50:
        raise serializers.ValidationError("Node name length should not exceed 50 characters.")
    return value
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'city', 'street', 'house_number']

class ContactSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Contact
        fields = ['id', 'email', 'address']

class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    node_network = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'first_name', 'last_name', 'active', 'node_network']

class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[validate_product_name])
    nodes = serializers.PrimaryKeyRelatedField(many=True, queryset=Node.objects.all())
    release_date = serializers.DateField()

    def validate_release_date(self, value):
        try:
            return datetime.strptime(str(value), '%Y-%m-%d').date()
        except ValueError:
            raise serializers.ValidationError("Неверный формат даты. Используйте формат 'YYYY-MM-DD'.")
    class Meta:
        model = Product
        fields = ['id', 'nodes', 'name', 'model', 'release_date']


class NodeLiteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[validate_node_name])
    contacts = ContactSerializer()

    class Meta:
        model = Node
        fields = ['id', 'name', 'level', 'parent', 'debt', 'type', 'created_at','employees','products','contacts']
        read_only_fields = ['debt']
class NodeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[validate_node_name])
    parent = serializers.PrimaryKeyRelatedField(queryset=Node.objects.all(),allow_null=True)
    contacts = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), allow_null=True)

    class Meta:
        model = Node
        fields = ['id', 'name', 'level', 'parent', 'debt', 'type', 'created_at','employees','products','contacts']
        read_only_fields = ['debt']

    def validate(self,data):
        self.validatetype(data)
        self.validatehierarhy(data)
        self.validatesupplier(data)
        return data

    def validatetype(self, data):
        node_type = data.get('type')
        if not node_type:
            raise serializers.ValidationError("Необходимо выбрать тип.")
        if node_type == Node.FACTORY and int(data.get('debt', 0)) != 0:
            raise serializers.ValidationError("Задолженность для типа 'Завод' должна быть равна 0")
        return data

    def validatehierarhy(self, data):
        node_type = data.get('type')
        parent = data.get('parent')
        if parent:

            parent_level = Node.TYPE_LEVELS[parent.type]
            current_level = Node.TYPE_LEVELS[node_type]
            if parent_level >= current_level:
                raise serializers.ValidationError(
                    "Ошибка уровня иерархии. Порядок иерархии не может быть изменен.")
            last_parent = parent
            while last_parent.parent:
                print(last_parent)
                last_parent = last_parent.parent
                print(last_parent)
                if last_parent.type != Node.FACTORY:
                    raise serializers.ValidationError(
                    "Некорректный тип родительского узла. 'Завод' всегда 0 уровень иерархии.")
        if node_type == Node.FACTORY and parent:
            raise serializers.ValidationError("Тип 'Завод' не должен иметь поставщика.")
        return data

    def validatesupplier(self, data):
        node_type = data.get('type')
        parent = data.get('parent')
        if node_type != Node.FACTORY and not parent:
            raise serializers.ValidationError("Некорректный поставщик для этого типа элемента.\n"
                                              "Только тип 'Завод' может не иметь поставщика\n"
                                              "Попробуйте сперва создать узел с типом 'Завод'")
        if parent and parent.type == node_type:
            raise serializers.ValidationError(f"Узел типа '{dict(Node.TYPE_CHOICES).get(node_type)}' не может иметь поставщика с таким же типом.")
        return data
