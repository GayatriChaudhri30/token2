from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Product,OrderDetail
from django.contrib.auth.views import login_required
from django.views.generic import ListView,DetailView,TemplateView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator

from django.http.response import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
#import stripe


#STRIPE_PUBLISHABLE_KEY = getattr(settings, "STRIPE_PUBLISHABLE_KEY", None)

# # Create your views here 

def index(request):
    return HttpResponse("Hello World ")

#get request 
def products(request):
     products = Product.objects.all()
     
     product_name = request.GET.get('product_name')
     if product_name!='' and product_name is not None:
        page_obj=products.filter(name_icontains=product_name)
        
    
     paginator=Paginator(products,3)
     page_number= request.GET.get('page')
     page_obj = paginator.get_page(page_number)
     context={
        'page_obj':page_obj
        }
     return render(request,'myapp/index.html',context) 
## HttpResponse(products)

#class base view for above products view [Listview]
class ProductListView(ListView):
    template_name = "myapp/index.html"
    model = Product       
    context_object_name = 'products'
    paginate_by = 3

## HttpResponse(products)

def product_detail(request,id):
    product = Product.objects.get(id=id)
    context={
         'product':product#,
         #'stripe_publishable_key':settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request,'myapp/detail.html',context)
 
# class base view for about product detail view[Detailview]
class productDetailView(DetailView):
    model = Product
    template_name = 'myapp/detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'
    
    
    def get_context_data(self, **kwargs):
        context = super(productDetailView,self).get_context_data(**kwargs)
        context['stripe_publishable_key'] = getattr(settings, "STRIPE_PUBLISHABLE_KEY", None)
        return context
    
    

#post request 
@login_required 
def add_product(request):
    if request.method =='POST':
        name  = request.POST.get('name')
        price = request.POST.get('price')
        desc  = request.POST.get('desc')
        image = request.FILES['upload']
        seller_name = request.user
        product = Product(name=name,price=price,desc=desc,image=image,seller_name=seller_name)
        product.save()
    return render(request, 'myapp/addproduct.html')

# class based view for creating a product  
class ProductCreateView(CreateView):
    model = Product
    fields =['name','price','desc','image','seller_name']
    #product_form.html
    

def update_product(request,id):
    product = Product.objects.get(id=id)
    if request.method =='POST':
        product.name  = request.POST.get('name')
        product.price = request.POST.get('price')
        product.desc  = request.POST.get('desc')
        if bool(request.FILES.get('filepath', False)) == True:            
            product.image = request.FILES['upload']
        product.save()
        return redirect('/myapp/products')
    context={
        'product':product,
    }
    return render(request,'myapp/updateproduct.html',context)

class ProductUpdateView(UpdateView):
    model = Product
    fields =['name','price','desc','image','seller_name']
    template_name_suffix = '_update_form'
    
    
    
    
    
def delete_product(request,id):
    product = Product.objects.get(id=id)
    context={
        'product':product,
    }
    if request.method == 'POST':
        product.delete()
        return redirect('/myapp/products')
    return render(request,'myapp/delete.html',context) 

# class based delete view
class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('myapp:product')

def my_listings(request):
    product = Product.objects.filter(seller_name=request.user)
    context = {
        'products':product,
    }
    return render(request,'myapp/mylistings.html',context)


@csrf_exempt
def checkout_session(request,id):
    product = get_object_or_404(Product,pk=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session=stripe.checkout.Session.create(
        customer_email = request.user.email,
        payment_method_type=['card'],
        line_items=[
            {
                'pricedata':{
                    'currency':'usd',
                    'product_data':{
                        'name':product.name,
                    },
                    'unit_amount':int(product.price*100),
                },
                'quality':1,
            },
        ],
        mode='payment',
        success_url=request.build_absolute_url(reverse('myapp:success'))+"?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_url(
            reverse('myapp:failed')),
        
    )
    
    order = OrderDetail()
    order.username=request.user.user.maketrans()
    order.product = product
    order.stripe_payment_intent= checkout_session['payment_intent']
    order.amount = int(product.price*100)    
    order.save()
    return JsonResponse({'sessionId':checkout_session.id})

class PaymentSuccessView(TemplateView):
    template_name='myapp/payment_success.html'
    
    
    def get(self,request,*args,**kwargs):
        session_id= request.GET.get('session_id')
        if session_id is None:
            return HttpResponseNotFound()
        session = stripe.checkout.Session.retrive(session_id)
        order = get_object_or_404(OrderDetail,stripe_payment_intent=checkout_session['payment_intent'])
        order.has_paid = True
        order.save()
        return render(request,self.temmplate_name)

class PaymentFailedView(TemplateView):
          template_name= 'myapp/payment_failed.html'
          