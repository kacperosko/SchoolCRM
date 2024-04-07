const alertStack = [];

function handleResponse(response) {
    const alertContainer = document.getElementById('alertContainer');
    let alertHTML = '';
    if (response.status === true) {
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

    // Dodaj alert na wierzch stosu
    alertStack.push(alertHTML);
    renderAlerts();
}

function renderAlerts() {
    const alertContainer = document.getElementById('alertContainer');
    alertContainer.innerHTML = ''; // Wyczyść kontener

    // Dodaj alerty w kolejności od najnowszego do najstarszego
    for (let i = alertStack.length - 1; i >= 0; i--) {
        alertContainer.innerHTML += alertStack[i];
    }

    // Usuń alerty po 3 sekundach
    setTimeout(function () {
        alertStack.shift(); // Usuń najstarszy alert ze stosu
        renderAlerts(); // Odśwież widok alertów
    }, 3000);
}

// const jsonResponse1 = {
//     "status": true,
//     "message": "test  <b>primary</b> alert"
// };
//
// handleResponse(jsonResponse1)