import re
import difflib
import frappe
from frappe import _
from frappe.utils import validate_email_address, escape_html
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

# SAFE REDIRECT CLASS
class SafeRedirect(HTTPException):
    code = 302
    def __init__(self, location):
        super().__init__()
        self.location = location

    def get_response(self, environ=None):
        from werkzeug.wrappers import Response
        resp = Response("", status=302)
        resp.headers["Location"] = self.location
        return resp
    
@frappe.whitelist(allow_guest=True)
def submit_contact(lead_name=None, email_id=None, phone=None, notes=None):
    # ---------- Normalize ----------
    lead_name = (lead_name or "").strip()
    email_id = (email_id or "").strip()
    phone = (phone or "").strip()
    notes = (notes or "").strip()

    errors = {}

    # ---------- Name validation ----------
    if not lead_name:
        errors["lead_name"] = "Name is required."
    elif not re.fullmatch(r"[A-Za-z ]{2,50}", lead_name):
        errors["lead_name"] = "Name must contain only letters and spaces. Numbers are not allowed."

    # ---------- Email validation ----------
    if not email_id:
        errors["email_id"] = "Email is required."
    elif not validate_email_address(email_id, throw=False):
        errors["email_id"] = "Enter a valid email address."

    # ---------- Phone validation ----------
    if not phone:
        errors["phone"] = "Phone number is required."
    elif not re.fullmatch(r"\d{10}", phone):
        errors["phone"] = "Phone number must be exactly 10 digits."
    elif phone == "0000000000":
        errors["phone"] = "Please enter a valid phone number."

    # ---------- Notes validation ----------
    if not notes:
        errors["notes"] = "Message is required."
    elif len(notes.split()) < 5:
        errors["notes"] = "Message must be at least 5 words."

    # ---------- If validation failed, return cleanly ----------
    if errors:
        return {
            "status": "validation_error",
            "errors": errors,
        }

    # ---------- Duplicate check (email or phone) ----------
    existing_lead = None
    if email_id:
        existing_lead = frappe.db.exists("Lead", {"email_id": email_id})
    if not existing_lead and phone:
        existing_lead = frappe.db.exists("Lead", {"phone": phone})

    if existing_lead:
        return {"status": "exists", "lead_id": existing_lead}

    # ---------- Create Lead + optional CRM Note ----------
    try:
        lead = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": lead_name,
            "email_id": email_id,
            "phone": phone,
        })
        lead.insert(ignore_permissions=True)

        if notes:
            safe_notes = escape_html(notes)
            crm_note = frappe.get_doc({
                "doctype": "CRM Note",
                "parent": lead.name,
                "parenttype": "Lead",
                "parentfield": "notes",
                "note": f"<div class='ql-editor read-mode'><p>{safe_notes}</p></div>",
                "added_by": "Guest",
            })
            crm_note.insert(ignore_permissions=True)

        frappe.db.commit()
        return {"status": "success", "lead_id": lead.name}

    except Exception as e:
        # Log the real traceback for you in the logs, but return clean JSON to the client
        frappe.log_error(frappe.get_traceback(), "Contact Form submit_contact failed")
        return {
            "status": "error",
            "message": "Internal error while saving your details. Please try again later.",
        }



# BLOCK PUBLIC ACCESS TO /app (Desk)


def block_desk_access():
    req = frappe.local.request
    path = (req.path or "")
    user = frappe.session.user

    # Allow static + API resources for everyone
    if path.startswith(("/assets", "/api", "/files")):
        return

    # ------------------- GUEST -------------------
    if user == "Guest":
        # Block login pages
        if path in ["/login", "/logout"]:
            raise SafeRedirect("/")

        # Block Desk entirely
        if path.startswith("/app"):
            raise SafeRedirect("/")

        # Guest browsing website pages is allowed
        return

    # ------------------- LOGGED-IN USER -------------------
    # Only allow Administrator full Desk access
    if user == "Administrator":
        # Admin can do everything
        return

    # Every other user — block Desk and login/logout pages
    if path.startswith("/app") or path in ["/login", "/logout"]:
        raise SafeRedirect("/")

    # They can still browse public website pages
    return


# =========================
# PUBLIC ROUTES + AUTOCORRECT
# =========================
PUBLIC_ROUTES = [
    "",      # root after rstrip("/")
    "/",     # explicit root
    "/index",
    "/about",
    "/services",
    "/careers",
    "/contact",
]


# =========================
# WEBSITE ROUTING HOOK
# (hook: website_before_render / website_route / etc.)
# =========================
def website_routing():
    request = frappe.local.request
    path = request.path or ""
    user = frappe.session.user

    # Allow assets + API always
    if path.startswith(("/api", "/assets", "/files")):
        return

    # Normalize path (remove trailing slash, lower-case)
    clean = path.rstrip("/").lower()

    # --------------------
    # 1. DESK + LOGIN ACCESS
    #    Only Administrator
    # --------------------
    if clean.startswith("/app") or clean in ["/login", "/logout"]:
        if user != "Administrator":
            # Non-admin (including Guest) → push them to homepage
            raise SafeRedirect("/")
        # Admin is allowed
        return

    # --------------------
    # 2. ROUTE NORMALIZATION
    # --------------------
    # /home → /
    if clean == "/home":
        raise SafeRedirect("/")

    # Internal paths (redundant safety)
    if clean.startswith(("/api", "/assets", "/files")):
        return

    # Already a valid public route
    if clean in PUBLIC_ROUTES:
        return

    # --------------------
    # 3. AUTO-CORRECT WRONG URLS
    # --------------------
    match = difflib.get_close_matches(clean, PUBLIC_ROUTES, n=1, cutoff=0.6)
    if match:
        target = match[0] or "/"   # if match is "" → redirect to "/"
        raise SafeRedirect(target)