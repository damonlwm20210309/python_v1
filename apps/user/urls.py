from django.conf.urls import url
from apps.user.views import RegisterView, ActiveView, LoginView

urlpatterns = [
    # url(r'^register$', views.register, name='register'),
    # url(r'^register_handle$', views.register_handle, name='register_handle'),
    url(r'^register$', RegisterView.as_view(), name='register'), # 处理注册页面
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'), # 用户激活
    url(r'^login$', LoginView.as_view(), name='login'), # 登录
]