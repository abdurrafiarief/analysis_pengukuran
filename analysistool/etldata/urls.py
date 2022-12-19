from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home_page, name='index'),
    path('upload/csv/$', views.upload_csv, name='upload_csv'),
    path('data/', views.read_table_data, name='data'),
    path('upload/excel/$', views.upload_excel, name='upload_excel'),
    path('see_excels/', views.read_excel_files, name='see_excels'),
    path(r'download_excel/(?P<part_id>[0-9]{*})/$', views.get_excel_file , name='download'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)