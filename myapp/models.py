from django.db import models
#from django.db import Model
from django.forms import forms
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.
class Product(models.Model):
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('myapp:products')
    
    #user = models.OneToOneField(User,on_delete=models.CASCADE)
    seller_name = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    name = models.CharField(max_length=1000)
    price =models.IntegerField()
    desc = models.CharField(max_length=2000)
    image =models.ImageField(blank=True,upload_to='static/myapp/images')



class OrderDetail(models.Model):
    customer_username = models.CharField(max_length=200)
    product = models.ForeignKey(to='Product',on_delete=models.PROTECT)
    amounr = models.IntegerField()
    stripe_payment_intent = models.CharField(max_length=200)
    has_paid=models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    update_on= models.DateTimeField(auto_now_add=True)
    
    
    
    
    
    
    