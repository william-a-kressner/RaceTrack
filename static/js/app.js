$(document).ready( function () {
    document.getElementById("logout-button").addEventListener("click", logout, false);
});

function logout() {
    window.alert("Log out successful. Refresh this page.");
    $.ajax({
        data : {},
        type : 'POST',
        url : '/logout'
    })
}

function submitStudent() {
    $.ajax({
        data : {
            student_name : $('#student_name').val(),
            tasks_completed : $('#tasks_completed').val()
        },
        type : 'POST',
        url : '/process'
    })
}

function deleteRacecar(id){
    $.ajax({
        data : {
            id : id
        },
        type : 'POST',
        url : '/delete'
    })
}

function incrementRacecar(id) {
    $.ajax({
        data : {
            id : id
        },
        type : 'POST',
        url : '/increment'
    });
    id = id.substring(0, id.length-10);
    //console.log(id);
    var current = parseInt(document.getElementById("num_tasks_"+id).innerText);
    current++;
    //console.log(current.toString());
    document.getElementById("num_tasks_"+id).innerText = current.toString();
}