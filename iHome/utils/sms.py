#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8a216da862cc8f910162dbe184ec0bab'

#主帐号Token
accountToken= 'c5e04de2b6f84a589b18bc6d3e9f540b'

#应用Id
appId='8a216da862cc8f910162dbe1853c0bb1'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'


class CCP(object):
    """封装单例类，用于统一的发送短信验证码"""
    _singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            cls._instance.rest = REST(serverIP,serverPort,softVersion)
            cls._instance.rest.setAccount(accountSid,accountToken)
            cls._instance.rest.setAppId(appId)

        return cls._instance

    def send_sms_msg(self, to, datas, tempId):
        """发送短信验证码的实例方法"""
        ret = self.rest.sendTemplateSMS(to, datas, tempId)

        if ret.get('statusCode') == '000000':
            return 1
        else:
            return 0



# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id
def sendTemplateSMS(to,datas,tempId):


    #初始化REST SDK
    rest = REST(serverIP,serverPort,softVersion)
    rest.setAccount(accountSid,accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(to,datas,tempId)
    for k,v in result.iteritems():

        if k=='templateSMS' :
                for k,s in v.iteritems():
                    print '%s:%s' % (k, s)
        else:
            print '%s:%s' % (k, v)

# 向17600992168发送短信验证码，内容为666666，5分钟后过期，使用id为1的模板
sendTemplateSMS('15917907641', ['611513', '5'], '1')