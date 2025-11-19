import frappe

def get_context(context):

    # Fetch job openings ordered properly
    context.jobs = frappe.get_all(
        "Job Opening",
        filters={"published": 1},
        fields=[
            "name",
            "job_title",
            "intro",
            "requirements",
            "sort_order"
        ],
        order_by="sort_order asc"
    )

    return context

