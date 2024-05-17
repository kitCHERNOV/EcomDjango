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
    wallet, created = Wallet.objects.get_or_create(user=request.user,defaults={'debit':10000.00,'credit':1000.00})
    waldebit = wallet.debit
    walcredit = wallet.credit

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'debit':waldebit, 'credit':walcredit}
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
        # wallet, created = Wallet.objects.get_or_create(user=request.user,
        #                                                defaults={
        #                                                    'debit':10000.00,
        #                                                    'credit':1000.00
        #                                                })
        # print(wallet.debit)
        # total = float(data['form']['total'])
        # wallet.debit -= total
        # print(wallet.debit)
        # wallet.reset_funds()

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

        return JsonResponse('Payment complete!', safe=False)
    else:
        return JsonResponse('Not enough funds in wallet', safe=False)
# Create your views here.


def signup(request):

    if request.POST:
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        # Создайте пользователя и сохраните его в базе данных
        user = User.objects.create_user(username=username, email=email, password=password)



        # user = authenticate(request, username=username, password=password)
        if user is not None:
        #     djlogin(request, user=user)
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

def LogoutView(request):
    logout(request)

    return redirect('store')


