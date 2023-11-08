from django.shortcuts import get_object_or_404,render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from django.db import models
from core.models import Node, Product
from core.serializers import NodeSerializer, NodeLiteSerializer, ProductSerializer
from core.permissions import IsActiveEmployeePermission
class BaseAPIView(APIView):
    permission_classes = [IsActiveEmployeePermission]
    authentication_classes = [TokenAuthentication]
    
    
class NodeListAPIView(BaseAPIView):
    def get(self, request):
        employee = request.user.employee
        nodes = Node.objects.filter(employees = employee)
        serializer = NodeLiteSerializer(nodes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Сохраняем объект и получаем созданный узел
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NodeDetailAPIView(BaseAPIView):
    def get(self, request, node_id):
        employee = request.user.employee
        node = get_object_or_404(Node, id=node_id,employees = employee)
        serializer = NodeLiteSerializer(node)
        return Response(serializer.data)

    def put(self, request, node_id):
        employee = request.user.employee
        node = get_object_or_404(Node, id=node_id,employees = employee)
        serializer = NodeSerializer(node, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except ValidationError as e:
                for error in e.error_dict:
                    messages.error(request, error)
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, node_id):
        employee = request.user.employee
        node = get_object_or_404(Node, id=node_id,employees= employee)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProductListAPIView(BaseAPIView):
    def get(self, request):
        employee = request.user.employee
        products = Product.objects.filter(node__employees = employee)
        employee = request.user.employee
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        node_id = request.data.get('node')
        employee = request.user.employee
        node = Node.objects.get(id=node_id,employee = employee)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(node=node)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailAPIView(BaseAPIView):
    def get(self, request, product_id):
        employee = request.user.employee
        product = get_object_or_404(Product, id=product_id,node__employees = employee)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, product_id):
        employee = request.user.employee
        product = get_object_or_404(Product, id=product_id, node__employees = employee)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        employee = request.user.employee
        product = get_object_or_404(Product, id=product_id, node__employees = employee)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClearDebtAPIView(BaseAPIView):
    def post(self, request):
        try:
            node_ids = request.data['node_ids']
            employee = request.user.employee
            nodes = Node.objects.filter(id__in=node_ids, employees=employee)
            nodes.update(debt=0)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KeyError:
            return Response({'error': 'Invalid request format'}, status=status.HTTP_400_BAD_REQUEST)

class CountryNodeListAPIView(BaseAPIView):
    def get(self, request, country):
        country = country.lower()
        employee = request.user.employee
        nodes = Node.objects.filter(employees=employee,contacts__address__country__iexact=country)
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)

class HighDebtNodesAPIView(BaseAPIView):
    def get(self, request):
        employee = request.user.employee
        average_debt = Node.objects.filter(employees=employee).aggregate(avg_debt=models.Avg('debt'))['avg_debt']
        nodes = Node.objects.filter(employees=employee,debt__gt=average_debt)
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)

class ProductNodesAPIView(BaseAPIView):
    def get(self, request, product_id):
        employee = request.user.employee
        nodes = Node.objects.filter(employees=employee,products__id=product_id)
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)



