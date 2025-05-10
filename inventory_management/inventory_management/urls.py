from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import path,include,re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
    path('',include('inventory_management_app.urls')),
]
urlpatterns+=re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
urlpatterns+=re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),