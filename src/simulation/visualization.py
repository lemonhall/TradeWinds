import matplotlib.pyplot as plt
import numpy as np

def plot_city_prices(simulation, city_name: str):
    """绘制城市商品价格历史"""
    city = simulation.cities[city_name]
    
    # 设置中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
    
    # 创建价格变化热图
    plt.figure(figsize=(14, 8))
    plt.subplot(211)  # 分成上下两个子图，上面是线图
    
    # 只显示价格波动较大的商品，避免图表过于拥挤
    price_changes = {}
    for good in city.base_prices:
        if len(city.price_history[good]) > 0:
            price_array = np.array(city.price_history[good])
            price_changes[good] = (np.max(price_array) - np.min(price_array)) / np.mean(price_array)
    
    # 选择价格波动最大的5种商品绘制
    top_goods = sorted(price_changes.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for good, _ in top_goods:
        plt.plot(city.price_history[good], label=good)
    
    plt.title(f"{city_name}价格历史（波动最大的商品）")
    plt.xlabel("天数")
    plt.ylabel("价格")
    plt.legend()
    plt.grid()
    
    # 创建热图，显示所有商品的价格波动
    plt.subplot(212)
    
    # 对所有商品的价格历史数据进行标准化处理
    normalized_data = []
    goods_list = []
    
    for good in city.base_prices:
        if len(city.price_history[good]) > 0:
            price_array = np.array(city.price_history[good])
            if np.max(price_array) != np.min(price_array):  # 避免除零错误
                normalized = (price_array - np.min(price_array)) / (np.max(price_array) - np.min(price_array))
                normalized_data.append(normalized)
                goods_list.append(good)
    
    if normalized_data:
        data_matrix = np.vstack(normalized_data)
        plt.imshow(data_matrix, aspect='auto', cmap='viridis')
        plt.colorbar(label='标准化价格')
        plt.yticks(range(len(goods_list)), goods_list)
        plt.title(f"{city_name}所有商品价格热图")
        plt.xlabel("天数")
    
    plt.tight_layout()
    plt.show()
    
    # 绘制商品质量分布图
    plot_city_quality_distribution(city)

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
    ship = simulation.ships[ship_name]
    
    # 设置中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
    
    plt.figure(figsize=(12, 6))
    plt.plot(ship.gold_history)
    plt.title(f"{ship_name}资金历史")
    plt.xlabel("交易次数")
    plt.ylabel("金币")
    plt.grid()
    
    # 添加平均增长趋势线
    if len(ship.gold_history) > 1:
        x = np.arange(len(ship.gold_history))
        z = np.polyfit(x, ship.gold_history, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), "r--", label=f"增长趋势: {z[0]:.2f}/次")
        plt.legend()
    
    plt.show()
    
    # 绘制船只交易历史和商品质量偏好图
    plot_ship_trading_history(ship)

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
    """绘制贸易地图，显示城市位置和航线"""
    # 设置中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
    
    plt.figure(figsize=(12, 10))
    
    # 获取城市坐标
    city_coords = simulation.trade_map.city_coords
    
    # 绘制城市
    for city_name, (x, y) in city_coords.items():
        plt.plot(x, y, 'ro', markersize=10)
        plt.text(x+5, y+5, city_name, fontsize=12)
    
    # 绘制航线
    routes = simulation.get_all_routes()
    for route in routes:
        from_city, to_city = route['from'], route['to']
        x1, y1 = city_coords[from_city]
        x2, y2 = city_coords[to_city]
        
        # 获取航线状态来确定线条颜色
        conditions = route.get('conditions', {})
        danger = conditions.get('危险度', 0.3)
        
        # 颜色由绿色(安全)到红色(危险)渐变
        color = (danger, 1-danger, 0)
        
        # 绘制航线
        plt.plot([x1, x2], [y1, y2], '-', color=color, alpha=0.7, linewidth=1.5)
        
        # 在航线中间添加距离标签
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        distance = route.get('distance', 0)
        plt.text(mid_x, mid_y, f'{distance:.1f}', fontsize=8, 
                 bbox=dict(facecolor='white', alpha=0.7))
    
    # 添加船只位置
    for ship_name, ship in simulation.ships.items():
        if ship.current_city and ship.current_city.name in city_coords:
            city_name = ship.current_city.name
            x, y = city_coords[city_name]
            plt.plot(x, y, 'b^', markersize=8)
            plt.text(x-5, y-10, ship_name, fontsize=8, color='blue')
    
    plt.title('贸易地图')
    plt.xlabel('X 坐标')
    plt.ylabel('Y 坐标')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.axis('equal')  # 确保比例一致
    
    # 创建图例
    plt.plot([], [], 'ro', label='城市')
    plt.plot([], [], 'b^', label='船只位置')
    plt.plot([], [], '-g', label='安全航线')
    plt.plot([], [], '-r', label='危险航线')
    plt.legend()
    
    plt.tight_layout()
    plt.show() 