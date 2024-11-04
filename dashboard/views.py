from django.http import HttpResponse
from django.shortcuts import render
import os
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from .models import Product  # Uygulama adınızı burada belirtin
from django.conf import settings
# Create your views here.
from django.shortcuts import render
from nltk.metrics import edit_distance
from fuzzywuzzy import fuzz

import nltk
from django.shortcuts import render
from .models import Product, Similar
from nltk.metrics import edit_distance
from nltk.tokenize import word_tokenize

# Ensure the Punkt tokenizer model is available
from django.shortcuts import render
from django.http import JsonResponse
from difflib import SequenceMatcher
from django.core.paginator import Paginator

def index(request):
    return render(request,'index.html')

def generate_common_entries(request):
    # Get all Market and Party products
    market_products = Product.objects.filter(page=Product.MARKET)
    party_products = Product.objects.filter(page=Product.PARTY)

    created_count = 0

    for market_product in market_products:
        for party_product in party_products:
            # Convert titles to lowercase for case-insensitive comparison
            market_title = market_product.title.lower()
            party_title = party_product.title.lower()

            # Calculate similarity
            similarity_ratio = SequenceMatcher(None, market_title, party_title).ratio()
            similarity_percentage = similarity_ratio * 100

            # Check if similarity is 50% or more
            if similarity_percentage >= 50:
                # Create a Common record without checking for existing records
                Similar.objects.create(
                    title_mark=market_product,
                    title_part=party_product,
                    ratio=similarity_percentage
                )
                created_count += 1

    # Return a JSON response with the result
    return JsonResponse({
        'status': 'success',
        'message': f'Generated {created_count} Common entries with >= 50% similarity.'
    })



# def calculate_similarity(str1, str2):
#     # Tokenize and lowercase both strings
#     tokens1 = [word.lower() for word in word_tokenize(str1)]
#     tokens2 = [word.lower() for word in word_tokenize(str2)]
    
#     # Join tokens back into strings for comparison
#     normalized_str1 = ' '.join(tokens1)
#     normalized_str2 = ' '.join(tokens2)
    
#     # Calculate edit distance similarity as a percentage
#     max_len = max(len(normalized_str1), len(normalized_str2))
#     distance = edit_distance(normalized_str1, normalized_str2)
#     similarity_ratio = (1 - distance / max_len) * 100
#     return similarity_ratio

def common(request):
    # Fetch "Market" and "Party" products from the database
    # urunler_a = Product.objects.filter(page='Market')
    # urunler_b = Product.objects.filter(page='Party')

    # # Clear previous matches (optional)
    # Common.objects.all().delete()

    # # Calculate similarity ratio and find matches
    # eslesen_urunler = []
    # for urun_a in urunler_a:
    #     for urun_b in urunler_b:
    #         # Use the calculate_similarity function
    #         benzerlik_orani = calculate_similarity(urun_a.title, urun_b.title)
    #         if benzerlik_orani >= 50:
    #             # Save matched products and their similarity ratio to the Common table
    #             common_entry = Common.objects.create(
    #                 title_mark=urun_a,
    #                 title_part=urun_b,
    #                 ratio=benzerlik_orani
    #             )
                
    #             # Prepare data for display in the template
    #             eslesen_urunler.append({
    #                 'urun_a': urun_a.title,
    #                 'urun_b': urun_b.title,
    #                 'oran': benzerlik_orani
    #             })

    # # Send matched products to the HTML template

  

    products_list = Similar.objects.all()
    
    
    paginator = Paginator(products_list, 10)  # Sayfa başına 10 ürün
    
    
    page_number = request.GET.get('page', 1)
    similars = paginator.get_page(page_number)
    return render(request, 'common.html', {"similars": similars})
    


def market(request):
    products_list = Product.objects.filter(page=Product.MARKET)
    
    
    paginator = Paginator(products_list, 10)  # Sayfa başına 10 ürün
    
    
    page_number = request.GET.get('page', 1)
    products = paginator.get_page(page_number)

    return render(request, 'market.html', {"products": products})


