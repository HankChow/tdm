#!/usr/bin/env python3

import datetime
import json
import logging
import time

from bson.objectid import ObjectId
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import config

from mongo_handler import MongoHandler
from weixin_handler import WeixinHandler


app = FastAPI()
cors_headers = {
    "Access-Control-Allow-Origin": "{protocol}://{url}:{port}".format(
        protocol=config.FRONTEND_PROTOCOL,
        url=config.FRONTEND_URL,
        port=config.FRONTEND_PORT
    ),
    "Access-Control-Allow-Methods": "POST"    
}
executor = ThreadPoolExecutor(5)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] [%(process)d-%(thread)d] %(asctime)s - %(message)s")


class NewToDo(BaseModel):
    user_id: str
    sender: str
    receiver: str
    content: str
    start_time: datetime.datetime
    expected_finish_time: datetime.datetime


class ListToDo(BaseModel):
    user_id: str


class DeleteToDo(BaseModel):
    user_id: str
    todo_id: str
    

class FinishToDo(BaseModel):
    user_id: str
    todo_id: str
    actual_finish_time: datetime.datetime

class UserCode(BaseModel):
    code: str


@app.get("/api/ping")
def ping():
    logging.debug("Received a ping, return a pong.")
    return {"msg": "pong"}


# TODO: to check whether the todo belongs to the user_id
@app.post("/api/add")
def add_todo(todo: NewToDo):
    logging.info("/add called. postdata: " + str(todo))
    new_todo = {
        "sender": todo.sender,
        "receiver": todo.receiver,
        "content": todo.content,
        "start_time": todo.start_time,
        "expected_finish_time": todo.expected_finish_time,
        "actual_finish_time": "",
        "status": 0,
        "is_visible": True
    }
    mh = MongoHandler()
    inserted = mh.collection.insert_one(new_todo)
    if inserted:
        logging.info("New todo added. id: {}".format(str(inserted.inserted_id)))
        executor.submit(WeixinHandler().send_notification, todo.receiver, "新待办通知", "<div>$userName={userid}$ 新增了待办：{content}</div>".format(
            userid=todo.receiver,
            content=todo.content
        ))
        return JSONResponse(content={"msg": "ok", "id": str(inserted.inserted_id)}, headers=cors_headers)
    else:
        logging.error("Adding todo failed.")
        return JSONResponse(content={"msg": "error"}, headers=cors_headers)


@app.post("/api/list_sent")
def list_sent_todo(todo: ListToDo):
    logging.info("/list_sent called. postdata: " + str(todo))
    mh = MongoHandler()
    todos = list(mh.collection.find({"sender": todo.user_id, "is_visible": True}, {"is_visible": 0}))
    for i in range(len(todos)):
        todos[i]["_id"] = str(todos[i]["_id"])
        todos[i]["expected_finish_time"] = str(todos[i]["expected_finish_time"])
        todos[i]["start_time"] = str(todos[i]["start_time"])
    return JSONResponse(content={"data": todos}, headers=cors_headers)


@app.post("/api/list_received")
def list_received_todo(todo: ListToDo):
    logging.info("/list_received called. postdata: " + str(todo))
    mh = MongoHandler()
    todos = list(mh.collection.find({"receiver": todo.user_id, "is_visible": True, "status": 0}, {"is_visible": 0}))
    for i in range(len(todos)):
        todos[i]["_id"] = str(todos[i]["_id"])
        todos[i]["expected_finish_time"] = str(todos[i]["expected_finish_time"])
        todos[i]["start_time"] = str(todos[i]["start_time"])
    return JSONResponse(content={"data": todos}, headers=cors_headers)


@app.post("/api/delete")
def delete_todo(todo: DeleteToDo):
    logging.info("/delete called. postdata: " + str(todo))
    mh = MongoHandler()
    mh.collection.update_one({
        "_id": ObjectId(todo.todo_id),
        "sender": todo.sender
    }, {
        "$set": {
            "is_visible": False
        } 
    })
    return JSONResponse(content={"msg": "ok", "id": todo.todo_id}, headers=cors_headers)


@app.post("/api/finish")
async def finish_todo(todo: FinishToDo):
    logging.info("/finish called. postdata: " + str(todo))
    mh = MongoHandler()
    mh.collection.update_one({
        "_id": ObjectId(todo.todo_id),
        "receiver": todo.receiver
    }, {
        "$set": {
            "status": 1,
            "actual_finish_time": todo.actual_finish_time.isoformat()
        } 
    })
    finished_todo = list(mh.collection.find({"_id": ObjectId(todo.todo_id), "is_visible": True}, {"sender": 1, "actual_finish_time": 1, "content": 1}))[0]
    logging.info("finished_todo: " + str(finished_todo))
    executor.submit(WeixinHandler().send_notification, finished_todo["sender"], "待办完成通知", "<div>$userName={userid}$ 已完成待办：{content}</div>".format(
        userid=finished_todo["sender"],
        content=finished_todo["content"]
    ))
    return JSONResponse(content={"msg": "ok", "id": todo.todo_id}, headers=cors_headers)


@app.post("/api/usercode")
def usercode(code: UserCode):
    logging.info("/usercode called. postdata: " + str(code))
    wh = WeixinHandler()
    user_id = wh.get_userid_from_code(code.code)
    if user_id:
        logging.info(code.code + " -> " + user_id)
        return JSONResponse(content={"msg": "ok", "user_id": user_id}, headers=cors_headers)


@app.post("/api/list_members")
def list_members():
    logging.info("/list_members called.")
    mh = MongoHandler(collection="members")
    members = list(mh.collection.find({}, {"_id": 0}))
    return JSONResponse(content={"msg": "ok", "members": members}, headers=cors_headers)
