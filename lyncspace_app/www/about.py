import frappe

def get_context(context):
    # So changes reflect immediately
    context.no_cache = 1

    # TECHNOLOGY SKILLS (progress bars)
    context.skills = frappe.get_all(
        "Technology Skill",
        filters={"published": 1},
        fields=["tech_name", "percentage", "sort_order"],
        order_by="sort_order asc",
        ignore_permissions=True,  # 🔥 important for public website
    )

    # TECHNOLOGY LOGOS (logo slider)
    context.tech_logos = frappe.get_all(
        "Technology Logo",
        filters={"published": 1},
        fields=["tech_name", "logo", "`order`"],
        order_by="`order` asc",
        ignore_permissions=True,  # 🔥 same here
    )

    return context
