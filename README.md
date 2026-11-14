# 🎓 Student Result Data Portal

A Django-based web application that simplifies student result management by allowing administrators to upload, process, and manage semester-wise academic results from PDF, CSV, and Excel files.

The portal is designed to organize student academic records, manage semester-wise results, and make result information easier to access.

## 🚀 Features

### 1. Student Management
- Student registration and account management.
- Store student details such as student ID and name.
- Manage student academic records.

### 2. Result Management
- Semester-wise result management.
- Support for regular and backlog examination batches.
- Store subject-wise marks and grades.
- Manage SGPA, grade points, credits, and result status.

### 3. Multiple File Format Support
Upload and process academic result files in:
- PDF
- CSV
- XLSX (Excel)

### 4. Automated Result Processing
- Extract student information from result files.
- Read student IDs and names.
- Extract subject-wise grades, grade points, and credits from PDFs.
- Process CSV and Excel result data.
- Automatically calculate grades based on obtained marks when applicable.
- Store processed information in the database.

### 5. Django Admin Dashboard
- Manage students, subjects, and result batches.
- View uploaded result files.
- Track file processing status.
- Reprocess uploaded result files.

### 6. Processing Status
Uploaded files can have the following statuses:
- Pending
- Processing
- Completed
- Failed

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| SQLite | Database |
| HTML | Frontend structure |
| CSS | Frontend styling |
| Pandas | CSV and Excel processing |
| PyMuPDF | PDF text extraction |
| OpenPyXL | Excel file support |

## 📂 Project Structure

```text
student-result-data-portal/
│
├── accounts/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── results/
│   ├── migrations/
│   ├── models.py
│   ├── admin.py
│   └── apps.py
│
├── pdf_processor/
│   ├── importers.py
│   ├── processor.py
│   ├── services.py
│   └── apps.py
│
├── templates/
├── static/
├── media/                 # Local uploaded files
├── manage.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites

- Python installed
- Git installed
- Basic knowledge of Django

### Step 1: Clone the Repository

```bash
git clone https://github.com/avdhutrawale466-gif/student-result-data-portal.git
```

### Step 2: Navigate to the Project

```bash
cd student-result-data-portal
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

If a requirements file is not available, install the main dependencies:

```bash
pip install django pandas pymupdf openpyxl
```

### Step 5: Configure Django Secret Key

Set a private environment variable instead of hardcoding the Django secret key.

Generate a key:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set the generated key as an environment variable:

```powershell
$env:DJANGO_SECRET_KEY = "YOUR_GENERATED_SECRET_KEY"
```

In `config/settings.py`, load it using:

```python
import os

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY is missing")
```

Never upload actual secret keys or passwords to GitHub.

### Step 6: Apply Database Migrations

```bash
python manage.py migrate
```

### Step 7: Create an Administrator Account

```bash
python manage.py createsuperuser
```

### Step 8: Run the Development Server

```bash
python manage.py runserver
```

Open the application:

http://127.0.0.1:8000/

Django Admin:

http://127.0.0.1:8000/admin/

## 🔄 Application Workflow

1. Administrator logs into the portal.
2. Creates or manages examination batches.
3. Uploads student result files.
4. The system identifies the uploaded file format.
5. The appropriate PDF, CSV, or Excel processor extracts result information.
6. Student and subject records are created or updated.
7. Processed results are stored in the database.
8. The administrator can review results and processing status.

## 🔐 Security Considerations

- Django authentication and admin permissions.
- Secret keys should be stored in environment variables.
- Database files should not be committed to GitHub.
- Uploaded student result documents should remain private.
- Do not upload real student personal information or academic records to a public repository.
- `DEBUG = True` should only be used during local development.
- Configure secure production settings before deployment.

## 🔮 Future Enhancements

- Student dashboard for viewing personal results.
- Semester-wise result PDF generation.
- SGPA and CGPA calculation.
- Advanced result analytics and visualization.
- Search and filtering of student records.
- Improved file validation and error reporting.
- Cloud deployment with secure storage.

## 🎯 Project Objective

The main objective of this project is to reduce manual effort in academic result management through automated file processing, structured database storage, and centralized result administration.

## 👨‍💻 Author

**Student Result Data Portal**

GitHub: [@avdhutrawale466-gif](https://github.com/avdhutrawale466-gif)

---

⭐ If you find this project useful, consider giving the repository a star.

**Note:** This project is intended for educational and development purposes. Production deployment requires additional security configuration and testing.
