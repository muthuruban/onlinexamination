from django.shortcuts import render,redirect,reverse

from exam.models import Question
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from student import models as SMODEL
from exam import forms as QFORM


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    'total_student':SMODEL.Student.objects.all().count()
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm=QFORM.CourseForm()
    if request.method=='POST':
        courseForm=QFORM.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='adminlogin')
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    # QuestionFormSet = inlineformset_factory(Course,Question,fields={'marks','question','option1','option2','option3','option4','answer'})
    questionForm = QFORM.QuestionForm()

    length = request.POST.get('totallength')
    # length = 1
    if request.method == 'POST':
        i = 0
        for index in range(i, int(length)):
            # courseId = int()
            courseId = QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            question = ""
            difficulty = ""
            marks = int()
            option1 = ""
            option2 = ""
            option3 = ""
            option4 = ""
            answer = ""
            flag = 0
            if ('difficulty_level' in request.POST):
                difficulty = request.POST['difficulty_level']
            if ('question' + str(index) in request.POST):
                question = request.POST['question' + str(index)]
                flag = 1
            if ('marks' + str(index) in request.POST):
                marks = request.POST['marks' + str(index)]
                flag = 1
            if ('option1_' + str(index) in request.POST):
                option1 = request.POST['option1_' + str(index)]
                flag = 1
            if ('option2_' + str(index) in request.POST):
                option2 = request.POST['option2_' + str(index)]
                flag = 1
            if ('option3_' + str(index) in request.POST):
                option3 = request.POST['option3_' + str(index)]
                flag = 1
            if ('option4_' + str(index) in request.POST):
                option4 = request.POST['option4_' + str(index)]
                flag = 1
            if ('answer' + str(index) in request.POST):
                answer = request.POST['answer' + str(index)]
                flag = 1

            if flag == 1:
                Question.objects.create(course=courseId, difficulty=difficulty, question=question, marks=marks,
                                        option1=option1,
                                        option2=option2, option3=option3, option4=option4, answer=answer)

        # questionForm = forms.QuestionForm(request.POST)
        # if questionForm.is_valid():
        #     if questionForm.cleaned_data:
        #         # question = questionForm.save(commit=False)
        #         questionForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return render(request, 'teacher/teacher_add_question.html',
                  {'questionForm': questionForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses= QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_question.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')
