document.getElementById("contactForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    let form = e.target;
    let box = document.getElementById("contactResponse");

    let url = `/api/method/lyncspace_app.api.submit_contact?lead_name=${encodeURIComponent(form.lead_name.value)}&email_id=${encodeURIComponent(form.email_id.value)}&phone=${encodeURIComponent(form.phone.value)}&notes=${encodeURIComponent(form.note.value)}`;

    try {
        let res = await fetch(url);
        let r = await res.json();

        let response = await res.json();

        if (response.message && response.message.message === "success") {
            box.innerHTML = `<div class="alert alert-success">Message sent successfully!</div>`;
            form.reset();
        } else {
            throw new Error("Failed");
        }

    } catch (err) {
        box.innerHTML = `<div class="alert alert-danger">Error: ${err}</div>`;
    }
});
