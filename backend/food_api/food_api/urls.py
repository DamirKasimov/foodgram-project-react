from django.contrib import admin
from django.urls import include, path
from users.views import MyTokenCreateView, Logout
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/', include('users.urls')),
    #path('api/', include('djoser.urls')),
    # получение токена/вход существующего пользователя
    path('api/auth/token/login/', MyTokenCreateView.as_view(), name='login'),
    # урл для логаута, удаления токена
    path('api/auth/token/logout/', Logout.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
