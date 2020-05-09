function teacherLogin() {
    var password = prompt("Please enter the password.");
    if (password === "duckies"){
        window.alert("Correct!");
        $.ajax({
            data : {status : "true"},
            type : 'POST',
            url : '/login_status'
        });
    }else {
        window.alert("Wrong!");
        $.ajax({
            data : {status : "false"},
            type : 'POST',
            url : '/login_status'
        });
    }
}