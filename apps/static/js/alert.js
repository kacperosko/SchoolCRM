const alertStack = [];

function handleResponse(response) {
    let alertHTML = '';
    if (response.status === true || response.status === 'success') {
        alertHTML = `
            <div class="alert text-white bg-success" role="alert">
                <div class="iq-alert-text">` + response.message + `</div>
            </div>
        `;
    } else {
        alertHTML = `
            <div class="alert text-white bg-danger" role="alert">
                <div class="iq-alert-text">` + response.message + `</div>
            </div>
        `;
    }

    alertStack.push(alertHTML);
    renderAlerts();
}

function addInformAlert(message) {
    let alertHTML = `
            <div class="alert text-white bg-info" role="alert">
                <div class="iq-alert-text">` + message + `</div>
            </div>
        `;
    alertStack.push(alertHTML);
    renderAlerts();
}

function renderAlerts() {
    const alertContainer = document.getElementById('alertContainer');
    alertContainer.innerHTML = '';

    for (let i = alertStack.length - 1; i >= 0; i--) {
        alertContainer.innerHTML += alertStack[i];
    }

    setTimeout(function () {
        alertStack.shift();
        renderAlerts();
    }, 6000);
}
