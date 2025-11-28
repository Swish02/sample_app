import frappe

def get_context(context):
    # ---------------------------
    # SLIDER (Homepage Carousel Slide)
    # ---------------------------
    slides = frappe.get_all(
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
            "`order`",
        ],
        order_by="`order` asc",
        ignore_permissions=True,   # ✅ so Guest/website users can see
    )

    # Optional: fallback slide if no published records
    if not slides:
        slides = [{
            "title_line_1": "Welcome to Lyncspace",
            "title_line_2": "Build smart web apps",
            "title_line_3": "",
            "description": "Control all homepage content using Frappe Doctypes.",
            "media_type": "None",
            "image": "",
            "youtube_embed": "",
            "order": 1,
        }]

    context.slides = slides

    # ---------------------------
    # HERO TEXT (single doctype)
    # ---------------------------
    try:
        context.hero = frappe.get_single("Hero Section Text")
    except Exception:
        context.hero = None

    # ---------------------------
    # FEATURES
    # ---------------------------
    context.features = frappe.get_all(
        "Feature",
        filters={"published": 1},
        fields=["title", "icon", "description", "`order`"],
        order_by="`order` asc",
        ignore_permissions=True,
    )

    # ---------------------------
    # TECHNOLOGY LOGOS
    # ---------------------------
    context.tech_logos = frappe.get_all(
        "Technology Logo",
        filters={"published": 1},
        fields=["tech_name", "logo", "`order`"],
        order_by="`order` asc",
        ignore_permissions=True,
    )

    # STATIC BANNER BACKGROUND
    context.banner_bg = "/assets/lyncspace_app/img/banner-bg.jpg"

    return context
