# Uncomment next two lines to enable admin:
#from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Uncomment the next line to enable the admin:
    #path('admin/', admin.site.urls)
    path('github/', include('GitHub.urls'))
]
