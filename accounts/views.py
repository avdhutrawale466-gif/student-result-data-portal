from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Student
from results.models import Result


def student_login(request):

    if request.user.is_authenticated:

        if hasattr(request.user, "student_profile"):
            return redirect("student_dashboard")

        if request.user.is_staff:
            return redirect("/admin/")

    if request.method == "POST":

        student_id = request.POST.get("student_id")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=student_id,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_staff:
                return redirect("/admin/")

            return redirect("student_dashboard")

        messages.error(
            request,
            "Invalid Student ID or Password."
        )

    return render(
        request,
        "accounts/login.html"
    )


def student_register(request):

    if request.method == "POST":

        student_id = request.POST.get("student_id")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        student_id = student_id.strip()
        email = email.strip()

        try:
            student = Student.objects.get(
                student_id=student_id
            )
        except Student.DoesNotExist:

            messages.error(
                request,
                "This Student ID was not found in university result data."
            )

            return render(
                request,
                "accounts/register.html"
            )

        if student.user is not None:

            messages.error(
                request,
                "An account is already registered with this Student ID."
            )

            return render(
                request,
                "accounts/register.html"
            )

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "This email is already registered."
            )

            return render(
                request,
                "accounts/register.html"
            )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "accounts/register.html"
            )

        user = User.objects.create_user(
            username=student_id,
            email=email,
            password=password
        )

        student.user = user
        student.email = email
        student.email_verified = False

        student.save()

        messages.success(
            request,
            "Account created successfully. You can now login."
        )

        return redirect("student_login")

    return render(
        request,
        "accounts/register.html"
    )


@login_required
def student_dashboard(request):

    student = request.user.student_profile

    results = Result.objects.filter(
        student=student
    ).select_related(
        "subject",
        "batch"
    ).order_by(
        "batch__semester",
        "subject__course_code"
    )

    semesters = {}

    for result in results:

        semester = result.batch.semester

        if semester not in semesters:

            semesters[semester] = []

        semesters[semester].append(result)

    # --------------------------------
    # Semester-wise SGPA
    # --------------------------------

    semester_summary = {}

    for semester, semester_results in semesters.items():

        total_credit_points = 0
        total_credits = 0
        backlog_count = 0

        for result in semester_results:

            grade = str(
                result.grade
            ).strip().upper()

            grade_point = result.grade_point
            credits = result.credits

            if grade in ["FF", "AOO", "ZOO"]:

                backlog_count += 1

            if (
                grade_point is not None
                and credits is not None
                and credits > 0
            ):

                total_credit_points += (
                    float(grade_point)
                    * float(credits)
                )

                total_credits += float(
                    credits
                )

        if total_credits > 0:

            sgpa = (
                total_credit_points
                / total_credits
            )

        else:

            sgpa = 0

        semester_summary[semester] = {
            "sgpa": round(sgpa, 2),
            "backlogs": backlog_count,
            "total_credits": total_credits,
        }

    # --------------------------------
    # Overall CGPA
    # --------------------------------

    total_credit_points = 0
    total_credits = 0

    for result in results:

        grade_point = result.grade_point
        credits = result.credits

        if (
            grade_point is not None
            and credits is not None
            and credits > 0
        ):

            total_credit_points += (
                float(grade_point)
                * float(credits)
            )

            total_credits += float(
                credits
            )

    if total_credits > 0:

        cgpa = (
            total_credit_points
            / total_credits
        )

    else:

        cgpa = 0

    # --------------------------------
    # Overall statistics
    # --------------------------------

    total_subjects = results.count()

    backlog_subjects = results.filter(
        grade__in=[
            "FF",
            "AOO",
            "ZOO"
        ]
    ).count()

    passed_subjects = (
        total_subjects
        - backlog_subjects
    )

    # --------------------------------
    # Make SGPA directly available
    # to the template
    # --------------------------------

    semester_data = []

    for semester, semester_results in semesters.items():

        semester_data.append({
            "semester": semester,
            "results": semester_results,
            "sgpa": semester_summary[
                semester
            ]["sgpa"],
            "backlogs": semester_summary[
                semester
            ]["backlogs"],
        })

    context = {
        "student": student,
        "results": results,
        "semesters": semester_data,
        "cgpa": round(cgpa, 2),
        "total_subjects": total_subjects,
        "passed_subjects": passed_subjects,
        "backlog_subjects": backlog_subjects,
    }

    return render(
        request,
        "student/dashboard.html",
        context
    )


@login_required
def student_logout(request):

    logout(request)

    return redirect("student_login")