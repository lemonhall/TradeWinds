import random
import math
from typing import Dict, List, Tuple

class TradeMap:
    """管理城市之间的地理关系、距离和航线"""
    
    def __init__(self):
        # 城市间距离表 {(city_a, city_b): distance}
        self.distances = {}
        # 航线状态 {(city_a, city_b): {'危险度': float, '风向优势': float, '海况': float}}
        self.route_conditions = {}
        # 城市坐标 {city_name: (x, y)}
        self.city_coords = {}
        
    def add_city(self, city_name: str, x: float, y: float):
        """添加城市到地图并设定坐标"""
        self.city_coords[city_name] = (x, y)
        
    def generate_distances(self):
        """根据坐标生成城市间距离"""
        city_names = list(self.city_coords.keys())
        
        for i, city_a in enumerate(city_names):
            for city_b in city_names[i+1:]:
                x_a, y_a = self.city_coords[city_a]
                x_b, y_b = self.city_coords[city_b]
                
                # 使用欧几里得距离
                distance = math.sqrt((x_b - x_a)**2 + (y_b - y_a)**2)
                
                # 添加距离（双向）
                self.distances[(city_a, city_b)] = distance
                self.distances[(city_b, city_a)] = distance
                
                # 初始化航线状态
                # 风向优势：0为逆风，1为顺风；海况：0为平静，1为风暴
                ab_route = {
                    '危险度': random.uniform(0.1, 0.5),  # 0-1 之间，越高越危险（海盗、暗礁等）
                    '风向优势': random.uniform(0.3, 0.8),  # 0-1 之间，越高风向越有利
                    '海况': random.uniform(0.1, 0.4)   # 0-1 之间，越高海况越恶劣
                }
                self.route_conditions[(city_a, city_b)] = ab_route
                
                # 相反方向的航线可能有不同的风向优势
                ba_route = ab_route.copy()
                ba_route['风向优势'] = random.uniform(0.2, 0.7)  # 不同方向风向不同
                self.route_conditions[(city_b, city_a)] = ba_route
    
    def get_distance(self, city_a: str, city_b: str) -> float:
        """获取两城市间的距离"""
        if (city_a, city_b) in self.distances:
            return self.distances[(city_a, city_b)]
        return float('inf')  # 如果没有直接连接，返回无穷大
    
    def calculate_travel_time(self, city_a: str, city_b: str, ship_speed: float) -> float:
        """计算船只航行所需时间（天）"""
        distance = self.get_distance(city_a, city_b)
        if distance == float('inf'):
            return float('inf')
            
        # 获取航线状态
        route = self.route_conditions.get((city_a, city_b), {'风向优势': 0.5, '海况': 0.2})
        wind_advantage = route['风向优势']
        sea_condition = route['海况']
        
        # 风向影响速度：顺风加速，逆风减速
        wind_factor = 0.5 + wind_advantage  # 0.5-1.5的因子
        
        # 海况恶劣减慢速度
        sea_factor = 1 - sea_condition  # 0.6-0.9的因子
        
        # 有效速度 = 基础速度 * 风向因子 * 海况因子
        effective_speed = ship_speed * wind_factor * sea_factor
        
        # 基础时间 = 距离/速度，四舍五入到0.5天
        travel_time = round(distance / effective_speed * 2) / 2
        return max(1, travel_time)  # 至少需要1天
    
    def calculate_route_cost(self, city_a: str, city_b: str, ship_size: float) -> float:
        """
        计算航线成本（船员工资、补给、港口费用等）
        :param ship_size: 船只大小因子（影响成本）
        """
        distance = self.get_distance(city_a, city_b)
        if distance == float('inf'):
            return float('inf')
            
        # 基础成本与距离成正比
        base_cost = distance * 2.0
        
        # 港口费用（与船只大小成正比）
        port_fee = 10 + ship_size * 5
        
        # 船员工资（与距离和船只大小成正比）
        crew_wage = distance * 0.5 * ship_size
        
        # 补给成本（食物、水等，与距离和船只大小成正比）
        supplies_cost = distance * 0.8 * ship_size
        
        # 航线危险度增加成本（保险、额外护卫等）
        route = self.route_conditions.get((city_a, city_b), {'危险度': 0.0})
        danger_factor = route['危险度']
        danger_cost = base_cost * danger_factor
        
        return base_cost + port_fee + crew_wage + supplies_cost + danger_cost
    
    def update_route_conditions(self):
        """更新航线状态（随机变化）"""
        for route in self.route_conditions:
            # 危险度变化（±10%）
            danger = self.route_conditions[route]['危险度']
            danger_change = random.uniform(-0.1, 0.1)
            self.route_conditions[route]['危险度'] = max(0.1, min(0.9, danger + danger_change))
            
            # 风向优势变化（±20%）
            wind = self.route_conditions[route]['风向优势']
            wind_change = random.uniform(-0.2, 0.2)
            self.route_conditions[route]['风向优势'] = max(0.1, min(0.9, wind + wind_change))
            
            # 海况变化（±15%）
            sea = self.route_conditions[route]['海况']
            sea_change = random.uniform(-0.15, 0.15)
            self.route_conditions[route]['海况'] = max(0.05, min(0.8, sea + sea_change))
    
    def get_route_description(self, city_a: str, city_b: str) -> str:
        """获取航线状态的文字描述"""
        if (city_a, city_b) not in self.route_conditions:
            return "未知航线"
            
        route = self.route_conditions[(city_a, city_b)]
        danger = route['危险度']
        wind = route['风向优势']
        sea = route['海况']
        
        # 危险度描述
        if danger < 0.2:
            danger_desc = "非常安全"
        elif danger < 0.4:
            danger_desc = "比较安全"
        elif danger < 0.6:
            danger_desc = "略有风险"
        elif danger < 0.8:
            danger_desc = "危险"
        else:
            danger_desc = "非常危险"
            
        # 风向描述
        if wind < 0.3:
            wind_desc = "多为逆风"
        elif wind < 0.5:
            wind_desc = "风向多变"
        elif wind < 0.7:
            wind_desc = "风向适宜"
        else:
            wind_desc = "顺风航线"
            
        # 海况描述
        if sea < 0.2:
            sea_desc = "海面平静"
        elif sea < 0.4:
            sea_desc = "微波粼粼"
        elif sea < 0.6:
            sea_desc = "波涛汹涌"
        else:
            sea_desc = "风暴频发"
            
        return f"{danger_desc}，{wind_desc}，{sea_desc}"
    
    def get_all_routes(self) -> List[Tuple[str, str, Dict]]:
        """获取所有航线信息"""
        routes = []
        # 只返回单向航线，避免重复
        added_routes = set()
        
        for (city_a, city_b), distance in self.distances.items():
            if (city_b, city_a) in added_routes:
                continue
                
            conditions = self.route_conditions.get((city_a, city_b), {})
            routes.append((city_a, city_b, {
                'distance': distance,
                'description': self.get_route_description(city_a, city_b),
                'conditions': conditions
            }))
            added_routes.add((city_a, city_b))
            
        return routes 