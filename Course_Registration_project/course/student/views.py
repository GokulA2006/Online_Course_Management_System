from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .forms import StudentForm
from .forms import LoginForm
from .forms import CourseForm
from .models import Student
from .models import Course
from .models import Student, Course, Registration
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.paginator import Paginator
from django.db.models import Count


def login(request):
    msg = ''

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                student = Student.objects.get(email=email)

                if check_password(password, student.password):
                    request.session['student_id'] = student.id
                    return redirect('dashboard')
                else:
                    msg = 'Invalid password'

            except Student.DoesNotExist:
                msg = 'Student not found'
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'msg': msg})


def logout_view(request):
    request.session.flush()
    response = redirect('login')
    response.delete_cookie('email')
    response.delete_cookie('password')
    return response

def register(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)

        if form.is_valid():
            student = form.save(commit=False)
            student.password = make_password(student.password)
            student.save()

            return redirect('login')
        else:
            print(form.errors)

    else:
        form = StudentForm()

    return render(request, 'register.html', {'form': form})

def dashboard(request):
    if 'student_id' in request.session:
        student = Student.objects.get(id=request.session['student_id'])

        total_courses = Course.objects.count()

        registrations = Registration.objects.filter(student=student)

        my_courses = registrations.count()
        pending = registrations.filter(status='pending').count()
        approved = registrations.filter(status='approved').count()

        return render(request, 'dashboard.html', {
            'student': student,
            'total_courses': total_courses,
            'my_courses': my_courses,
            'pending': pending,
            'approved': approved
        })

    return redirect('login')


def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('add_course')
    else:
        form = CourseForm()

    return render(request, 'add_course.html', {'form': form})



def view_courses(request):

    courses = Course.objects.all().order_by('id')

    search = request.GET.get('search', '')
    fees = request.GET.get('fees', '')

    if search:
        courses = courses.filter(course_name__icontains=search)

    if fees == 'low':
        courses = courses.filter(fees__lte=5000)

    elif fees == 'high':
        courses = courses.filter(fees__gt=5000)

    paginator = Paginator(courses, 6)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(request, 'courses.html', {
        'courses': page_obj,
        'page_obj': page_obj,
        'search': search,
        'fees': fees
    })

def register_course(request, id):
    if 'student_id' not in request.session:
        return redirect('login')

    student = Student.objects.get(id=request.session['student_id'])
    course = Course.objects.get(id=id)

    if Registration.objects.filter(student=student, course=course).exists():
        msg = 'Already registered'
    elif course.available_seats > 0:
        Registration.objects.create(
            student=student,
            course=course
        )

        course.available_seats -= 1
        course.save()

        return redirect('view_courses')
    else:
        msg = 'No seats available'

    return render(request, 'course_register.html', {
        'course': course,
        'msg': msg
    })


def my_courses(request):
    if 'student_id' not in request.session:
        return redirect('login')

    student = Student.objects.get(id=request.session['student_id'])

    registrations = Registration.objects.filter(
        student=student
    ).select_related('course')

    total = registrations.count()
    pending = registrations.filter(status='pending').count()
    approved = registrations.filter(status='approved').count()
    rejected = registrations.filter(status='rejected').count()

    return render(request, 'my_courses.html', {
        'registrations': registrations,
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected
    })

def edit_course(request, id):
    course = Course.objects.get(id=id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)

        if form.is_valid():
            form.save()
            return redirect('view_courses')
    else:
        form = CourseForm(instance=course)

    return render(request, 'edit_course.html', {'form': form})

def delete_course(request, id):
    course = Course.objects.get(id=id)

    if request.method == 'POST':
        course.delete()
        return redirect('view_courses')

    return render(request, 'delete_course.html', {'course': course})


def admin_login(request):
    msg = ''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:
            auth_login(request, user)
            return redirect('admin_dashboard')
        else:
            msg = 'Invalid admin username or password'

    return render(request, 'admin_login.html', {'msg': msg})



def admin_dashboard(request):
    if request.user.is_authenticated and request.user.is_staff:

        total_students = Student.objects.count()
        total_courses = Course.objects.count()
        total_registrations = Registration.objects.count()

        pending = Registration.objects.filter(status='pending').count()

        recent_registrations = Registration.objects.select_related(
            'student', 'course'
        ).order_by('-id')[:5]

        pending_registrations = Registration.objects.filter(
            status='pending'
        ).select_related('student', 'course').order_by('-id')[:5]

        courses = Course.objects.all()

        popular_courses = Course.objects.annotate(
            registration_count=Count('registration')
        ).order_by('-registration_count')[:5]

        return render(request, 'admin_dashboard.html', {
            'total_students': total_students,
            'total_courses': total_courses,
            'total_registrations': total_registrations,
            'pending': pending,
            'recent_registrations': recent_registrations,
            'pending_registrations': pending_registrations,
            'popular_courses': popular_courses,
            'courses': courses
        })

    return redirect('admin_login')



def admin_logout(request):
    auth_logout(request)
    return redirect('admin_login')

def view_students(request):
    if request.user.is_authenticated and request.user.is_staff:
        students = Student.objects.all()
        return render(request, 'view_students.html', {'students': students})
    return redirect('admin_login')

def admin_registrations(request):
    if request.user.is_authenticated and request.user.is_staff:
        registrations = Registration.objects.all().select_related('student', 'course')
        return render(request, 'admin_registrations.html', {
            'registrations': registrations
        })

    return redirect('admin_login')


def update_status(request, id, status):
    if request.user.is_authenticated and request.user.is_staff:
        registration = get_object_or_404(Registration, id=id)

        if status in ['approved', 'rejected']:
            registration.status = status
            registration.save()

        return redirect('admin_registrations')

    return redirect('admin_login')

def student_profile(request):
    if 'student_id' in request.session:
        student = Student.objects.get(id=request.session['student_id'])

        return render(request, 'student_profile.html', {
            'student': student
        })

    return redirect('login')


def edit_profile(request):
    if 'student_id' in request.session:
        student = Student.objects.get(id=request.session['student_id'])

        if request.method == 'POST':
            student.name = request.POST.get('name')
            student.email = request.POST.get('email')
            student.phone_number = request.POST.get('phone_number')

            student.save()

            return redirect('student_profile')

        return render(request, 'edit_profile.html', {
            'student': student
        })

    return redirect('login')

def course_details(request, id):
    course = get_object_or_404(Course, id=id)

    return render(request, 'course_details.html', {
        'course': course
    })

def delete_student(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            student = get_object_or_404(Student, id=id)
            student.delete()

        return redirect('view_students')

    return redirect('admin_login')