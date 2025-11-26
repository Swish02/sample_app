frappe.pages['ly'].on_page_load = function(wrapper) {
    const target_url = "/index";  // or "/lyni.html" or whatever your homepage route is
    window.location.href = target_url;
};

