import re
import fitz


# ---------------------------------------------------------
# 1. PDF SE PAGES READ KARNA
# ---------------------------------------------------------

def extract_pdf_pages(file_path):

    document = fitz.open(file_path)

    pages = []

    for page in document:
        pages.append(page.get_text())

    document.close()

    return pages


# ---------------------------------------------------------
# 2. STUDENT LINE CHECK KARNA
# ---------------------------------------------------------

def is_student_line(line):

    return re.match(r"^\d{14}\s+", line.strip()) is not None


# ---------------------------------------------------------
# 3. STUDENT ID + NAME EXTRACT KARNA
# ---------------------------------------------------------

def extract_student_details(line):

    line = line.strip()

    match = re.match(
        r"^(\d{14})\s+(?:\([A-Z]\))?(.*?)\s+\d+\s+-\s+",
        line
    )

    if match:

        student_id = match.group(1)

        name = match.group(2).strip()

        return student_id, name

    # Fallback
    match = re.match(r"^(\d{14})\s+(.*)", line)

    if match:

        student_id = match.group(1)

        remaining = match.group(2).strip()

        return student_id, remaining

    return None, None


# ---------------------------------------------------------
# 4. SUBJECT RESULT LINE CHECK KARNA
# ---------------------------------------------------------

def parse_subject_line(line):

    line = line.strip()

    pattern = r"^(-?\d+(?:\.\d+)?)\/([A-Z]{2,5})\/(-?\d+(?:\.\d+)?)(?:\([^)]*\))?$"

    match = re.match(pattern, line)

    if not match:
        return None

    grade_point = float(match.group(1))

    grade = match.group(2)

    credit_value = float(match.group(3))

    return {
        "grade_point": grade_point,
        "grade": grade,
        "credits": credit_value
    }


# ---------------------------------------------------------
# 5. STUDENT RECORD PARSE KARNA
# ---------------------------------------------------------

def parse_student_record(lines, start_index):

    student_line = lines[start_index].strip()

    student_id, name = extract_student_details(student_line)

    if not student_id:
        return None, start_index

    record = {
        "student_id": student_id,
        "name": name,
        "sgpa": None,
        "subjects": [],
        "result_status": ""
    }

    subject_results = []

    i = start_index + 1

    # Search until next student or page end
    while i < len(lines):

        line = lines[i].strip()

        # Next student found
        if is_student_line(line):

            break

        # Try to find subject result
        subject = parse_subject_line(line)

        if subject:

            subject_results.append(subject)

            # This PDF has 7 subjects
            if len(subject_results) == 7:

                # Usually SGPA appears before the subject
                # lines, so we don't search backward here.

                # Stop collecting subjects
                break

        i += 1

    record["subjects"] = subject_results

    # -----------------------------------------------------
    # Search nearby lines for SGPA
    # -----------------------------------------------------

    search_end = min(
        len(lines),
        start_index + 20
    )

    for j in range(start_index + 1, search_end):

        value = lines[j].strip()

        # Ignore subject result lines
        if parse_subject_line(value):
            continue

        # SGPA should normally be between 0 and 10
        try:

            number = float(value)

            if 0 <= number <= 10:

                # Avoid values that are obviously marks/credits
                record["sgpa"] = number

                break

        except ValueError:
            pass

    # -----------------------------------------------------
    # Search result status
    # -----------------------------------------------------

    status_words = [
        "PASS",
        "FAIL",
        "WITHHELD",
        "ABSENT"
    ]

    for j in range(start_index + 1, search_end):

        upper_line = lines[j].strip().upper()

        for status in status_words:

            if status in upper_line:

                record["result_status"] = status

                break

        if record["result_status"]:

            break

    return record, i


# ---------------------------------------------------------
# 6. ENTIRE PDF PARSE KARNA
# ---------------------------------------------------------

def parse_pdf(file_path):

    pages = extract_pdf_pages(file_path)

    all_records = []

    for page_number, page_text in enumerate(pages, start=1):

        lines = page_text.splitlines()

        i = 0

        while i < len(lines):

            line = lines[i].strip()

            if is_student_line(line):

                record, next_index = parse_student_record(
                    lines,
                    i
                )

                if record:

                    record["page_number"] = page_number

                    all_records.append(record)

                    i = next_index

                    continue

            i += 1

    return all_records


# ---------------------------------------------------------
# 7. TEST OUTPUT
# ---------------------------------------------------------

def print_records(records):

    print("\n========================================")
    print("TOTAL STUDENT RECORDS:", len(records))
    print("========================================")

    for record in records[:5]:

        print("\nStudent ID :", record["student_id"])

        print("Name       :", record["name"])

        print("SGPA       :", record["sgpa"])

        print("Status     :", record["result_status"])

        print("Page       :", record["page_number"])

        print("\nSubjects:")

        for number, subject in enumerate(
            record["subjects"],
            start=1
        ):

            print(
                f"{number}. "
                f"Grade Point={subject['grade_point']} | "
                f"Grade={subject['grade']} | "
                f"Credits={subject['credits']}"
            )


# ---------------------------------------------------------
# 8. MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    file_path = (
        "media/result_files/"
        "Sem_4_Revised_Result_Bachelor_of_Technology_"
        "Computer_Science_and_Engineerin_vYPBABs.pdf"
    )

    records = parse_pdf(file_path)

    print_records(records)