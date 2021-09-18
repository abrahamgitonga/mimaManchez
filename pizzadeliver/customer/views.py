import json
from .models import MenuItem, OrderModel, Category
from django.shortcuts import redirect, render
from django.views import View
from django.core.mail import send_mail


# Create your views here.
class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request,'customer/index.html')

class About(View):
    def get(self, request, *args, **kwargs):
        return render(request,'customer/about.html')


class Order(View):
    def get(self, request, *args, **kwargs):
        #get item from each category

        appetizers = MenuItem.objects.filter(category__name__contains='Appetizer')
        drinks = MenuItem.objects.filter(category__name__contains='Drinks')
        pizzas = MenuItem.objects.filter(category__name__contains='Pizza')
        desserts = MenuItem.objects.filter(category__name__contains='Dessert')

        #pass into context

        context = {
            'appetizers':appetizers,
            'drinks':drinks,
            'pizzas':pizzas,
            'desserts':desserts

        }

        #render the template

        return render(request, 'customer/order.html', context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        street = request.POST.get('street')
        county = request.POST.get('county')
        town = request.POST.get('town')
        zip_code = request.POST.get('zip_code')

        order_items = {
            'items':[]
        }    
        items = request.POST.getlist('items[]')

        for item in items:
            menu_item = MenuItem.objects.get(pk__contains=int(item))
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price
            }

            order_items['items'].append(item_data)
            price = 0
            item_ids = []

        for item in order_items['items']:
            price += item['price'] 
            item_ids.append(item['id'])

            order = OrderModel.objects.create(
                price=price,
                name=name,
                email=email,
                street=street,
                county=county,
                town=town,
                zip_code=zip_code
                )
            order.items.add(*item_ids)

            #send confirmation email to user

            body = ('Thankyou for your order! Your order is being processed and will be delivered soon!\n'
                f'Your Total: {price}\n'
                'Thankyou again for your order!')


            send_mail(
                'Thankyou for your order!',
                body,
                'example@example.com',
                [email],
                fail_silently=False
            )

            context = {
                'items': order_items['items'],
                'price': price
            }   

            return redirect('order-confirmation',pk=order.pk)


class OrderConfirmation(View):
    def get(self, request,pk, *args, **kwargs):
        order = OrderModel.objects.get(pk=pk)

        context = {
            'pk': order.pk,
            'items': order.items,
            'price': order.price,
        }


        return render(request, 'customer/order_confirmation.html', context)


    def post(self, request,pk, *args, **kwargs):

        data = json.loads(request.body)

        if data['isPaid']:
            order = OrderModel.objects.get(pk=pk)
            order.is_paid = True
            order.save()
        return  redirect('payment-confirmation')    



class OrderPayConfirmation(View):
    def get(self, request, *args, **kwargs):

        return render(request, 'customer/order_pay_confirmation.html')
