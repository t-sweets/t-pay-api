from django.conf.urls import include, url
from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token,
                                      verify_jwt_token)

urlpatterns = [
    url(r'^login/', obtain_jwt_token),
]
