from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('park/', include('park.urls')),
    path('map/', include('map.urls')),
    path('schedule/', include('schedule.urls')),
    path('accounts/', include('allauth.urls')),  # allauth만 연결
    path('', RedirectView.as_view(url='/park/')),  # 루트는 park로 리다이렉트
]
