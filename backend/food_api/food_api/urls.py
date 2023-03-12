"""food_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from users.views import MyTokenCreateView, Logout, CustomUserViewSet
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # для добавления @actions управления подписками
    path('api/users/subscriptions/', CustomUserViewSet.as_view(
        {'get': 'subscriptions'}), name='subscriptions'),
    path('api/users/<int:id>/subscribe/', CustomUserViewSet.as_view(
        {'post': 'subscribe', 'delete': 'subscribe'}), name='to_un/subscribe'),
    path('api/', include('djoser.urls')),
    # получение токена/вход существующего пользователя
    path('api/auth/token/login/', MyTokenCreateView.as_view(), name='login'),
    # урл для логаута, удаления токена
    path('api/auth/token/logout/', Logout.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
