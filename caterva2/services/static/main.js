function activate(selector, trigger) {
    const url = new URL(document.URL);
    for (el of document.querySelectorAll(selector)) {
        if (trigger === undefined) {
            const href = new URL(el.href)
            if (url.pathname.startsWith(href.pathname)) {
                el.classList.add("active");
            }
            else {
                el.classList.remove("active");
            }
        }
        else {
            if (trigger == el) {
                el.classList.add("active");
            }
            else {
                el.classList.remove("active");
            }
        }
    }
}

function clearContent(elementID) {
    document.getElementById(elementID).innerHTML = "";
}

async function _submitForm(form, successURL, resultElementID, asJSON) {
    const result = document.getElementById(resultElementID);
    result.replaceChildren();  // empty the result view

    const params = {};
    for (const field of form.elements)
        if (field.name != "")
            params[field.name] = field.value;

    const response = await fetch(
        form.action, {
            method: form.method,
            headers: {'Content-Type': (asJSON ? 'application/json'
                                       : 'application/x-www-form-urlencoded')},
            body: (asJSON ? JSON.stringify(params)
                   : new URLSearchParams(params))},
    );

    if (response.ok) {
        window.location.href = successURL;
        return;
    }

    const json = await response.json();
    const resd = document.createElement("div");
    resd.setAttribute("class", "alert alert-danger");
    resd.appendChild(document.createTextNode("Submission failed: "));
    resd.appendChild(document.createElement("code"))
        .textContent = `${response.status} ${response.statusText}`;
    resd.appendChild(document.createElement("pre"))
        .textContent = JSON.stringify(json);
    result.replaceChildren(resd);
}

async function submitForm(form, successURL, resultElementID="result") {
    return await _submitForm(form, successURL, resultElementID, false);
}

async function submitFormAsJSON(form, successURL, resultElementID="result") {
    return await _submitForm(form, successURL, resultElementID, true);
}
