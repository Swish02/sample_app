const form = document.getElementById("contactForm");
const box  = document.getElementById("contactResponse");
let submitting = false;


// -------- helper: clear old errors --------
function clearErrors() {
    document.querySelectorAll(".error-text").forEach(p => p.innerText = "");
}


// -------- helper: show error under the input --------
function showFieldError(field, msg) {
    const target = document.querySelector(`[data-error-for="${field}"]`);
    if (target) target.innerText = msg;
}


form.addEventListener("submit", async function (e) {
    e.preventDefault();

    if (submitting) return;
    submitting = true;

    clearErrors();
    box.innerHTML = "";

    const lead_name = form.lead_name.value.trim();
    const email_id  = form.email_id.value.trim();
    const phone     = form.phone.value.trim();
    const notes     = form.note.value.trim();

    const localErrors = {};

    // ------ Name ------
    if (!lead_name) {
        localErrors.lead_name = "Name is required.";
    } else if (!/^[A-Za-z ]+$/.test(lead_name)) {
        localErrors.lead_name = "Only letters allowed. Numbers not allowed.";
    }

    // ------ Email ------
    if (!email_id) {
        localErrors.email_id = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email_id)) {
        localErrors.email_id = "Enter a valid email address.";
    }

    // ------ Phone ------
    if (!phone) {
        localErrors.phone = "Phone number is required.";
    } else if (!/^\d{10}$/.test(phone)) {
        localErrors.phone = "Phone must be 10 digits.";
    } else if (phone === "0000000000") {
        localErrors.phone = "Please enter a valid phone number.";
    }

    // ------ Message ------
    if (!notes) {
        localErrors.notes = "Message is required.";
    } else if (notes.split(/\s+/).length < 10) {
        localErrors.notes = "Message must be at least 10 words.";
    }

    // ---------- If frontend errors: show under inputs ----------
    if (Object.keys(localErrors).length > 0) {
        Object.entries(localErrors).forEach(([field, msg]) => {
            showFieldError(field, msg);
        });
        submitting = false;
        return;
    }


    // ---------- Call API ----------
    const url = `/api/method/lyncspace_app.api.submit_contact`
        + `?lead_name=${encodeURIComponent(lead_name)}`
        + `&email_id=${encodeURIComponent(email_id)}`
        + `&phone=${encodeURIComponent(phone)}`
        + `&notes=${encodeURIComponent(notes)}`;

    try {
        const res = await fetch(url);
        const data = await res.json();
        const payload = data.message || data;

        if (payload.status === "success") {
            box.innerHTML = `
                <div class="alert alert-success">
                    Message sent successfully.
                </div>`;
            form.reset();
        }

        else if (payload.status === "exists") {
            showFieldError("email_id", "This email is already registered.");
            showFieldError("phone", "This phone number is already registered.");
        }

        else if (payload.status === "validation_error") {
            // backend validation → show each under input
            Object.entries(payload.errors).forEach(([field, msg]) => {
                showFieldError(field, msg);
            });
        }

        else {
            throw new Error("Unexpected server response.");
        }

    } catch (err) {
        box.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
    }

    submitting = false;
});
