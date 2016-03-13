from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^placequery/?$', views.placequery, name='placequery'),
    url(r'^place/(\d+)', views.locationplace, name='locationplace')
]
