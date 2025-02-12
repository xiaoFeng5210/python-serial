import threading
import time

import serial
import serial.tools.list_ports
from btb_coffee_config import btb_coffee_drink_dict, clean_type_desc
from btb_coffee_utils import read_btb_coffee_status
from utils import *
from utils import logger

# 测试数据011A5502000000000000000000000000000000000000000072FF，帮我写成bytes类型
# 测试故障数据 011A55030000090000FFFF0000000000000000000000007AFF
test_status_response = bytes.fromhex(
    "011A5502000000000000000000000000000000000000000072FF"
)


coffee_lock = threading.Lock()  # 准备一个读的互斥锁

BAUDRATE = 115200
BYTESIZE = 8
PARITY = "N"
STOPBITS = 1
TIMEOUT = 0.2  # 1秒超时

"""
新咖啡机通讯
"""


class BTBCoffeeSerial:
    # 命令码定义
    CMD_STATUS = 0x01  # 状态查询
    CMD_PARAM = 0x02  # 参数查询与设置
    CMD_POWER_OFF = 0x03  # 关机
    CMD_MAKE = 0x04  # 制作饮品

    # 常量定义
    INSTRUCTION_QUERY = 0x55  # 查询指令
    INSTRUCTION_SET = 0xAA  # 设置指令

    END_CODE = 0xFF  # 结束码

    CLEAN_TYPE_BREW_CORE = 1  # 酿造核心快速冲洗
    CLEAN_TYPE_MILK_SYS = 2  # 牛奶系统自动冲洗
    CLEAN_TYPE_PREHEAT = 3  # 预热冲洗
    CLEAN_TYPE_POWDER = 4  # 配料管路快速冲洗
    CLEAN_TYPE_MILK_OUT = 5  # 牛奶出口管路自动冲洗

    def __init__(self, port):
        # 初始化串口
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=115200,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=1,
            )
            print(f"✅ 串口 {port} 打开成功")
        except Exception as e:
            print(f"初始化串口失败: {str(e)}")

    def send_command(self, cmd_type, cmd_code, data=None):
        """发送命令并等待响应
        cmd_type: 命令码
        cmd_code: 指令码
        data: 数据
        """
        with coffee_lock:  # 加锁
            if data is None:
                data = []
            # 构建消息
            message = [cmd_type]  # 命令码(查询/设置)
            data_part = [cmd_code] + (data if isinstance(data, list) else [data])
            length = len(data_part) + 4

            # 组装完整消息
            message.append(length)  # 长度码
            message.extend(data_part)  # 指令码和数据

            # 计算校验码（除校验码和结束码外所有数据之和的低8位）
            checksum = sum(message) & 0xFF
            message.append(checksum)  # 校验码
            message.append(self.END_CODE)  # 结束码

            # 发送数据
            for retry in range(4):  # 最多重试3次
                try:
                    # 清空缓冲区
                    self.ser.reset_input_buffer()
                    self.ser.reset_output_buffer()
                    self.ser.write(bytes(message))  # 发送数据
                    print(f"> 发送: {bytes(message).hex().upper()}")
                    self.ser.flush()
                    time.sleep(0.2)  # 等待一段时间确保数据发送完成

                    # 读取响应
                    response = self.read_rst()
                    if response:
                        return response
                    else:
                        return None

                except Exception as e:
                    print(f"通讯错误: {str(e)}")

            # FIXME:通讯失败 返回None
            print("通讯失败, 达到最大重试次数")
            return None

    # 获取数据字节部分
    def get_data_byte(self, response: bytes) -> bytes:
        if response:
            return response[3:-2]
        else:
            return None

    def read_rst(self):
        try:
            # 读取数据
            byte_head = self.ser.read(3)  # 头部
            byte_data = self.ser.read(21)  # 数据
            byte_verify = self.ser.read(1)  # 校验码
            byte_end = self.ser.read(1)  # 结束符

            # 组合数据
            response = byte_head + byte_data + byte_verify + byte_end

            # 打印调试信息
            print(f"📥 接收: {response.hex().upper()} ({len(response)}字节)")

            # 验证数据
            if len(response) < 3:
                print("❌ 数据长度不足")
                return None

            if response[-1] != self.END_CODE:
                print(f"❌ 结束符不满足预期: 期望{self.END_CODE}, 实际{response[-1]}")
                return None

            return response
        except Exception:
            return None

    # 具体功能实现
    def query_status(self):
        """查询状态"""
        response = self.send_command(self.CMD_STATUS, self.INSTRUCTION_QUERY)
        if response:
            data = self.get_data_byte(response)  # 获取数据字节部分
            if data:
                return read_btb_coffee_status(data)
        return None

    def query_params(self):
        """查询参数"""
        return self.send_command(self.CMD_PARAM, self.INSTRUCTION_QUERY)

    def set_params(self, params):
        """设置参数"""
        return self.send_command(self.CMD_PARAM, self.INSTRUCTION_SET, params)

    def make(self, drink_id):
        """出饮品
        数据1: 0x00 出饮品 其他为清洗
        Args:
            drink_id: 饮品编号 1~50
        Returns:
            returned_drink_id: 出饮品编号
            success: 是否成功
        """
        if not 1 <= drink_id <= 50:
            logger.error(f"❌ 饮品编号错误: {drink_id}")
            return drink_id, False
        response = self.send_command(
            self.CMD_MAKE, self.INSTRUCTION_SET, [0x00, drink_id]
        )
        returned_drink_id = 0
        if response:
            data = self.get_data_byte(response)
            if data and len(data) >= 2:
                returned_drink_id = data[0]
                if data[1] == 0x01:
                    return returned_drink_id, True
                elif data[1] == 0x00:
                    return returned_drink_id, False
        return returned_drink_id, False

    def make_drink_from_name(self, drink_name):
        """出饮品
        Args:
            drink_name: 饮品name
        Returns:
            returned_drink_name: 出饮品name
            success: 是否成功
        """

        if drink_name not in btb_coffee_drink_dict:
            logger.error(f"❌ 暂无该饮品: {drink_name.value}")
            return drink_name.value, False

        drink_id = btb_coffee_drink_dict[drink_name]
        _, is_success = self.make(drink_id)
        if is_success:
            logger.info(f"✅ 出饮品成功: {drink_name.value}")
            return drink_name.value, True
        else:
            logger.error(f"❌ 出饮品失败: {drink_name.value}")
            return drink_name.value, False

    def close_machine(self):
        response = self.send_command(self.CMD_POWER_OFF, self.INSTRUCTION_SET)
        if response:
            # 获取数据部分（数据1）
            data = self.get_data_byte(response)
            if data and len(data) > 0:
                if data[0] == 0x01:
                    print("✅ 关闭咖啡机成功")
                    return True
                elif data[0] == 0x00:
                    print("❌ 关闭咖啡机失败：设备可能处于故障状态")
                    return False

        print("❌ 关闭咖啡机失败：通信错误")
        return False

    # 关闭串口
    def close_serial(self):
        self.ser.close()

    def query_status_loop(self):
        while True:
            try:
                if self.ser.is_open:
                    coffee.query_status()
                    time.sleep(3.0)
                else:
                    print("❌ 串口未打开")
            except Exception as e:
                print(f"程序错误: {str(e)}")

    def clean_machine(self, clean_type: int) -> bool:
        if clean_type not in clean_type_desc:
            logger.error(f"清洗类型错误: {clean_type}")
            return False

        logger.info(f"开始: {clean_type_desc[clean_type]}")
        response = self.send_command(
            self.CMD_MAKE,  # 命令码 0x04
            self.INSTRUCTION_SET,  # 指令码 0xAA
            [clean_type, 0x00],  # [数据1=清洗类型，饮品编号(清洗时无效)]
        )
        if response:
            data = self.get_data_byte(response)
            if data and len(data) >= 2:
                status = data[1]  # 状态（0x00失败，0x01成功）

                if status == 0x01:
                    logger.info(f"✅ {clean_type_desc[clean_type]}开始执行")
                    return True
                else:
                    logger.error(f"❌ {clean_type_desc[clean_type]}执行失败")
                    return False
        logger.error(f"清洗失败: {response.hex().upper()}")
        return False


if __name__ == "__main__":
    coffee = BTBCoffeeSerial("/dev/ttyS3")
    thread_eq = threading.Thread(target=coffee.query_status_loop, args=(), daemon=True)
    thread_eq.start()

    # drink_name, success = coffee.make_drink_from_name(CoffeeDrinkName.ESPRESSO)
    # print(f"出饮品: {drink_name}, 是否成功: {'成功' if success else '失败'}")

    # time.sleep(5)

    # drink_name, success = coffee.make_drink_from_name(CoffeeDrinkName.ESPRESSO)
    # print(f"出饮品: {drink_name}, 是否成功: {'成功' if success else '失败'}")

    while True:
        time.sleep(1.0)
