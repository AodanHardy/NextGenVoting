from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('core.urls')),
    path("dashboard", include('elections.urls')),
    path('dashboard/', include(('elections.urls', 'elections'), namespace='elections')),
    path('vote/', include(('voting.urls', 'voting'), namespace='vote')),
]
