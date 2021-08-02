from django.template.defaulttags import register
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from main.models import PurchaseType, Purchase, Recurring, Shop, InterPayment, Paycheck
from django.contrib.auth.decorators import login_required
from datetime import date

# graphing libs
from plotly.offline import plot
from plotly.graph_objs import Bar


def splash(request):
    if request.user.is_authenticated:
        types = PurchaseType.objects.all()
        shops = Shop.objects.all()
        return render(request, 'home.html', {'user': request.user, 'purchase_types': types, 'shops': shops})
    return render(request, "splash.html", {})


def purchases_between(start_date, end_date, username=None):
    '''
    retrieve all purchases made between [start_date, ..., end_date] inclusive.
    returns tuple (purchase_type_purchases, shop_purchases) where each is a dictionary
    from type / shop -> [purchase list]
    '''
    types = PurchaseType.objects.all()
    shops = Shop.objects.all()

    if (username):
        user = User.objects.get(username=username)

    # group purchaes by shop / type within date range purchased by username
    if username:
        purchase_type_purchases = {purchase_type: purchase_type.purchases.filter(
            date__range=[start_date, end_date], purchased_by=user) for purchase_type in types}
        shop_purchases = {shop: shop.purchases.filter(
            date__range=[start_date, end_date], purchased_by=user) for shop in shops}
    else:
        purchase_type_purchases = {purchase_type: purchase_type.purchases.filter(
            date__range=[start_date, end_date]) for purchase_type in types}
        shop_purchases = {shop: shop.purchases.filter(
            date__range=[start_date, end_date]) for shop in shops}

    all_purchases = []
    for purchases in shop_purchases.values():
        all_purchases += purchases

    return (all_purchases, purchase_type_purchases, shop_purchases)


def purchases_for_breakdown(purchases):
    '''
    For a list of purchase objects, return a tuple ($michael only, $michelle only, $both, $total)
    breaking down what portion of purchases were purchased for who
    '''
    total = sum([purchase.total_price() for purchase in purchases])
    just_michael = sum(
        [purchase.total_price() for purchase in purchases if purchase.bought_for == 'MICHAEL'])
    just_michelle = sum(
        [purchase.total_price() for purchase in purchases if purchase.bought_for == 'MICHELLE'])
    both = total - (just_michael + just_michelle)
    return (just_michael, just_michelle, both, total)


def stat_date_range_helper(request):
    start_date, end_date = date(2021, 7, 1), date.today()
    if 'start_date' in request.GET and request.GET['start_date']:
        start_date = request.GET['start_date']
    if 'end_date' in request.GET and request.GET['end_date']:
        end_date = request.GET['end_date']
    return (start_date, end_date)


def calc_grouped_sum_prices(purchases):
    grouped_sum_prices = dict()
    for grouping, purchases in purchases.items():
        grouped_sum_prices[grouping] = sum(
            [purchase.total_price() for purchase in purchases])
    return grouped_sum_prices


def generate_plot(type_sum_prices):
    # https://plotly.com/
    x = [purchase_type.type for purchase_type in type_sum_prices.keys()]
    y = [float(val) for val in type_sum_prices.values()]
    plot_div = plot([Bar(x=x, y=y)], output_type='div')
    return plot_div


