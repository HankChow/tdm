# tdm
To-do Management

### 配置文件
需要将以下内容配置到 `backend/config.py`:
```
# MongoDB 主机
MONGODB_HOST = ""
# MongoDB 端口，默认 27017
MONGODB_PORT = 27017
# MongoDB 数据库名
MONGODB_DB = ""
# MongoDB 集合名
MONGODB_COLLECTION = ""

# 前端页面访问协议，http 或 https
FRONTEND_PROTOCOL = ""
# 前端页面域名
FRONTEND_URL = ""
# 前端页面端口
FRONTEND_PORT = ""

# 企业微信应用 ID
WX_AGENTID = ""
# 企业微信应用 Secret
WX_CORPSECRET = ""
# 企业微信公司 ID
WX_CORPID = ""
# 企业微信卡片跳转页面
WX_ENTRYURL = r""
# 企业微信通信录 Secret
WX_MEMBERS_CORPSECRET = ""
```
