import matplotlib.pyplot as plt
import numpy as np

def plot_city_prices(simulation, city_name: str):
    """绘制城市商品价格历史"""
    if city_name not in simulation.cities:
        return
    
    city = simulation.cities[city_name]
    
    # 选择价格波动较大的商品进行展示
    price_volatility = {}
    for good, prices in city.price_history.items():
        if len(prices) > 1:
            price_volatility[good] = np.std(prices) / np.mean(prices)
    
    # 按价格波动排序，只展示波动最大的6种商品
    top_goods = sorted(price_volatility.items(), key=lambda x: x[1], reverse=True)[:6]
    top_goods = [good for good, _ in top_goods]
    
    plt.figure(figsize=(12, 6))
    for good in top_goods:
        prices = city.price_history[good]
        if len(prices) > 1:  # 确保有足够的数据点
            plt.plot(prices, label=good)
    
    plt.title(f"{city_name}的商品价格历史")
    plt.xlabel("天数")
    plt.ylabel("价格")
    plt.legend()
    plt.grid(True)

def plot_city_quality_distribution(city):
    """绘制城市商品质量分布"""
    plt.figure(figsize=(14, 8))
    
    # 准备数据
    goods = list(city.base_prices.keys())
    qualities = ["粗糙", "普通", "精良", "极品"]
    
    # 获取所有商品的质量分布数据
    data = []
    for good in goods:
        quality_amounts = []
        total = sum(city.inventory_by_quality[good].values())
        if total > 0:
            for quality in qualities:
                percentage = (city.inventory_by_quality[good].get(quality, 0) / total) * 100 if total > 0 else 0
                quality_amounts.append(percentage)
            data.append(quality_amounts)
        else:
            data.append([0, 0, 0, 0])  # 无库存的情况
    
    # 转置数据矩阵以便绘图
    data = np.array(data).T
    
    # 绘制堆叠柱状图
    bottom = np.zeros(len(goods))
    
    # 使用不同颜色表示不同质量
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    
    for i, quality in enumerate(qualities):
        plt.bar(goods, data[i], bottom=bottom, label=quality, color=colors[i])
        bottom += data[i]
    
    plt.title(f"{city.name}商品质量分布")
    plt.xlabel("商品")
    plt.ylabel("百分比 (%)")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def plot_ship_gold(simulation, ship_name: str):
    """绘制船只资金历史"""
    if ship_name not in simulation.ships:
        return
    
    ship = simulation.ships[ship_name]
    
    plt.figure(figsize=(10, 6))
    plt.plot(ship.gold_history)
    plt.title(f"{ship_name}的资金历史")
    plt.xlabel("天数")
    plt.ylabel("金币")
    plt.grid(True)
    
    # 添加事件标记
    events = [t for t in ship.trade_history if t["type"] == "route"]
    
    for i, event in enumerate(events):
        if i > 0 and i < len(ship.gold_history):
            try:
                day = events[i-1]["day"] if "day" in events[i-1] else i * 10  # 估计天数
                plt.axvline(x=day, color='r', linestyle='--', alpha=0.3)
                plt.text(day, ship.gold_history[i], f"{event['from']}->{event['to']}", 
                         fontsize=8, rotation=45, ha='right')
            except (IndexError, KeyError):
                pass  # 忽略数据不完整的情况

