from pymongo import MongoClient





# ------------修改集合名即可----------------
collection_name = "doc_slice256"



# MongoDB 认证信息
username = "chuangdata"
password = "Hjklzxc0505"
host = "192.168.110.238"
port = 27017
auth_db = "admin"
# 连接 MongoDB
client = MongoClient(f"mongodb://{username}:{password}@{host}:{port}/{auth_db}")
mongo_db = client["data"]
collection = mongo_db[collection_name]



# 获取集合中字段的信息
sample = collection.find_one()
if not sample:
    print("集合为空，无法生成模型")
    exit()

# 映射 MongoDB 字段类型到 Django 字段类型
field_mapping = {
    str: "StringField()",
    int: "IntField()",
    float: "FloatField()",
    bool: "BooleanField()",
    list: "ListField()",
    dict: "DictField()",
    type(None): "StringField(null=True)",  # 处理可能为 null 的字段
}

# 构建 Django 模型代码
model_name = collection_name
model_code = f"class {model_name}(Document):\n"

for field, value in sample.items():
    if field == "_id":
        model_code += f"    {field} = ObjectIdField(primary_key=True)\n"
    else:
        field_type = field_mapping.get(type(value), "StringField()")
        model_code += f"    {field} = {field_type}\n"

# 输出 Django 模型代码
print("生成的 Django 模型代码如下：\n")
print(model_code)
