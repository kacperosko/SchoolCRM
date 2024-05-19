function createNote() {
    const recordId = $('#recordId_addNoteForm').val();
    const modelName = $('#modelName_addNoteForm').val();
    const content = $('#content_addNoteForm')
    const close_button = $('#addNoteModal_closeWindow')
    const textAreaError = $('#addNoteModal_textAreaError')

    if (content.val().length < 1){
        textAreaError.text("Treść nie może być pusta");
        return;
    }

    $.ajax({
        url: '/crm_api/create-note',
        type: 'POST',
        data: {
            record_id: recordId,
            model_name: modelName,
            content: content.val(),
            csrfmiddlewaretoken: $(csrf_token).val(),
        },
        dataType: 'json',
        success: function (response) {
            if (response.status) {
                response.message = "Notatka dodana pomyślnie";
                handleResponse(response);
                content.val("");

                addNoteOnPage(response.note);
            }else {
                handleResponse(response);
            }
            close_button.trigger('click');
        },
        error: function (error) {
            console.error('Error creating note:', error);
            alert('Failed to create note.');
        }
    });
}

function addNoteOnPage(note_data) {
    const notes_container = $('#note-full-container');

    // Tworzenie nowego elementu div
    const new_note = $(`
        <div class="col-lg-4 col-md-6" style="">
            <div class="card card-body">
                <p class="font-12 text-muted">${note_data.created_at} ${note_data.created_by}</p>
                <div class="">
                    <p class="">
                        ${note_data.content}
                    </p>
                </div>
                <div class="d-flex align-items-center">
                    <div class="ml-auto">
                        <div class="btn-group">
                            <a class="nav-link dropdown-toggle category-dropdown label-group p-0"
                               data-toggle="dropdown" href="#" role="button" aria-haspopup="true"
                               aria-expanded="true">
                            </a>
                            <div class="dropdown-menu dropdown-menu-right">
                                <a class="badge-group-item dropdown-item position-relative text-info"
                                   href="#">
                                   Edytuj
                                </a>
                                <a class="badge-group-item dropdown-item position-relative text-danger"
                                   href="#;">
                                    Usuń
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `);

    notes_container.prepend(new_note);
}
