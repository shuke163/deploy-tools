'''
@Author: your name
@Date: 2020-04-13 12:02:08
@LastEditTime: 2020-04-13 12:19:37
@LastEditors: your name
@Description: In User Settings Edit
@FilePath: /deploy-backend/door/urls.py
'''
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.conf.urls import include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from rest_framework.authtoken.views import obtain_auth_token

from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="door Server API",
        url="http://localhost:9002/api/",
        default_version='v1',
        description="Door api docs",
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
    urlconf="door.urls",
)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth', obtain_auth_token, name='api_token_auth'),
    url(r'^swagger$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r'api/(?P<version>[v1]+)/account/', include("account.urls")),
    url(r'api/(?P<version>[v1]+)/deploy/', include("deploy.urls")),
    url(r'api/(?P<version>[v1]+)/host/', include("host.urls")),
    # url(r'api/(?P<version>[v1]+)/sprint/', include("sprint.urls")),
]
