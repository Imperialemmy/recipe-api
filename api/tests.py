from django.test import TestCase
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from app.models import Order, CustomUser, Product,OrderItem

@pytest.mark.django_db
def test_create_order():
    client = APIClient()
    user = CustomUser.objects.create_user(username='testuser', password='testpass')
    client.force_authenticate(user=user)
    url = reverse('order-list')
    data = {}
    response = client.post(url, data, format='json')
    assert response.status_code == 201
    assert Order.objects.count() == 1
    assert Order.objects.get().user == user


# Test for creating a product
@pytest.mark.django_db
def test_create_product():
    client = APIClient()
    url = reverse('product-list')
    data = {
        'name': 'Test Product',
        'description': 'Test Description',
        'price': '10.00'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 201
    assert Product.objects.count() == 1
    assert Product.objects.get().name == 'Test Product'


@pytest.mark.django_db
def test_create_order_item():
    client = APIClient()
    user = CustomUser.objects.create_user(username='testuser', password='testpass')
    client.force_authenticate(user=user)
    product = Product.objects.create(name='Test Product', description='Test Description', price='10.00')
    order = Order.objects.create(user=user)
    url = reverse('orderitem-list')
    data = {
        'order': order.id,
        'product': product.id,
        'quantity': 2,
        'price': '10.00'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 201
    assert OrderItem.objects.count() == 1
    assert OrderItem.objects.get().order == order
    assert OrderItem.objects.get().product == product