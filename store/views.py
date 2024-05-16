from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as djlogin
from django.contrib.auth.models import User

def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products':products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


# First that we want create is a print our data
# Скорее всего данные подгружаются из какого то общего пакета приложения
def updateItem(request):
    data = json.loads(request.body) # запрс точечных данных
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)


    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)


    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

#from django.views.decorators.csrf import csrf_exempt
#@csrf_exempt
# Это пропуск отправки файлов на сервер, т.к. это может не работать внутри режима инкогнито
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)


    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)
# Create your views here.


def signup(request):

    if request.POST:
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        # Создайте пользователя и сохраните его в базе данных
        user = User.objects.create_user(username, email, password)



        # user = authenticate(request, username=username, password=password)
        if user is not None:
            djlogin(request, user=user)
            return redirect('store') # отправит нас на главную страницу
    return render(request, 'store/signup.html')

# def login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)  # Проверяем аутентификацию пользователя
#         if user is not None:
#             djlogin(request, user)  # Аутентифицируем пользователя
#             # После успешной аутентификации, выполните необходимые действия, например, перенаправление на другую страницу
#             return redirect('home')  # Замените 'home' на имя вашего URL-шаблона
#         else:
#             # Если аутентификация не удалась, покажите сообщение об ошибке или форму для повторной попытки входа
#             return render(request, 'login.html', {'error_message': 'Invalid username or password'})
#     else:
#         # Если запрос не является POST, отобразите форму входа
#         return render(request, 'login.html')

def login(request):

    if request.POST:
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            djlogin(request, user=user)
            return redirect('store') # отправит нас на главную страницу
    return render(request, 'store/login.html')

# class Login(DataMixin, LoginView):
#     form_class = LoginUserForm
#     template_name = 'women/login.html'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         c_def = self.get_user_context(title="Авторизация")
#         return dict(list(context.items()) + list(c_def.items()))
#
#     def get_success_url(self):
#         return reverse_lazy('home')


# def logout(request):
#     logout(request)
#     return redirect('login')

# def logout(request):
#     logout(request)
#     return redirect('home')  # перенаправить на вашу домашнюю страницу