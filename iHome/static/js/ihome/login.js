function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $("#mobile").focus(function () {
        $("#mobile-err").hide();
    });
    $("#password").focus(function () {
        $("#password-err").hide();
    });
    // TODO: 添加登录表单提交操作
    $(".form-login").submit(function (e) {
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

        //　封装参数
        var params = {'mobile':mobile, 'passwd':passwd};

        $(".form-login").serializeArray().map(function (x) {
            params[x.name] = x.value
        });

        var jsonData = JSON.stringify(params);

        $.ajax({
            url: "/api/1.0/session",
            type: "post",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (data) {
                if ("0" == data.errno) {
                    // 登录成功，跳转到主页
                    location.href = "/";
                    return;
                }
                else {
                    // 其他错误信息，在页面中展示
                    $("#password-err span").html(data.errmsg);
                    $("#password-err").show();
                    return;
                }
            }
        });
    });


    function logout() {
        $.ajax({
            url: '/api/1.0/session',
            type: 'delete',
            headers: {"X-CSRFToken": getCookie("csrf_token")},
            datatype: 'json',
            success: function (resp) {
                if (resp.errno == "0") {
                    location.href = "/index.html";
                }
            }
        })
    }


});
