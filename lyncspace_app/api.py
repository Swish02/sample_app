import frappe
@frappe.whitelist(allow_guest=True)
def submit_contact(lead_name, email_id=None, phone=None, notes=None):
    # Create the Lead
    lead = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": lead_name,
        "email_id": email_id,
        "phone": phone
    })
    lead.insert(ignore_permissions=True)

    # Insert into CRM Note (Lead > Notes Tab)
    if notes:
        crm_note = frappe.get_doc({
            "doctype": "CRM Note",
            "parent": lead.name,
            "parenttype": "Lead",
            "parentfield": "notes",
            "note": f"<div class='ql-editor read-mode'><p>{notes}</p></div>",
            "added_by": "Guest"
        })
        crm_note.insert(ignore_permissions=True)

    frappe.db.commit()
    return {"status": "success", "lead_id": lead.name}