import frappe

def get_context(context):
    context.no_cache = 1  # optional, so changes show immediately

    context.jobs = frappe.get_all(
        "Job Opening",
        filters={"published": 1},
        fields=[
            "name",
            "job_title",
            "intro",
            "requirements",
            "sort_order",
        ],
        order_by="sort_order asc",
        ignore_permissions=True,  # 🔥 important for public website
    )

    return context
