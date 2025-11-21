import frappe

def get_context(context):

    # SLIDER
    context.slides = frappe.get_all(
        "Homepage Carousel Slide",
        filters={"published": 1},
        fields=[
            "title_line_1",
            "title_line_2",
            "title_line_3",
            "description",
            "media_type",
            "image",
            "youtube_embed",
            "order" 
        ],
        order_by="`order` asc"
    )

    # HERO TEXT
    context.hero = frappe.get_single("Hero Section Text")

    # FEATURES
    context.features = frappe.get_all(
        "Feature",
        filters={"published": 1},
        fields=["title","icon","description","order"],
        order_by="`order` asc"
    )

    # TECHNOLOGY LOGOS
    context.tech_logos = frappe.get_all(
        "Technology Logo",
        filters={"published": 1},
        fields=["tech_name","logo","order"],
        order_by="`order` asc"
    )

    # STATIC BANNER BACKGROUND
    context.banner_bg = "/assets/lyncspace_app/img/banner-bg.jpg"

    return context
