#!/usr/bin/env python3

import time

from mongo_handler import MongoHandler
from weixin_handler import WeixinHandler

import config


def update_members():
    st = time.time()
    mh = MongoHandler(collection="members")
    wh = WeixinHandler(corpsecret=config.WX_MEMBERS_CORPSECRET)
    all_members = wh.get_all_members()
    if all_members:
        mh.collection.delete_many({})
        mh.collection.insert_many(all_members)


if __name__ == "__main__":
    update_members()
