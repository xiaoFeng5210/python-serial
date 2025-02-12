import json
import os

from btb_coffee_config import (
    CoffeeDrinkName,
    btb_coffee_drink_dict,
    btb_coffee_error_dict,
    btb_coffee_state_dict,
)

"""
  以后使用这个函数直接拿到所有解析的数据。然后进行逻辑处理。
  觉得不方便也可以在这个函数里改。
  msg是所有的中文信息(list), code是数字码(list): 以后前端用来做国际化

  解析整体思路是：
  1. 拿到数据字节(数据1, 数据2, 数据3, 数据4 ...)部分
  2. 把字节部分通过byte_to_binary函数转换为二进制字符串
  3. 针对二进制字符串每个进行解析，拿到具体数据信息
  4. 把具体数据信息放到response中作为返回值

  Args:
    data: bytes
"""


def read_btb_coffee_status(data: bytes):
    response = {
        # 设备状态还有设备故障信息, 故障信息没有msg为空
        "device": {
            "status": "NORMAL",
            "code": [],
            "msg": [],
        },
        # 运行状态还有其他信息放这里
        "maintain": {
            "progress": 0,
            "msg": [],
            "code": [],
        },
        # 饮品是否可做
        "material": {"can_not_make": []},
    }
    data1_binary_str = byte_to_binary(data[0])
    res1 = parse_data1(data1_binary_str)
    response["device"]["status"] = res1["device"]["status"]
    response["maintain"]["status"] = res1["maintain"]["status"]

    # 数据2，数据3，数据4。设备相关故障信息处理
    device_res = parse_device_abnormal_status(data)
    response["device"]["code"] = device_res["code"]
    response["device"]["msg"] = device_res["msg"]

    # 拿到饮品制作进度或者初始化进度(数据5)
    data5_binary_str = byte_to_binary(data[4])
    data5 = parse_data5(data5_binary_str)
    response["maintain"]["progress"] = data5

    # 拿到运行中状态信息(数据6)
    data6_binary_str = byte_to_binary(data[5])
    data6 = parse_data6(data6_binary_str)
    response["maintain"]["code"] = data6["code"]
    response["maintain"]["msg"] = data6["msg"]

    can_make_list, can_not_make_list = drink_can_make(data)
    response["material"]["can_not_make"] = can_not_make_list
    can_not_make_drink_name(can_not_make_list)

    data20_binary_str = byte_to_binary(data[19])
    data20 = parse_data20(data20_binary_str)
    if len(data20["code"]) > 0:
        response["maintain"]["code"].extend(data20["code"])
        response["maintain"]["msg"].extend(data20["msg"])

    data21_binary_str = byte_to_binary(data[20])
    data21 = parse_data21(data21_binary_str)
    if len(data21["code"]) > 0:
        response["maintain"]["code"].extend(data21["code"])
        response["maintain"]["msg"].extend(data21["msg"])

    print(f"read_btb_coffee_status: {response}")
    return response


def parse_data1(binary_str: str):
    bits = list(binary_str)
    bits.reverse()
    json_data1 = {
        "device": {
            "status": "NORMAL",
        },
        "maintain": {
            "status": "初始化状态",
        },
    }
    json_data1["device"]["status"] = "NORMAL" if bits[0] == "0" else "ABNORMAL"
    maintain_status_data = bits[2] + bits[1]
    if maintain_status_data == "00":
        json_data1["maintain"]["status"] = btb_coffee_state_dict["0"]
    elif maintain_status_data == "01":
        json_data1["maintain"]["status"] = btb_coffee_state_dict["1"]
    elif maintain_status_data == "10":
        json_data1["maintain"]["status"] = btb_coffee_state_dict["2"]
    elif maintain_status_data == "11":
        json_data1["maintain"]["status"] = btb_coffee_state_dict["3"]

    return json_data1


def parse_data2(binary_str: str):
    bits = list(binary_str)
    bits.reverse()
    data2 = {
        "code": [],
        "msg": [],
    }
    for i in range(len(bits)):
        if bits[i] == "1":
            data2["code"].append(20 + i)
            data2["msg"].append(btb_coffee_error_dict[str(20 + i)])
    return data2


def parse_data3(binary_str: str):
    bits = list(binary_str)
    bits.reverse()
    data3 = {
        "code": [],
        "msg": [],
    }
    for i in range(len(bits)):
        if bits[i] == "1":
            data3["code"].append(30 + i)
            data3["msg"].append(btb_coffee_error_dict[str(30 + i)])
    return data3


