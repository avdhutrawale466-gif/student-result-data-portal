from django.contrib import admin, messages

from .models import (
    ResultBatch,
    Subject,
    Result,
    ResultFile
)

from pdf_processor.services import process_result_file


@admin.register(ResultBatch)
class ResultBatchAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "semester",
        "exam_type",
        "exam_session",
        "created_at",
    )

    list_filter = (
        "semester",
        "exam_type",
    )

    search_fields = (
        "exam_session",
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "course_code",
        "subject_code",
        "subject_name",
        "semester",
        "credits",
    )

    search_fields = (
        "course_code",
        "subject_code",
        "subject_name",
    )

    list_filter = (
        "semester",
    )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "batch",
        "subject",
        "grade",
        "grade_point",
        "credits",
        "result_status",
    )

    search_fields = (
        "student__student_id",
        "student__name",
        "subject__subject_name",
        "subject__course_code",
    )

    list_filter = (
        "grade",
        "batch",
        "result_status",
    )


@admin.register(ResultFile)
class ResultFileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "batch",
        "file",
        "file_type",
        "processing_status",
        "uploaded_at",
    )

    list_filter = (
        "file_type",
        "processing_status",
    )

    readonly_fields = (
        "processing_status",
        "uploaded_at",
    )

    actions = [
        "reprocess_files",
    ]

    @admin.action(
        description="Reprocess selected result files"
    )
    def reprocess_files(self, request, queryset):

        success_count = 0
        failed_count = 0

        for result_file in queryset:

            try:

                process_result_file(
                    result_file
                )

                success_count += 1

            except Exception as error:

                failed_count += 1

                self.message_user(
                    request,
                    f"{result_file.file.name}: {error}",
                    level=messages.ERROR
                )

        if success_count:

            self.message_user(
                request,
                f"{success_count} result file(s) reprocessed successfully.",
                level=messages.SUCCESS
            )

        if failed_count:

            self.message_user(
                request,
                f"{failed_count} result file(s) failed to process.",
                level=messages.ERROR
            )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        # Automatically detect file type

        filename = obj.file.name.lower()

        if filename.endswith(".pdf"):

            obj.file_type = "PDF"

        elif filename.endswith(".csv"):

            obj.file_type = "CSV"

        elif filename.endswith(".xlsx"):

            obj.file_type = "XLSX"

        else:

            raise ValueError(
                "Only PDF, CSV and XLSX files are supported."
            )

        # Save file first

        super().save_model(
            request,
            obj,
            form,
            change
        )

        # Process only when a new file is uploaded

        if not change:

            process_result_file(
                obj
            )