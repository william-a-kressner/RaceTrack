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