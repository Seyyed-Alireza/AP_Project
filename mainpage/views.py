# from django.shortcuts import render

# def mainpage(request):
#     return render(request, 'mainpage/mainpage.html')



# for test
from django.shortcuts import render

def mainpage(request):
    products = [
        {'name': 'کرم مرطوب‌کننده', 'price': '120,000 تومان', 'image': 'images/product1.jpg'},
        {'name': 'ضدآفتاب قوی', 'price': '180,000 تومان', 'image': 'images/product2.jpg'},
        {'name': 'کرم شب', 'price': '150,000 تومان', 'image': 'images/product3.jpg'},
    ]
    return render(request, 'mainpage/mainpage.html', {'products': products})