def plot_ship_trading_history(ship):
    """绘制船只交易历史和质量偏好"""
    if not ship.trade_history:
        return
        
    # 统计不同质量的交易量
    quality_counts = {"粗糙": 0, "普通": 0, "精良": 0, "极品": 0}
    locations = {}
    goods_traded = {}
    
    for trade in ship.trade_history:
        if "quality" in trade:
            quality = trade["quality"]
            if quality in quality_counts:
                quality_counts[quality] += trade["amount"]
                
        if "location" in trade:
            location = trade["location"]
            if location not in locations:
                locations[location] = 0
            locations[location] += 1
            
        if "good" in trade:
            good = trade["good"]
            if good not in goods_traded:
                goods_traded[good] = 0
            goods_traded[good] += trade["amount"]
    
    plt.figure(figsize=(15, 10))
    
    # 绘制质量分布图
    plt.subplot(221)
    qualities = list(quality_counts.keys())
    counts = list(quality_counts.values())
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    plt.pie(counts, labels=qualities, autopct='%1.1f%%', colors=colors)
    plt.title(f"{ship.name}交易的商品质量分布")
    
    # 绘制访问城市频率
    plt.subplot(222)
    cities = list(locations.keys())
    frequencies = list(locations.values())
    plt.bar(cities, frequencies)
    plt.title(f"{ship.name}访问城市频率")
    plt.xticks(rotation=45, ha='right')
    
    # 绘制交易商品数量
    plt.subplot(212)
    goods = list(goods_traded.keys())
    amounts = list(goods_traded.values())
    plt.bar(goods, amounts, color='skyblue')
    plt.title(f"{ship.name}交易商品数量")
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()

def plot_map(simulation):
    """绘制贸易地图"""
    plt.figure(figsize=(12, 10))
    
    # 绘制城市节点
    for city_name, (x, y) in simulation.trade_map.city_coords.items():
        plt.scatter(x, y, s=200, alpha=0.7)
        plt.text(x, y+5, city_name, ha='center', fontsize=10)
    
    # 绘制航线
    for (city_a, city_b), conditions in simulation.trade_map.route_conditions.items():
        if city_a in simulation.trade_map.city_coords and city_b in simulation.trade_map.city_coords:
            x1, y1 = simulation.trade_map.city_coords[city_a]
            x2, y2 = simulation.trade_map.city_coords[city_b]
            
            # 根据航线状态调整线条样式
            danger_level = conditions.get('危险度', 0)
            sea_condition = conditions.get('海况', 0)
            
            line_width = 1 + (1 - danger_level) * 2  # 危险程度越高，线越细
            
            # 根据海况选择线条样式
            if sea_condition > 0.6:  # 风暴频发
                line_style = ':'  # 暴风雨用点线
                color = 'blue'
            elif sea_condition > 0.4:  # 波涛汹涌
                line_style = '--'  # 雾用虚线
                color = 'gray'
            elif sea_condition < 0.2:  # 海面平静
                line_style = '-'  # 好天气用实线
                color = 'green'
            else:
                line_style = '-'
                color = 'black'
            
            plt.plot([x1, x2], [y1, y2], linestyle=line_style, 
                     linewidth=line_width, color=color, alpha=0.5)
            
            # 添加距离标记
            distance = simulation.trade_map.get_distance(city_a, city_b)
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            plt.text(mid_x, mid_y, f"{distance:.1f}", fontsize=8, 
                     ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))
    
    plt.title("贸易地图")
    plt.axis('equal')  # 保持比例
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 添加图例 - 修正格式问题
    plt.plot([], [], color='green', linestyle='-', label='晴朗')
    plt.plot([], [], color='blue', linestyle=':', label='暴风雨')
    plt.plot([], [], color='gray', linestyle='--', label='大雾')
    plt.legend(loc='best')

def plot_currency_history(simulation):
    """绘制货币系统历史数据"""
    # 绘制货币供应量历史
    plt.figure(figsize=(10, 6))
    plt.plot(simulation.currency_supply_history)
    plt.title("货币供应量历史")
    plt.xlabel("天数")
    plt.ylabel("供应量")
    plt.grid(True)
    
    # 绘制全局通货膨胀率历史
    plt.figure(figsize=(10, 6))
    plt.plot(simulation.global_inflation_history)
    plt.title("全局通货膨胀率历史")
    plt.xlabel("天数")
    plt.ylabel("通货膨胀率")
    plt.grid(True)
    
    # 绘制各城市货币价值历史
    plt.figure(figsize=(12, 6))
    for city_name, city in simulation.cities.items():
        plt.plot(city.currency_value_history, label=city_name)
    plt.title("各城市货币价值变化")
    plt.xlabel("天数")
    plt.ylabel("货币价值(相对标准)")
    plt.legend()
    plt.grid(True) 