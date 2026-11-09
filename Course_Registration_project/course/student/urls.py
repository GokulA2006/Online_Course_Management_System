from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/create/', views.add_course, name='add_course'),
    path('courses/', views.view_courses, name='view_courses'),
    path('courses/register/<int:id>/', views.register_course, name='register_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('courses/edit/<int:id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:id>/', views.delete_course, name='delete_course'),
    path('', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('students/', views.view_students, name='view_students'),
    path('admin-registrations/', views.admin_registrations, name='admin_registrations'),
    path('update-status/<int:id>/<str:status>/', views.update_status, name='update_status'),
    path('profile/', views.student_profile, name='student_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('course-details/<int:id>/', views.course_details, name='course_details'),
    path('students/delete/<int:id>/', views.delete_student, name='delete_student'),
]