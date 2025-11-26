import re
import frappe
from frappe.utils import validate_email_address, escape_html


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
    elif len(notes.split()) < 10:
        errors["notes"] = "Message must be at least 10 words."

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