def helper_stats_common(request, username):
    if request.user.is_authenticated:
        start_date, end_date = stat_date_range_helper(request)
        all_purchases, purchase_type_purchases, shop_purchases = purchases_between(
            start_date, end_date, request.user if username else None)

        type_sum_prices, shop_sum_prices = calc_grouped_sum_prices(
            purchase_type_purchases), calc_grouped_sum_prices(shop_purchases)

        for_michael, for_michelle, for_both, total = purchases_for_breakdown(
            all_purchases)

        type_plot_div = generate_plot(type_sum_prices)
        x_shop = [shop.name for shop in shop_sum_prices.keys()]
        y_shop = [float(val) for val in shop_sum_prices.values()]
        shop_plot_div = plot([Bar(x=x_shop, y=y_shop)], output_type='div')

        return render(request, 'stats.html', {'is_joint': False if username else True,
                                              'purchase_type_purchases': purchase_type_purchases,
                                              'shop_purchases': shop_purchases,
                                              'type_sum_prices': type_sum_prices,
                                              'shop_sum_prices': shop_sum_prices,
                                              'start_date': start_date,
                                              'end_date': end_date,
                                              'for_michael': for_michael,
                                              'for_michelle': for_michelle,
                                              'for_both': for_both,
                                              'total': total,
                                              'user': request.user,
                                              'type_bar_chart': type_plot_div,
                                              'shop_bar_chart': shop_plot_div})


def joint_stats(request):
    return helper_stats_common(request, None)


def stats(request):
    return helper_stats_common(request, request.user)


def login_(request):
    if request.method == "POST":
        print("LOGGING IN")
        user = authenticate(username=request.POST.get(
            'username'), password=request.POST.get('password'))
        print(user)
        if user is not None:
            print("LOGGED IN")
            login(request, user)
            return redirect("/")
        print("COULD NOT FIND USER")
    return render(request, "login.html", {})


def logout_(request):
    logout(request)
    return redirect("/")


@login_required
def add_recurring(request):
    if request.method == 'POST':
        recurring = Recurring.objects.create(
            price=request.POST['price'],
            shop=Shop.objects.get(name=request.POST['shop']),
            description=request.POST['description'],
            bought_for=request.POST['for_choices'],
            purchased_by=User.objects.get(username=request.user),
            frequency=request.POST['frequency']
        )
        recurring.save()
    return redirect('/')


@login_required
def add_purchase(request):
    if request.method == 'POST':
        purchase_type = request.POST.getlist("type_choices")[0]
        purchase_type_obj = PurchaseType.objects.get(type=purchase_type)
        
        # if amount is null default to 1
        amount = request.POST['amount'] if request.POST['amount'] else 1
        dt = request.POST['date'] if request.POST['date'] else date.today()

        purchase = Purchase.objects.create(
            price=request.POST['price'],
            shop=Shop.objects.get(name=request.POST['shop']),
            date=dt,
            description=request.POST['description'],
            amount=amount,
            bought_for=request.POST['for_choices'],
            purchase_type=purchase_type_obj,
            purchased_by=User.objects.get(username=request.user)
        )

        purchase.save()
        return redirect('/')
    else:
        return redirect('/')

@login_required
def add_inter_payment(request):
    if request.method == 'POST':
        # get user objects
        from_user = User.objects.get(username=request.user)
        to_user = None
        if (from_user.first_name.lower() == 'michelle'):
            to_user = User.objects.get(username='michael')
        else:
            to_user = User.objects.get(username='michelle')

        # create and save obj
        inter_payment = InterPayment.objects.create(
            price=request.POST['price'],
            from_user=from_user,
            to_user=to_user,
            payment_for=request.POST['payment_for'],
            date = request.POST['date'] if request.POST['date'] else date.today()
        )
        inter_payment.save()
    return redirect ('/')

@login_required
def add_paycheck(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        amount = request.POST['amount']
        dt = request.POST['date'] if request.POST['date'] else date.today()

        paycheck = Paycheck.objects.create(
            amount = amount,
            user = user,
            date = dt
        )
        paycheck.save()
    return redirect('/')


@login_required
def new_purchase_type(request):
    if request.method == 'POST':
        if request.POST['type']:
            new_type = PurchaseType.objects.create(type=request.POST['type'])
            new_type.save()
    return redirect('/')


@login_required
def new_shop(request):
    if request.method == 'POST':
        if request.POST['shop']:
            new_shop = Shop.objects.create(name=request.POST['shop'])
            new_shop.save()
    return redirect('/')


# django filter shit


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
