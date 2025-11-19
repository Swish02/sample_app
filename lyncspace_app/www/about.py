import frappe

def get_context(context):

    context.skills = frappe.get_all(
        "Technology Skill",
        filters={"published": 1},
        fields=["tech_name", "percentage", "sort_order"],
        order_by="sort_order asc"
    )

    return context
