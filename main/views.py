from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Avg
from .forms import UserRegisterForm, UserLoginForm, ReviewForm
from .models import Category, Product, Order, OrderItem, Customer, Review

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                Customer.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'main/profile.html')

def home(request):
    categories = Category.objects.all()
    return render(request, 'main/home.html', {'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.all()

    for product in products:
        product.average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'main/category_detail.html', {'category': category, 'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.customer = request.user.get_customer()
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'main/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'form': form,
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = request.user.get_customer()
    order, created = Order.objects.get_or_create(customer=customer, is_paid=False)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        if created:
            order_item.quantity = quantity
        else:
            order_item.quantity += quantity
        order_item.price = product.price * order_item.quantity
        order_item.save()

        messages.success(request, 'Product added to cart')
        return redirect('cart')

    return redirect('product_detail', product_id=product.id)

@login_required
def update_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = request.user.get_customer()
    order = get_object_or_404(Order, customer=customer, is_paid=False)
    order_item = get_object_or_404(OrderItem, order=order, product=product)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        if quantity > 0:
            order_item.quantity = quantity
            order_item.price = product.price * quantity
            order_item.save()
        else:
            order_item.delete()

    return redirect('cart')

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = request.user.get_customer()
    order = get_object_or_404(Order, customer=customer, is_paid=False)
    order_item = get_object_or_404(OrderItem, order=order, product=product)

    if request.method == 'POST':
        order_item.delete()
        
    return redirect('cart')

@login_required
def cart(request):
    order = get_object_or_404(Order, customer=request.user.customer, is_paid=False)
    return render(request, 'main/cart.html', {'order': order})
