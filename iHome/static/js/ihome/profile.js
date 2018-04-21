function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // TODO: 在页面加载完毕向后端查询用户的信息
    $.get('/api/1.0/users', function (response) {
        if (response.errno == '0') {
            $('#user-avatar').attr('src', response.data.avatar_url);
            $('#user-name').val(response.data.name);
        }
        else {
            alert(response.errmsg);
        }
    });

    // TODO: 管理上传用户头像表单的行为
    $('#form-avatar').submit(function (event) {
        // 禁用表单自己的提交行为
        event.preventDefault();

        // 模拟表单的提交行为:方便读取input里面的file数据,不需要自己写代码
        $(this).ajaxSubmit({
            url: '/api/1.0/users/avatar',
            type: 'post',
            contentType: 'application/json',
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            success: function (response) {
                if (response.errno == '0') {
                    // 渲染用户头像
                    $('#user-avatar').attr('src', response.data);
                }
                else {
                    alert(response.errmsg);
                }
            }
        });
    });

    // TODO: 管理用户名修改的逻辑
    $('#form-name').submit(function (event) {
        event.preventDefault();
        var new_name = $('#user-name').val();
        if (!new_name){
            alert('请输入用户名');
        }

        var params = {'name':new_name};

        $.ajax({
            url: '/api/1.0/users/name',
            type: 'put',
            data: JSON.stringify(params),
            contentType: 'application/json',
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            success: function (response) {
                if (response.errno == '0') {
                    //
                    showSuccessMsg();
                }
                else if (response.errno == '4101'){
                    location.href = 'login.html';
                }
                else {
                    alert(response.errmsg);
                }
            }
        })
    });


});

