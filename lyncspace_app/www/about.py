import frappe

def get_context(context):

    context.skills = frappe.get_all(
        "Technology Skill",
        filters={"published": 1},
        fields=["tech_name", "percentage", "sort_order"],
        order_by="sort_order asc"
    )

     # TECHNOLOGY LOGOS
    context.tech_logos = frappe.get_all(
        "Technology Logo",
        filters={"published": 1},
        fields=["tech_name","logo","order"],
        order_by="`order` asc")

    return context