def parse_data4(binary_str: str):
    bits = list(binary_str)
    bits.reverse()
    data4 = {
        "code": [],
        "msg": [],
    }
    for i in range(len(bits)):
        if bits[i] == "1":
            data4["code"].append(40 + i)
            data4["msg"].append(btb_coffee_error_dict[str(40 + i)])
    return data4


# 解析咖啡机饮品制作进度（0～100），数据5
def parse_data5(binary_str: str) -> int:
    progress = int(binary_str, 2)
    # 确保进度在0 - 100之间
    progress = min(100, max(0, progress))
    return progress


# 解析数据6，运行状态的故障信息
def parse_data6(binary_str: str) -> dict:
    # 将二进制字符串转为列表并反转，使得索引与bit位对应
    bits = list(binary_str)
    bits.reverse()

    errors = {
        "code": [],
        "msg": [],
    }
    # 检查每个位的故障情况
    if bits[0] == "1":
        errors["code"].append(60)
        errors["msg"].append(btb_coffee_error_dict["60"])

    if bits[1] == "1":
        errors["code"].append(61)
        errors["msg"].append(btb_coffee_error_dict["61"])

    if bits[2] == "1":
        errors["code"].append(62)
        errors["msg"].append(btb_coffee_error_dict["62"])

    if bits[3] == "1":
        errors["code"].append(63)
        errors["msg"].append(btb_coffee_error_dict["63"])

    if bits[4] == "1":
        errors["code"].append(64)
        errors["msg"].append(btb_coffee_error_dict["64"])

    if bits[5] == "1":
        errors["code"].append(65)
        errors["msg"].append(btb_coffee_error_dict["65"])

    if bits[6] == "1":
        errors["code"].append(66)
        errors["msg"].append(btb_coffee_error_dict["66"])

    if bits[7] == "1":
        errors["code"].append(67)
        errors["msg"].append(btb_coffee_error_dict["67"])

    return errors


# 解析设备device的故障信息
def parse_device_abnormal_status(data: str):
    binary_str2 = byte_to_binary(data[1])
    binary_str3 = byte_to_binary(data[2])
    binary_str4 = byte_to_binary(data[3])

    res = {
        "code": [],
        "msg": [],
    }
    data2 = parse_data2(binary_str2)
    data3 = parse_data3(binary_str3)
    data4 = parse_data4(binary_str4)

    res["code"] = [*data2["code"], *data3["code"], *data4["code"]]
    res["msg"] = [*data2["msg"], *data3["msg"], *data4["msg"]]
    return res


def drink_can_make(data: str):
    all_list = []
    for i in range(13):
        binary_str = byte_to_binary(data[6 + i])
        binary_list = list(binary_str)
        binary_list.reverse()
        all_list.append(binary_list)

    can_make_list = []
    can_not_make_list = []

    for dataIndex, dataList in enumerate(all_list):
        for index, value in enumerate(dataList):
            drink_id = dataIndex * 8 + index + 1
            if value == "1":
                # 无法制作
                can_not_make_list.append(drink_id)
            else:
                can_make_list.append(drink_id)
    return can_make_list, can_not_make_list


def parse_data20(binary_str: str):
    bits = list(binary_str)
    bits.reverse()
    data20 = {
        "code": [],
        "msg": [],
    }
    for i in range(len(bits)):
        if bits[i] == "1":
            data20["code"].append(20 + i)
            data20["msg"].append(btb_coffee_error_dict[str(20 + i)])
    return data20


def parse_data21(binary_str: str):
    bits = list(binary_str)
    bits.reverse()
    data21 = {
        "code": [],
        "msg": [],
    }
    for i in range(len(bits)):
        if bits[i] == "1":
            data21["code"].append(21 + i)
            data21["msg"].append(btb_coffee_error_dict[str(21 + i)])
    return data21


def read_file(file_path: str):
    """读取文件"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return None


def write_file(file_path: str, data):
    """写入文件"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"写入文件失败: {str(e)}")


def crc16(bytes, invert=True):
    a = 0xFFFF
    b = 0xA001
    for byte in bytes:
        a ^= byte
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    s = hex(a).upper()[2:]
    s = (4 - len(s)) * "0" + s
    return s[2:4] + s[0:2] if invert == True else s


def byte_to_binary(byte: int):
    binary = bin(byte)[2:].zfill(8)
    return binary


def can_not_make_drink_name(can_not_make_list: list):
    can_not_make_drink_name_list = []
    for drink_id in can_not_make_list:
        for drink_name in CoffeeDrinkName:
            if btb_coffee_drink_dict[drink_name] == drink_id:
                can_not_make_drink_name_list.append(drink_name.value)
    return can_not_make_drink_name_list
