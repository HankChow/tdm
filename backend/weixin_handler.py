#!/usr/bin/env python3

import requests
import json

import config


class WeixinHandler(object):

    def __init__(self, agentid=None, corpsecret=None, corpid=None):
        self.agentid = agentid if agentid else config.WX_AGENTID
        self.corpsecret = corpsecret if corpsecret else config.WX_CORPSECRET
        self.corpid = corpid if corpid else config.WX_CORPID
        self.token = self.get_new_token()

    def get_new_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}'.format(
            corpid=self.corpid,
            secret=self.corpsecret
        )
        response = requests.get(url).text
        j = json.loads(response)
        if not j['errcode']:
            new_token = j['access_token']
            return new_token

    def get_userid_from_code(self, code):
        url = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={token}&code={code}".format(
            token=self.token,
            code=code
        )
        response = requests.get(url).text
        j = json.loads(response)
        if not j['errcode']:
            userid = j["UserId"]
            return userid

    def get_all_members(self):
        url = "https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token={token}&department_id=1&fetch_child=1".format(
            token=self.token
        )
        response = requests.get(url)
        try:
            if response.json()["errcode"] == 0:
                return [{"userid": item["userid"], "name": item["name"], "eng_name": item["alias"]} for item in response.json()["userlist"]]
        except:
            return None

    def send_notification(self, touser, title, description):
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}".format(
            token = self.token
	    )
        msg_data = json.dumps({
            "msgtype": "textcard",
            "agentid": self.agentid,
            "touser": touser,
            "enable_id_trans": 1,
            "textcard": {
                "title": title,
                "description": description,
                "url": config.WX_ENTRYURL
            }
        })
        response = requests.post(url, data=msg_data).json()
        return response