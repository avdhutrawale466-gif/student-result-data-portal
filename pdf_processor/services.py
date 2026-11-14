from pathlib import Path

from accounts.models import Student
from results.models import ResultBatch, Subject, Result

from .processor import parse_pdf
from .importers import parse_result_file


def clean_value(value):

    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() == "nan":
        return ""

    return text


def to_float(value):

    try:

        if value is None:
            return None

        text = str(value).strip()

        if text == "" or text.lower() == "nan":
            return None

        return float(text)

    except (ValueError, TypeError):

        return None


def get_subject_credits(course_code):

    credit_map = {

        "BTITC301": 4,
        "BTITC302": 4,
        "BTITC303": 4,
        "BTITC304": 4,

    }

    return credit_map.get(
        clean_value(course_code),
        None
    )


def get_result_status(grade, existing_status=""):

    existing_status = clean_value(
        existing_status
    )

    if existing_status:
        return existing_status.upper()

    grade = clean_value(
        grade
    ).upper()

    if grade in ["FF", "AOO", "ZOO"]:
        return "FAIL"

    if grade:
        return "PASS"

    return ""


def get_or_create_student(student_id, name):

    student_id = clean_value(student_id)
    name = clean_value(name)

    if not student_id:
        return None

    student = Student.objects.filter(
        student_id=student_id
    ).first()

    if student:

        if name and student.name != name:

            student.name = name

            student.save(
                update_fields=["name"]
            )

        return student

    student = Student.objects.create(
        student_id=student_id,
        name=name,
        email=None,
        email_verified=False
    )

    return student


def get_or_create_subject(
    course_code,
    subject_code,
    subject_name,
    semester
):

    course_code = clean_value(
        course_code
    )

    subject_code = clean_value(
        subject_code
    )

    subject_name = clean_value(
        subject_name
    )

    credits = get_subject_credits(
        course_code
    )

    subject = Subject.objects.filter(
        course_code=course_code,
        subject_code=subject_code,
        semester=semester
    ).first()

    if subject:

        changed = False

        if (
            subject_name
            and subject.subject_name != subject_name
        ):

            subject.subject_name = subject_name

            changed = True

        if (
            credits is not None
            and subject.credits != credits
        ):

            subject.credits = credits

            changed = True

        if changed:

            subject.save()

        return subject

    return Subject.objects.create(

        course_code=course_code,

        subject_code=subject_code,

        subject_name=subject_name or course_code,

        semester=semester,

        credits=credits

    )


def save_result(
    student,
    batch,
    subject,
    obtained_marks=None,
    grade="",
    grade_point=None,
    credits=None,
    result_status=""
):

    grade = clean_value(
        grade
    ).upper()

    grade_point = to_float(
        grade_point
    )

    obtained_marks = to_float(
        obtained_marks
    )

    credits = to_float(
        credits
    )

    if credits is None:

        credits = subject.credits

    if credits is None:

        credits = get_subject_credits(
            subject.course_code
        )

    result_status = get_result_status(
        grade,
        result_status
    )

    existing = Result.objects.filter(
        student=student,
        batch=batch,
        subject=subject
    ).first()

    if existing:

        existing.obtained_marks = obtained_marks

        existing.grade = grade

        existing.grade_point = grade_point

        existing.credits = credits

        existing.result_status = result_status

        existing.save()

        return existing, False

    result = Result.objects.create(

        student=student,

        batch=batch,

        subject=subject,

        obtained_marks=obtained_marks,

        grade=grade,

        grade_point=grade_point,

        credits=credits,

        result_status=result_status

    )

    return result, True


def import_csv_or_xlsx(result_file):

    file_path = result_file.file.path

    records = parse_result_file(
        file_path
    )

    batch = result_file.batch

    created_count = 0

    skipped_count = 0

    for record in records:

        student = get_or_create_student(
            record.get("student_id"),
            record.get("name")
        )

        if not student:
            continue

        semester = record.get(
            "semester"
        )

        if not semester:

            semester = batch.semester

        subject = get_or_create_subject(

            record.get(
                "course_code",
                ""
            ),

            record.get(
                "subject_code",
                ""
            ),

            record.get(
                "subject_name",
                ""
            ),

            semester

        )

        result, created = save_result(

            student=student,

            batch=batch,

            subject=subject,

            obtained_marks=record.get(
                "obtained_marks"
            ),

            grade=record.get(
                "grade"
            ),

            grade_point=record.get(
                "grade_point"
            ),

            credits=record.get(
                "credits"
            ),

            result_status=record.get(
                "result_status"
            )

        )

        if created:

            created_count += 1

        else:

            skipped_count += 1

    return created_count, skipped_count


def import_pdf(result_file):

    file_path = result_file.file.path

    records = parse_pdf(
        file_path
    )

    batch = result_file.batch

    created_count = 0

    skipped_count = 0

    subject_codes = [

        "BTBSC404",
        "BTCOC401",
        "BTCOC402",
        "BTCOL406",
        "BTCOS407",
        "BTES405",
        "BTHM403",

    ]

    subject_credits = [

        3,
        4,
        4,
        3,
        2,
        4,
        3,

    ]

    for record in records:

        student = get_or_create_student(

            record.get(
                "student_id"
            ),

            record.get(
                "name"
            )

        )

        if not student:
            continue

        subjects = record.get(
            "subjects",
            []
        )

        for index, subject_data in enumerate(
            subjects
        ):

            if index >= len(
                subject_codes
            ):
                break

            subject_code = subject_codes[
                index
            ]

            subject = get_or_create_subject(

                course_code=subject_code,

                subject_code=subject_code,

                subject_name=subject_code,

                semester=batch.semester

            )

            # PDF credits are defined
            # separately for each subject.

            pdf_credits = subject_credits[
                index
            ]

            result, created = save_result(

                student=student,

                batch=batch,

                subject=subject,

                obtained_marks=None,

                grade=subject_data.get(
                    "grade"
                ),

                grade_point=subject_data.get(
                    "grade_point"
                ),

                credits=pdf_credits,

                result_status=record.get(
                    "result_status",
                    ""
                )

            )

            if created:

                created_count += 1

            else:

                skipped_count += 1

    return created_count, skipped_count


def process_result_file(result_file):

    result_file.processing_status = "PROCESSING"

    result_file.save(
        update_fields=[
            "processing_status"
        ]
    )

    try:

        extension = Path(
            result_file.file.name
        ).suffix.lower()

        if extension == ".pdf":

            created_count, skipped_count = import_pdf(
                result_file
            )

        elif extension in [
            ".csv",
            ".xlsx"
        ]:

            created_count, skipped_count = import_csv_or_xlsx(
                result_file
            )

        else:

            raise ValueError(
                f"Unsupported file format: {extension}"
            )

        result_file.processing_status = "COMPLETED"

        result_file.save(
            update_fields=[
                "processing_status"
            ]
        )

        return {

            "success": True,

            "created": created_count,

            "skipped": skipped_count,

        }

    except Exception:

        result_file.processing_status = "FAILED"

        result_file.save(
            update_fields=[
                "processing_status"
            ]
        )

        raise