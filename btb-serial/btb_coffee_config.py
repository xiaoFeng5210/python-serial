from enum import Enum

# 咖啡机运行状态
btb_coffee_state_dict = {
    "0": "INIT",  # 初始化状态
    "1": "IDLE",  # 空闲状态
    "2": "RUNNING",  # 运行状态
    "3": "TURN_OFF",  # 关机状态
}


# 故障码
btb_coffee_error_dict = {
    "20": "蒸汽锅炉温度过低",
    "21": "咖啡锅炉温度过高",
    "22": "蒸汽锅炉温度过高",
    "23": "",
    "24": "咖啡管路堵塞",
    "25": "常温水管路堵塞",
    "26": "1号磨豆系统异常",
    "27": "2号磨豆系统异常",
    "30": "1号咖啡豆用尽",
    "31": "2号咖啡豆用尽",
    "32": "1投放口开关异常",
    "33": "2投放口开关异常",
    "34": "配料1用尽",
    "35": "配料2用尽",
    "36": "进水口压力异常",
    "37": "请关闭酿造门",
    "40": "冲泡器未安装",
    "41": "奶路3缺奶",
    "42": "奶路1缺奶",
    "43": "需要安装蓄水盘",
    "44": "蓄水盘水满",
    "45": "渣满",
    "46": "冲泡器故障",
    "47": "酿造压力过大",
    "60": "3号咖啡豆用尽",
    "61": "搅拌器未安装",
    "62": "即热式咖啡锅炉断线",
    "63": "即热式咖啡锅炉NTC故障",
    "64": "即热式咖啡锅炉温度过低",
    "65": "即热式咖啡锅炉温度过高",
    "66": "投放口故障",
    "67": "奶路2缺奶",
    "200": "冲泡器电机过热",
    "201": "管路漏水",
    "202": "豆仓光电检测1",
    "203": "豆仓光电检测2",
    "204": "豆仓光电检测3",
    "205": "豆仓1未安装",
    "206": "豆仓2未安装",
    "207": "豆仓3未安装",
    "210": "豆仓拉手未到位",
    "211": "粉料搅拌仓未安装",
}


class CoffeeDrinkName(Enum):
    # 意式浓缩
    ESPRESSO = "ESPRESSO"
    # 双杯意式咖啡
    DOUBLE_ESPRESSO = "DOUBLE_ESPRESSO"
    # 美式咖啡
    AMERICANO = "AMERICANO"
    # 冰美式咖啡
    ICE_AMERICANO = "ICE_AMERICANO"
    # 卡布奇诺
    CAPPUCCINO = "CAPPUCCINO"
    # 拿铁玛奇朵
    LATTE_MACCHIATO = "LATTE_MACCHIATO"
    # 拿铁咖啡
    LATTE = "LATTE"
    # 热奶沫
    HOT_MILK_FOAM = "HOT_MILK_FOAM"
    # 克利马咖啡
    CLIMATE_COFFEE = "CLIMATE_COFFEE"
    # 芮斯崔朵
    RISTRETTO = "RISTRETTO"
    # 馥芮白
    FRAPPUCCINO = "FRAPPUCCINO"
    # 清式咖啡
    CLEAN_COFFEE = "CLEAN_COFFEE"
    # 热牛奶
    HOT_MILK = "HOT_MILK"
    # 热水
    HOT_WATER = "HOT_WATER"
    # 欧蕾咖啡
    AULA_COFFEE = "AULA_COFFEE"
    # 大壶咖啡
    LARGE_COFFEE = "LARGE_COFFEE"


# 饮品的编号
btb_coffee_drink_dict = {
    CoffeeDrinkName.ESPRESSO: 1,
    CoffeeDrinkName.DOUBLE_ESPRESSO: 2,
    CoffeeDrinkName.AMERICANO: 3,
    CoffeeDrinkName.ICE_AMERICANO: 4,
    CoffeeDrinkName.CAPPUCCINO: 5,
    CoffeeDrinkName.LATTE_MACCHIATO: 6,
    CoffeeDrinkName.LATTE: 7,
    CoffeeDrinkName.HOT_MILK_FOAM: 8,
    CoffeeDrinkName.CLIMATE_COFFEE: 9,
    CoffeeDrinkName.RISTRETTO: 10,
    CoffeeDrinkName.FRAPPUCCINO: 11,
    CoffeeDrinkName.CLEAN_COFFEE: 12,
    CoffeeDrinkName.HOT_MILK: 13,
    CoffeeDrinkName.HOT_WATER: 14,
    CoffeeDrinkName.AULA_COFFEE: 15,
    CoffeeDrinkName.LARGE_COFFEE: 16,
}


# 清洗类型
clean_type_desc = {
    1: "酿造核心快速冲洗",
    2: "牛奶系统自动冲洗",
    3: "预热冲洗",
    4: "配料管路快速冲洗",
    5: "牛奶出口管路自动冲洗",
}
