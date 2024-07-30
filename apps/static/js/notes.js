function createNote() {
    const recordId = $('#recordId_addNoteForm').val();
    const noteId = $('#notedId_upsertNoteForm').val();
    const content = $('#content_upsertNoteForm')
    const close_button = $('#addNoteModal_closeWindow')
    const textAreaError = $('#addNoteModal_textAreaError')

    if (content.val().length < 1) {
        textAreaError.text("Tre\u015B\u0107 nie mo\u017Ce by\u0107 pusta");
        return;
    }

    $.ajax({
        url: '/crm_api/create-note',
        type: 'POST',
        data: {
            record_id: recordId,
            note_id: noteId,
            content: content.val(),
            csrfmiddlewaretoken: $(csrf_token).val(),
        },
        dataType: 'json',
        success: function (response) {
            if (response.status) {
                response.message = "Notatka " +  (noteId === "" ? "dodana" : "zaktualizowana") + " pomy\u015Blnie";
                handleResponse(response);
                content.val("");

                if (noteId)
                    $("#note_"+noteId).remove();

                addNoteOnPage(response.note);

            } else {
                handleResponse(response);
            }
            close_button.trigger('click');
        },
        error: function (error) {
            console.error('Error upserting note:', error);
            alert('Failed to upsert note.');
        }
    });
}

function addNoteOnPage(note_data) {
    const notes_container = $('#note-full-container');
    const empty_notes_info = $('#empty-notes-info');
    if (empty_notes_info !== undefined) {
        empty_notes_info.hide();
    }

    const new_note = $(`
        <div class="col-lg-4 col-md-6" style="" id="note_${note_data.note_id}">
            <div class="card card-body">
                <p class="font-12 text-muted" id="${note_data.note_id}_createdInfo">${note_data.created_at} ${note_data.created_by}</p>
                <div class="">
                    <p class=""  id="${note_data.note_id}_content">${note_data.content}</p>
                </div>
                <div class="d-flex align-items-center">
                    <div class="ml-auto">
                            <div class="btn-group">
                                <a class="btn text-primary  dropdown-item position-relative "
                                   type="button" data-toggle="modal"
                                   data-target="#upsertNoteModalCenter" onclick="show_edit_modal('${note_data.note_id}')">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                         stroke-width="1"
                                         stroke="currentColor" class="w-6 h-6 mr-1" width="18">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                              d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
                                    </svg>
                                </a>
   
                                <a class="btn text-danger badge-group-item dropdown-item position-relative text-danger"
                                   type="button" data-toggle="modal"
                                   data-target="#deleteNoteModalCenter" onclick="show_delete_modal('${note_data.note_id}')">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                         stroke-width="1.5"
                                         stroke="currentColor" class="w-6 h-6 mr-1" width="18">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                              d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"></path>
                                    </svg>
                                </a>
                            </div>
                        </div>
                </div>
            </div>
        </div>
    `);

    notes_container.prepend(new_note);

}

function delete_note(note_id) {
    $.ajax({
        url: '/crm_api/delete-note',
        type: 'POST',
        data: {
            note_id: note_id,
            csrfmiddlewaretoken: $(csrf_token).val(),
        },
        dataType: 'json',
        success: function (response) {
            if (response.status) {
                response.message = "Notatka usuni\u0119ta pomy\u015Blnie";
                handleResponse(response);

                const note_element = document.getElementById('note_' + note_id);
                note_element.remove();

                const empty_notes_info = $('#empty-notes-info');
                const notes_container = $('#note-full-container');

                if (empty_notes_info !== undefined && notes_container.children().length < 1) {
                    empty_notes_info.show();
                }


            } else {
                handleResponse(response);
            }
            $('#deleteNote_closeWindow').click();
        },
        error: function (error) {
            console.error('Error creating note:', error);
            alert('Failed to delete note.');
        }
    });
}


function show_delete_modal(note_id) {
    let content = $('#'+note_id+'_content');
    let createdInfo = $('#'+note_id+'_createdInfo');

    $('#deleteNoteCreatedInfo').text(createdInfo.text());
    $('#deleteNoteContent').text(content.text());
    $('#deleteNoteId').val(note_id);
}

function show_edit_modal(note_id){
    let content = $('#'+note_id+'_content');

    $('#content_upsertNoteForm').val(content.text());
    $('#notedId_upsertNoteForm').val(note_id);
}

function show_create_modal(){
    if ($('#notedId_upsertNoteForm').val() !== ""){
        $('#content_upsertNoteForm').val('');
        $('#notedId_upsertNoteForm').val('');
    }
}