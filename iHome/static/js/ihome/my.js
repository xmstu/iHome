function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// TODO: 点击退出按钮时执行的函数
function logout() {
    $.ajax({
        url: '/api/1.0/session',
        type: 'delete',
        headers: {"X-CSRFToken": getCookie("csrf_token")},
        datatype: 'json',
        success: function (resp) {
            if (resp.errno == "0") {
                location.href = "/";
            }
            else if (resp.errno == '4101'){
                location.href = 'login.html';
            }
            else {
                alert(resp.errmsg);
            }
        }
    })
}

$(document).ready(function () {

    // TODO: 在页面加载完毕之后去加载个人信息
    $.get('/api/1.0/users', function (resp) {
        if (resp.errno == '0'){
            $('#user-avatar').attr('src', resp.data.avatar_url);
            $('#user-name').html(resp.data.name);
            $('#user-mobile').html(resp.data.mobile);
        } else if (resp.errno == '4101'){
            location.href = 'login.html';
        }
        else {
            alert(resp.errmsg);
        }
    })
});
