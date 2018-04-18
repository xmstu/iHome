function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
// 定义一个成员变量用于记录上一次的验证码编号
var preImageCodeId = "";

var imageCodeId = "";
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 1. 生成一个编号
    // 严格一点的使用uuid保证编号唯一,不是很严谨的情况下,也可以使用时间戳
    imageCodeId = generateUUID();

    alert(imageCodeId);
    // 2.　拼接验证码地址
    var imageCodeUrl = "/api/v1.0/image_code?cur=" + imageCodeId;

    // 3. 设置页面中图片验证码img标签的src属性
    $(".image-code>img").attr("src", imageCodeUrl);

    // 4. 将当前生成的编号进行保存,用于下一次请求传入
    preImageCodeId = imageCodeId;

}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO: 通过ajax方式向后端接口发送请求，让后端发送短信验证码
}

$(document).ready(function() {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // TODO: 注册的提交(判断参数是否为空)
});
