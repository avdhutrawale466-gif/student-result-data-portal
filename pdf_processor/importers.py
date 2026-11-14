import pandas as pd
import re


def clean_student_id(value):

    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = value.lstrip("'")

    if value.endswith(".0"):
        value = value[:-2]

    return value


def clean_text(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def calculate_grade(marks):

    try:
        marks = float(marks)
    except:
        return "", None

    if marks >= 90.01:
        return "EX", 10

    elif marks >= 85.01:
        return "AA", 9

    elif marks >= 80.01:
        return "AB", 8.5

    elif marks >= 75.01:
        return "BB", 8

    elif marks >= 70.01:
        return "BC", 7.5

    elif marks >= 65.01:
        return "CC", 7

    elif marks >= 60.01:
        return "CD", 6.5

    elif marks >= 55.01:
        return "DD", 6

    elif marks >= 50.01:
        return "DE", 5.5

    elif marks >= 40:
        return "EE", 5

    else:
        return "FF", 0


def parse_csv_file(file_path):

    df = pd.read_csv(file_path)

    records = []

    for _, row in df.iterrows():

        student_id = clean_student_id(
            row.get("EnrollMent No")
        )

        name = clean_text(
            row.get("Candidate Name")
        )

        program = clean_text(
            row.get("Program")
        )

        total_marks = row.get("Total Marks")

        obtained_marks = row.get("Obtain Marks")

        course_code = ""
        subject_name = ""
        semester = None

        match = re.match(
            r"^([^_]+)_(.+)_(\d+)$",
            program
        )

        if match:

            course_code = match.group(1)

            subject_name = match.group(2)

            semester = int(match.group(3))


        grade, grade_point = calculate_grade(
            obtained_marks
        )


        records.append({

            "student_id": student_id,

            "name": name,

            "semester": semester,

            "course_code": course_code,

            "subject_code": "",

            "subject_name": subject_name,

            "total_marks": total_marks,

            "obtained_marks": obtained_marks,

            "grade": grade,

            "grade_point": grade_point,

            "credits": None,

            "result_status": ""

        })


    return records


def parse_xlsx_file(file_path):

    raw_df = pd.read_excel(
        file_path,
        header=None
    )

    header_row = None

    for index, row in raw_df.iterrows():

        values = [
            str(value).strip()
            for value in row.tolist()
        ]

        if "PRN" in values and "Name" in values:

            header_row = index

            break


    if header_row is None:

        raise ValueError(
            "Could not find XLSX header row."
        )


    df = pd.read_excel(
        file_path,
        header=header_row
    )

    records = []


    for _, row in df.iterrows():

        student_id = clean_student_id(
            row.get("PRN")
        )

        name = clean_text(
            row.get("Name")
        )

        semester_value = row.get("Semester")

        course_code = clean_text(
            row.get("Course Code")
        )

        subject_code = clean_text(
            row.get("Subject Code")
        )

        subject_name = clean_text(
            row.get("Subject Name")
        )


        obtained_marks = row.get(
            "Rev Obtained Marks"
        )


        if pd.isna(obtained_marks):

            obtained_marks = row.get(
                "Obtained Marks"
            )


        grade_remark = clean_text(
            row.get("Grade / Remark")
        )


        try:

            semester = int(
                float(semester_value)
            )

        except:

            semester = None


        # If university already gives a grade,
        # use that grade.

        grade = grade_remark

        grade_point = None


        # Calculate grade point from marks.

        calculated_grade, calculated_grade_point = calculate_grade(
            obtained_marks
        )


        if not grade:

            grade = calculated_grade


        if calculated_grade_point is not None:

            grade_point = calculated_grade_point


        records.append({

            "student_id": student_id,

            "name": name,

            "semester": semester,

            "course_code": course_code,

            "subject_code": subject_code,

            "subject_name": subject_name,

            "total_marks": None,

            "obtained_marks": obtained_marks,

            "grade": grade,

            "grade_point": grade_point,

            "credits": None,

            "result_status": ""

        })


    return records


def parse_result_file(file_path):

    file_path = str(
        file_path
    ).lower()


    if file_path.endswith(".csv"):

        return parse_csv_file(
            file_path
        )


    elif file_path.endswith(".xlsx"):

        return parse_xlsx_file(
            file_path
        )


    else:

        raise ValueError(
            "Unsupported file format. "
            "Only CSV and XLSX are supported."
        )