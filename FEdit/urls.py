from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.views.static import serve
app_name = 'FEdit'
urlpatterns = [
    path('', views.index, name='index'),
    path('viton', views.viton, name='viton'),
    path('pose', views.pose, name='pose'),
    # path('viton', views.index_viton, name='viton'),
    # path('', views.IndexView.as_view(), name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('results/', views.results, name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    #path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),

] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)