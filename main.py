import random
import matplotlib.pyplot as plt
import matplotlib as mpl

from src.city import City
from src.ship import Ship
from src.simulation import TradeSimulation

# 配置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

# 示例使用
if __name__ == "__main__":
    # 定义商品
    goods = [
        "香料", "丝绸", "宝石", "铁矿", "粮食", 
        "瓷器", "茶叶", "香木", "药材", "珍珠",
        "玉石", "琥珀", "香水", "葡萄酒", "羊毛"
    ]
    
    # 城市特产描述
    city_specialties = {
        "里斯本": ["葡萄酒", "羊毛", "铁矿"],
        "威尼斯": ["丝绸", "香水", "玻璃制品"],
        "君士坦丁堡": ["香料", "丝绸", "瓷器"],
        "亚历山大": ["香料", "药材", "宝石"],
        "热那亚": ["葡萄酒", "丝绸", "铁矿"],
        "巴塞罗那": ["葡萄酒", "香水", "羊毛"],
        "亚丁": ["香料", "香木", "珍珠"]
    }
    
    # 创建城市
    cities = [
        City("里斯本", 
             {"香料": 50, "丝绸": 100, "宝石": 500, "铁矿": 20, "粮食": 5,
              "瓷器": 300, "茶叶": 40, "香木": 80, "药材": 150, "珍珠": 400,
              "玉石": 450, "琥珀": 200, "香水": 120, "葡萄酒": 30, "羊毛": 15},
             {"香料": 10, "铁矿": 50, "粮食": 200, "葡萄酒": 80, "羊毛": 100},
             {"丝绸": 15, "宝石": 5, "铁矿": 30, "粮食": 180, "香水": 20}),
        
        City("威尼斯", 
             {"香料": 60, "丝绸": 80, "宝石": 450, "铁矿": 30, "粮食": 8,
              "瓷器": 350, "茶叶": 35, "香木": 70, "药材": 160, "珍珠": 450,
              "玉石": 500, "琥珀": 220, "香水": 100, "葡萄酒": 25, "羊毛": 20},
             {"丝绸": 20, "宝石": 8, "香水": 25, "葡萄酒": 90},
             {"香料": 12, "丝绸": 18, "宝石": 10, "铁矿": 25, "粮食": 150, "香木": 15}),
        
        City("君士坦丁堡", 
             {"香料": 40, "丝绸": 120, "宝石": 400, "铁矿": 25, "粮食": 6,
              "瓷器": 400, "茶叶": 45, "香木": 60, "药材": 140, "珍珠": 420,
              "玉石": 480, "琥珀": 180, "香水": 110, "葡萄酒": 35, "羊毛": 18},
             {"香料": 15, "丝绸": 15, "粮食": 180, "茶叶": 30, "药材": 25},
             {"香料": 8, "丝绸": 20, "宝石": 7, "铁矿": 40, "粮食": 200, "珍珠": 10}),
             
        City("亚历山大", 
             {"香料": 45, "丝绸": 110, "宝石": 420, "铁矿": 28, "粮食": 7,
              "瓷器": 380, "茶叶": 50, "香木": 75, "药材": 130, "珍珠": 380,
              "玉石": 470, "琥珀": 190, "香水": 95, "葡萄酒": 40, "羊毛": 22},
             {"香料": 20, "药材": 30, "香水": 30},
             {"丝绸": 25, "宝石": 12, "铁矿": 35, "粮食": 170, "琥珀": 15}),
             
        City("热那亚", 
             {"香料": 55, "丝绸": 90, "宝石": 480, "铁矿": 22, "粮食": 9,
              "瓷器": 320, "茶叶": 38, "香木": 85, "药材": 145, "珍珠": 430,
              "玉石": 460, "琥珀": 210, "香水": 105, "葡萄酒": 20, "羊毛": 16},
             {"葡萄酒": 70, "羊毛": 90, "铁矿": 45},
             {"香料": 14, "丝绸": 22, "宝石": 9, "铁矿": 20, "瓷器": 15}),
             
        City("巴塞罗那", 
             {"香料": 58, "丝绸": 95, "宝石": 460, "铁矿": 26, "粮食": 10,
              "瓷器": 360, "茶叶": 42, "香木": 78, "药材": 155, "珍珠": 410,
              "玉石": 490, "琥珀": 205, "香水": 115, "葡萄酒": 28, "羊毛": 12},
             {"葡萄酒": 85, "香水": 35},
             {"香料": 16, "丝绸": 17, "宝石": 8, "粮食": 160, "香木": 18, "羊毛": 80}),
             
        City("亚丁", 
             {"香料": 35, "丝绸": 130, "宝石": 390, "铁矿": 32, "粮食": 12,
              "瓷器": 370, "茶叶": 32, "香木": 90, "药材": 125, "珍珠": 440,
              "玉石": 510, "琥珀": 195, "香水": 125, "葡萄酒": 45, "羊毛": 25},
             {"香料": 25, "香木": 35, "珍珠": 15},
             {"茶叶": 20, "宝石": 6, "粮食": 190, "瓷器": 18, "药材": 28}),
    ]
    
    # 设置各城市特产
    for city in cities:
        if city.name in city_specialties:
            # 强制设置城市特产
            city.specialty_goods = set(city_specialties[city.name])
    
    # 创建船只
    ships = [
        Ship("海蛇号", capacity=100, speed=3),
        Ship("海狮号", capacity=150, speed=2),
        Ship("黄金鹿号", capacity=120, speed=4),
        Ship("北极星号", capacity=200, speed=2),
        Ship("龙骑士号", capacity=180, speed=3),
        Ship("风暴使者号", capacity=130, speed=5),
        Ship("宝藏号", capacity=250, speed=1),
    ]
    
    # 打印船只质量偏好
    print("====== 船只质量偏好 ======")
    for ship in ships:
        print(f"{ship.name}: {'偏好高质量' if ship.quality_preference == '质量' else '偏好低价'}")
    
    # 打印城市特产
    print("\n====== 城市特产 ======")
    for city in cities:
        specialty_list = list(city.specialty_goods)
        print(f"{city.name}: {', '.join(specialty_list)}")
    
    # 创建并运行模拟
    simulation = TradeSimulation(cities, ships)
    simulation.run_simulation(days=365)  # 模拟一年
    
    # 打印事件日志
    print("\n====== 模拟期间发生的随机事件 ======")
    simulation.print_event_log()
    
    # 打印商品质量分布
    print("\n====== 商品质量分布 ======")
    for city in cities:
        print(f"\n{city.name}:")
        for good in goods:
            qualities = city.get_available_qualities(good)
            if qualities:
                print(f"  {good}: ", end="")
                for quality, amount in qualities.items():
                    print(f"{quality}({amount:.1f}) ", end="")
                print()
    
    # 绘制结果
    simulation.plot_city_prices("里斯本")
    simulation.plot_ship_gold("海蛇号")
    simulation.plot_ship_gold("海狮号")
    
    # 分析利润最高的商品
    print("\n====== 船只交易分析 ======")
    for ship_name, ship in simulation.ships.items():
        if not ship.trade_history:
            continue
            
        profits_by_good = {}
        quality_profits = {"粗糙": 0, "普通": 0, "精良": 0, "极品": 0}
        
        buy_transactions = [t for t in ship.trade_history if t["type"] == "buy"]
        sell_transactions = [t for t in ship.trade_history if t["type"] == "sell"]
        
        for buy in buy_transactions:
            good = buy["good"]
            if good not in profits_by_good:
                profits_by_good[good] = {"买入总额": 0, "卖出总额": 0, "利润": 0}
            profits_by_good[good]["买入总额"] += buy["amount"] * buy["price"]
            
        for sell in sell_transactions:
            good = sell["good"]
            if good in profits_by_good:
                profits_by_good[good]["卖出总额"] += sell["amount"] * sell["price"]
                profits_by_good[good]["利润"] = profits_by_good[good]["卖出总额"] - profits_by_good[good]["买入总额"]
                
            quality = sell["quality"]
            if quality in quality_profits:
                quality_profits[quality] += sell["amount"] * sell["price"]
        
        print(f"\n{ship_name}的交易分析:")
        sorted_goods = sorted(profits_by_good.items(), key=lambda x: x[1]["利润"], reverse=True)
        for good, data in sorted_goods[:3]:  # 只显示前3名
            if data["买入总额"] > 0:
                profit_margin = (data["利润"] / data["买入总额"]) * 100
                print(f"  {good}: 利润 {data['利润']:.1f} 金币 (利润率: {profit_margin:.1f}%)")
        
        print(f"  质量收益分析:")
        for quality, profit in quality_profits.items():
            if profit > 0:
                print(f"    {quality}: {profit:.1f} 金币")
    
    plt.show() # 显示所有图表 