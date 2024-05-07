from django.urls import path
from Seating import views
from django.contrib import admin

admin.site.site_header = 'DarkStarTech Admin'

urlpatterns = [
    path("", views.home, name="home"),
    path('contacts',views.contacts , name='contacts'),
    path("login", views.loginUser, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("signup", views.signupuser,  name="signup"),
    path('error_page' , views.error_page , name="error_page"),
    path('verified/<auth_token>' , views.verified , name="verified"),
    path('passwordReset' , views.passwordreset , name="passwordReset"),
    path('changepassword/<action>/<auth_token>' , views.changepassword , name="changepassword"),

    path("rooms", views.rooms, name="rooms"),
    path("addroom", views.rooms_add, name="addroom"),
    path("addbatch", views.add_batch, name="addbatch"),
    path("class", views.batch_class, name="class"),
    path("plan", views.do_plan, name="plan"),
    path("makeplan", views.make_plan, name="makeplan"),
    path("test", views.test_page, name="test"),

    path("profileimg", views.profile_img_upload, name="profileimg"),
    path("devmng", views.devmng, name="devmng"),

    path("attendance", views.attendance, name="attendance"),
    path("plusdates", views.add_attendence_date, name="plusdates"),
]

