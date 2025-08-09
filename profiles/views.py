from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import ShoppingCartItem
from mainpage.models import Product
from routine.views import find_step_products, routine_generator
from routine.models import RoutinePlan
from quiz.models import SkinProfile

PLAN_NAMES = {
    'full': 'برنامه‌ی کامل (اگه سلامت پوستت خیلی برات مهمه)',
    'hydration': '',
    'minimalist': ''
}

@login_required
def profile_view(request):
    user = request.user
    profile = user.userprofile
    cart_items = ShoppingCartItem.objects.filter(user=user).select_related('product')
    if cart_items:
        total_shoppingcart_price = sum([item.total_price() for item in cart_items])
    else:
        total_shoppingcart_price = 0
    plans = []
    steps = None
    # try:
    #     routine_plans = RoutinePlan.objects.filter(user=user)
    #     steps = None
    #     for routine_plan in routine_plans:
    #         steps = find_step_products(user=user, name=routine_plan.plan_name)
    #         plans.append((routine_plan.plan_name, steps))
    # except:
    #     pass
    routine_plans = RoutinePlan.objects.filter(user=user)
    steps = None
    for routine_plan in routine_plans:
        steps = find_step_products(request, name=routine_plan.plan_name)
        plans.append((PLAN_NAMES[routine_plan.plan_name], steps))

    # if RoutinePlan.objects.filter(user=user).exists():
    #     steps = find_step_products(user.skinprofile)
    # elif SkinProfile.objects.get(user=user).quiz_completed:
    #     routine_generator(request)
    #     steps = find_step_products(user.skinprofile)

    context = {
        # 'steps': steps,
        'plans': plans,
        'cart_items': cart_items,
        'total_shoppingcart_price': total_shoppingcart_price,
        'quiz_completed': user.skinprofile.quiz_completed
    }
    return render(request, 'profiles/profile.html', context)

@login_required
def profile_edit(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if 'remove_picture' in request.POST:
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.profile_picture = None

            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profiles/profile_edit.html', {'form': form})    

from accounts.models import ProductSearchHistory
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if not ProductSearchHistory.objects.filter(user=request.user, product=product, interaction_type='cart').exists():
        ProductSearchHistory.objects.create(user=request.user, product=product, interaction_type='cart')
    cart_item, created = ShoppingCartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('product_detail', pk=product_id)


@login_required
def decrease_cart_item(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item = ShoppingCartItem.objects.filter(user=request.user, product=product).first()
    
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            try:
                interaction = ProductSearchHistory.objects.get(user=request.user, product=product, interaction_type='cart')
                interaction.delete()
            except:
                pass
    return redirect('profile')

@login_required
def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    ShoppingCartItem.objects.filter(user=request.user, product=product).delete()
    try:
        interaction = ProductSearchHistory.objects.get(user=request.user, product=product, interaction_type='cart')
        interaction.delete()
    except:
        pass
    return redirect('profile')

@login_required
def buy_products(request):
    if request.method == 'POST':
        cart_items = ShoppingCartItem.objects.filter(user=request.user)

        for item in cart_items:
            product = item.product
            product.sales_count += item.quantity
            ProductSearchHistory.objects.create(user=request.user, product=product, interaction_type='purchase')
            product.save()
        cart_items.delete()

        return redirect('profile')