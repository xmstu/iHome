#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '8a216da862cc8f910162dbe184ec0bab'

#���ʺ�Token
accountToken= 'c5e04de2b6f84a589b18bc6d3e9f540b'

#Ӧ��Id
appId='8a216da862cc8f910162dbe1853c0bb1'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'


class CCP(object):
    """��װ�����࣬����ͳһ�ķ��Ͷ�����֤��"""
    _singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            cls._instance.rest = REST(serverIP,serverPort,softVersion)
            cls._instance.rest.setAccount(accountSid,accountToken)
            cls._instance.rest.setAppId(appId)

        return cls._instance

    def send_sms_msg(self, to, datas, tempId):
        """���Ͷ�����֤���ʵ������"""
        ret = self.rest.sendTemplateSMS(to, datas, tempId)

        if ret.get('statusCode') == '000000':
            return 1
        else:
            return 0



# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
# @param $tempId ģ��Id
def sendTemplateSMS(to,datas,tempId):


    #��ʼ��REST SDK
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

# ��17600992168���Ͷ�����֤�룬����Ϊ666666��5���Ӻ���ڣ�ʹ��idΪ1��ģ��
sendTemplateSMS('15917907641', ['611513', '5'], '1')