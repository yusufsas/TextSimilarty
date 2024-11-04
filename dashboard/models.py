from django.db import models

# Create your models here.


class Product(models.Model):
    MARKET = 'Market'
    PARTY = 'Party'
    COMMON = 'Common'


    ROL_CHOICES = [
        (MARKET, 'Market'),
        (PARTY, 'Party'),
        (COMMON, 'Common'),
        
    ]
    id=models.AutoField(primary_key=True)
    page = models.CharField(max_length=20, choices=ROL_CHOICES)
    title = models.CharField(max_length=300)
    image=models.ImageField(upload_to="images",blank=True)
    price=models.CharField(max_length=100)
    created=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title


class Similar(models.Model):
    id = models.AutoField(primary_key=True)
    title_mark = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='market_product', limit_choices_to={'page': Product.MARKET})
    title_part = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='party_product', limit_choices_to={'page': Product.PARTY})
    ratio = models.DecimalField(max_digits=10, decimal_places=3, blank=True)

    
    def __str__(self):
        return f"{self.title_mark.title} - {self.title_part.title} ({self.ratio}%)"


