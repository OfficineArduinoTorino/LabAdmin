from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from . import views


pwd_change_opts = {
    'template_name': 'labadmin/password_change_form.html',
    'post_change_redirect': 'labadmin-password-change-done',
}

pwd_change_done_opts = {
    'template_name': 'labadmin/password_change_done.html',
}

pwd_reset_opts = {
    'template_name': 'labadmin/password_reset_form.html',
    'email_template_name': 'labadmin/password_reset_email.html',
    'post_reset_redirect': 'labadmin-password-reset-done',
}

pwd_reset_done_opts = {
    'template_name': 'labadmin/password_reset_done.html',
}

pwd_reset_confirm_opts = {
    'template_name': 'labadmin/password_reset_confirm.html',
    'post_reset_redirect': 'labadmin-password-reset-complete',
}

pwd_reset_complete_opts = {
    'template_name': 'labadmin/password_reset_complete.html',
}

urlpatterns = [
    url(r'^opendoorbynfc/$', views.OpenDoor.as_view()),
    url(r'^opendoor/$', views.OpenDoor.as_view(), name="open-door"),
    url(r'^user/identity/$', views.UserIdentity.as_view()),
    url(r'^nfc/users/$', views.LoginByNFC.as_view(), name='nfc-users'),
    url(r'^card/credits/$', views.CardCredits.as_view(), name='card-credits'),
    url(r'^device/use/start/$', views.DeviceStartUse.as_view(), name='device-use-start'),
    url(r'^device/use/stop/$', views.DeviceStopUse.as_view(), name='device-use-stop'),

    url(r'^$', TemplateView.as_view(template_name='labadmin/index.html'), name='labadmin-index'),
    url(r'^profile$', views.UserProfileView.as_view(), name='labadmin-user-profile'),
    url(r'^password/change$', auth_views.password_change, pwd_change_opts, name='labadmin-password-change'),
    url(r'^password/change/done$', auth_views.password_change_done, pwd_change_done_opts, name='labadmin-password-change-done'),
    url(r'^password/reset$', auth_views.password_reset, pwd_reset_opts, name='labadmin-password-reset'),
    url(r'^password/reset/done$', auth_views.password_reset_done, pwd_reset_done_opts, name='labadmin-password-reset-done'),
    url(r'^password/reset/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, pwd_reset_confirm_opts, name='labadmin-password-reset-confirm'),
    url(r'^password/reset/complete$', auth_views.password_reset_complete, pwd_reset_complete_opts, name='labadmin-password-reset-complete'),
    url(r'^logout$', auth_views.logout, {'next_page': 'labadmin-index'}, name='labadmin-logout'),
 ]