def party(request):
    products_list=Product.objects.filter(page=Product.PARTY)

    paginator = Paginator(products_list, 10)  # Sayfa başına 10 ürün
    
    
    page_number = request.GET.get('page', 1)
    products = paginator.get_page(page_number)

    return render(request, 'party.html',{"products":products})



# def common(request):
#     scraping('https://www.kbkmarket.com/bekarliga-veda-partisi')
#     return render(request, 'common.html')

def partyScraping():
    for sayi in range(0,102):
        url = 'https://www.partymarty.com.tr/kategori/parti-grubu?tp={sayi}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            product_divs = soup.find('div', class_='showcase-container').find('div', class_='row').find_all('div', class_='col-6')
            for div in product_divs:
                image=div.find('img', class_='lazyload')
                name=div.find('div', class_='showcase-content').find('div', class_='showcase-title').text
                price=div.find('div', class_='showcase-price').text
                
                if image:
                    img_url = 'https:'+image.get('src')
                    if img_url is not None:
                        img_response = requests.get(img_url)
                        if img_response.status_code == 200:
                # Yeni ürün oluştur
                            product = Product(
                            page=Product.PARTY,  # Örnek olarak 'Market' olarak ayarladık
                            title=name,
                            price=price
                            )
                            product.save()  # Önce nesneyi kaydetmek gerekli
                
                # Resmi kaydetmek için ImageField'ı kullan
                            product.image.save(os.path.basename(img_url), ContentFile(img_response.content), save=True)
                
                            print(f"Ürün kaydedildi: {name}, Resim: {img_url}")

                print(name.strip())
                print(price.strip())

def link(request):
    url = 'https://www.kbkmarket.com/milli-bayramlar'

# Sayfa içeriğini çek
    response = requests.get(url)

# Yanıt başarılıysa devam et
    if response.status_code == 200:
    # HTML içeriğini parse et
        soup = BeautifulSoup(response.content, 'html.parser')
        product_divs = soup.find_all('section', class_='landing-block')

        for div in product_divs:
            adres_list=div.find_all('div',class_='txcol-6')
            for link in adres_list:
                linka=link.find('a',class_='blokResimLink').get('href')
                scraping(linka)

    return HttpResponse("Merhaba, Django!")

def scraping(link):



    response = requests.get(link)


    if response.status_code == 200:

        soup = BeautifulSoup(response.content, 'html.parser')
    
    # Belirli ID'ye sahip div'i bul
        product_div = soup.find('div', id='ProductPageProductList')
    
    # Eğer bu ID'ye sahip bir div bulduysak
        if product_div:
        # Bu div içerisindeki tüm div'leri bul
            inner_divs = product_div.find_all('div',class_='ItemOrj')
        
        # Her bir iç div'i yazdır
            for div in inner_divs:

                name = div.find('div',class_='productItem').find('div',class_='productDetail').find('div',class_='productName')
                image=div.find('div',class_='productItem').find('div',class_='productImage').find('a',class_='detailLink').find('img',class_='resimOrginal')
                price=div.find('div',class_='productItem').find('div',class_='productDetail').find('div',class_='productPrice').find('div',class_='discountPrice').find('span',class_='discountPriceSpan')

            
                if image:
                    img_url = image.get('src')
                    if img_url is not None:
                        img_response = requests.get(img_url)
                        if img_response.status_code == 200:
                # Yeni ürün oluştur
                            product = Product(
                            page=Product.MARKET,  # Örnek olarak 'Market' olarak ayarladık
                            title=name.text,
                            price=price.text
                            )
                            product.save()  # Önce nesneyi kaydetmek gerekli
                
                # Resmi kaydetmek için ImageField'ı kullan
                            product.image.save(os.path.basename(img_url), ContentFile(img_response.content), save=True)
                
                            print(f"Ürün kaydedildi: {name}, Resim: {img_url}")

                print(name.text.strip())
                print(price.text.strip())




    
   
 



