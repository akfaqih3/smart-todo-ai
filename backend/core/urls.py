
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tasks.urls')), # Include tasks app URLs under /api/
    # You might add other app URLs here later, e.g., path('api/context/', include('context.urls'))
]
