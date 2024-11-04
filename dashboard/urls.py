
from django.contrib import admin
from django.urls import path
from .views import common, party, market,scraping,link,generate_common_entries,index


urlpatterns = [
    path('market/', market, name='market'),
    path('party/', party, name='party'),
    path('common/', common, name='common'),
    path('', index, name='index'),
    path('scraping/', link, name='link'),
     
     
      path('generate-common/', generate_common_entries, name='generate_common_entries'), # New URL added here
  
    

]