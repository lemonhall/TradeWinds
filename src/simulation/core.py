import random
from typing import List

from ..city import City
from ..ship import Ship
from ..map import TradeMap
from ..events import WeatherEvent, PirateEvent, CityEvent
from .update import update_simulation
from .trading import perform_trading_strategy
from .visualization import plot_city_prices, plot_ship_gold, plot_map

class TradeSimulation:
    def __init__(self, cities: List[City], ships: List[Ship], trade_map: TradeMap = None):
        self.cities = {city.name: city for city in cities}
        self.ships = {ship.name: ship for ship in ships}
        self.day = 0
        self.city_names = [city.name for city in cities]
        self.event_log = []
        
        # 初始化或使用提供的贸易地图
        if trade_map:
            self.trade_map = trade_map
        else:
            self.trade_map = self._generate_map(cities)
            
        self._init_events()
    
    def _generate_map(self, cities: List[City]) -> TradeMap:
        """生成贸易地图，设置城市坐标和距离"""
        trade_map = TradeMap()
        
        # 简单布局，将城市放在圆形布局上
        num_cities = len(cities)
        radius = 100
        center_x, center_y = 150, 150
        
        for i, city in enumerate(cities):
            # 计算圆形布局上的位置
            angle = 2 * 3.14159 * i / num_cities
            x = center_x + radius * random.uniform(0.8, 1.2) * random.uniform(0.8, 1.2) * 1.5 * round(0.9 + 0.2*random.random(), 1)
            y = center_y + radius * random.uniform(0.8, 1.2) * random.uniform(0.8, 1.2) * round(0.9 + 0.2*random.random(), 1)
            
            # 添加城市到地图
            trade_map.add_city(city.name, x, y)
        
        # 生成距离和航线状态
        trade_map.generate_distances()
        return trade_map
    
    def _init_events(self):
        """初始化随机事件列表"""
        self.weather_events = [
            WeatherEvent("暴风雨", "强烈的暴风雨减缓了船只的航行速度", 0.5, 3),
            WeatherEvent("大雾", "浓雾使船只不得不减速航行", 0.7, 2),
            WeatherEvent("顺风", "顺风加快了船只的航行速度", 1.5, 2),
            WeatherEvent("飓风", "强大的飓风几乎使船只无法航行", 0.3, 4),
            WeatherEvent("平静海域", "平静的海域使船只能够以适中的速度航行", 1.2, 3),
            WeatherEvent("梅雨季节", "连绵阴雨使航行变得困难", 0.6, 3),
            WeatherEvent("极光", "极光照亮夜空，船员士气高涨，加快航行", 1.3, 2)
        ]
        
        self.pirate_events = [
            PirateEvent("海盗袭击", "海盗抢劫了船上的部分货物和金钱", 0.2),
            PirateEvent("海盗围攻", "大群海盗围攻船只，造成重大损失", 0.4),
            PirateEvent("小型海盗", "小型海盗抢走了少量货物", 0.1),
            PirateEvent("巴巴里海盗", "凶猛的巴巴里海盗造成严重损失", 0.5),
            PirateEvent("海盗旗舰", "遭遇海盗旗舰，损失惨重", 0.6)
        ]
        
        self.city_events = [
            CityEvent("丰收", "农作物丰收使粮食价格下降", 0.7, ["粮食"]),
            CityEvent("矿产发现", "新矿产的发现使金属价格下降", 0.8, ["铁矿"]),
            CityEvent("贸易封锁", "贸易封锁导致商品价格上涨", 1.3),
            CityEvent("节日庆典", "节日庆典增加了奢侈品需求", 1.4, ["丝绸", "宝石", "香料", "香水", "葡萄酒"]),
            CityEvent("疾病爆发", "疾病爆发导致劳动力减少，商品价格上涨", 1.2),
            CityEvent("皇室采购", "皇室大量采购使珍稀品价格上涨", 1.5, ["瓷器", "珍珠", "玉石", "琥珀"]),
            CityEvent("茶叶流行", "茶叶成为上流社会新宠，价格上涨", 1.6, ["茶叶"]),
            CityEvent("手工业繁荣", "手工业繁荣使原材料需求增加", 1.3, ["羊毛", "丝绸", "铁矿"]),
            CityEvent("新航线开通", "新航线开通降低了运输成本", 0.85),
            CityEvent("药材短缺", "药材短缺导致价格飙升", 2.0, ["药材"]),
            CityEvent("香料战争", "香料战争导致香料价格波动剧烈", 1.8, ["香料", "香木"])
        ]
    
    def update(self):
        """更新模拟状态"""
        # 更新航线状态（每10天更新一次）
        if self.day % 10 == 0:
            self.trade_map.update_route_conditions()
            
        update_simulation(self)
        self.day += 1
    
    def perform_trading_strategy(self, ship):
        """执行交易策略"""
        perform_trading_strategy(self, ship)
        
    def run_simulation(self, days: int):
        """运行模拟"""
        # 初始化船只位置和路线
        self._init_ships()
        
        for _ in range(days):
            self.update()
            
    def _init_ships(self):
        """初始化船只状态"""
        for ship in self.ships.values():
            if not ship.current_city:
                start_city = random.choice(list(self.cities.values()))
                ship.current_city = start_city
                
            # 初始化船只的天气事件列表和原始速度
            ship.weather_events = []
            ship.original_speed = ship.speed
            ship.in_transit = False
            
            # 初始化资金历史记录
            if not ship.gold_history:
                ship.gold_history.append(ship.gold)
            
        # 让船只在初始城市先做一次决策
        for ship in self.ships.values():
            if ship.current_city:
                self.perform_trading_strategy(ship)
            
    def plot_city_prices(self, city_name: str):
        """绘制城市商品价格历史"""
        plot_city_prices(self, city_name)
    
    def plot_ship_gold(self, ship_name: str):
        """绘制船只资金历史"""
        plot_ship_gold(self, ship_name)
    
    def plot_map(self):
        """绘制贸易地图"""
        plot_map(self)
        
    def print_event_log(self):
        """打印事件日志"""
        for event in self.event_log:
            print(event)
            
    def get_route_info(self, city_a: str, city_b: str) -> dict:
        """获取两城市间航线信息"""
        distance = self.trade_map.get_distance(city_a, city_b)
        description = self.trade_map.get_route_description(city_a, city_b)
        conditions = self.trade_map.route_conditions.get((city_a, city_b), {})
        
        return {
            'from': city_a,
            'to': city_b,
            'distance': distance,
            'description': description,
            'conditions': conditions
        }
    
    def get_all_routes(self) -> List[dict]:
        """获取所有航线信息"""
        return [
            {
                'from': city_a,
                'to': city_b,
                'distance': data['distance'],
                'description': data.get('description', ''),
                'conditions': data.get('conditions', {})
            }
            for city_a, city_b, data in self.trade_map.get_all_routes()
        ] 