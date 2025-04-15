from typing import Dict, Tuple, List, Optional
# 从 .city 导入 City 以进行类型提示，避免循环导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .city import City
    from .map import TradeMap

class Ship:
    def __init__(self, name: str, capacity: float, speed: float):
        """
        初始化一艘船
        :param name: 船名
        :param capacity: 载货容量
        :param speed: 航行速度(基础城市间移动速度，受风向和海况影响)
        """
        self.name = name
        self.capacity = capacity
        self.speed = speed
        # 修改货物存储结构为 {商品名: {质量等级: 数量}}
        self.cargo = {}
        self.cargo_by_quality = {}
        self.current_city = None  # type: 'City | None'
        self.destination = None   # type: 'City | None'
        self.days_in_transit = 0
        self.travel_time = 0      # 当前航程总需时间
        self.gold = 1000          # 初始资金
        self.trade_history = []
        self.gold_history = []
        self.route_costs = []     # 航线成本历史
        self.in_transit = False   # 是否在航行状态
        # 增加质量偏好，有些船只偏好高质量，有些偏好低价
        self.quality_preference = "价格" if name.endswith(("号", "Lion")) else "质量"
        
        # 船只规模，影响船员数量和补给成本
        self.size = capacity / 100  # 船只大小因子
        self.crew_count = int(10 + self.size * 20)  # 船员数量
        
        # 船只特性
        self.sailing_skill = 1.0  # 航海技巧倍率，影响航行速度
        self.trading_skill = 1.0  # 交易技巧倍率，影响港口费用
    
    def load_cargo(self, good: str, amount: float, price: float, quality: str = "普通"):
        """
        装载货物
        :param good: 商品名称
        :param amount: 装载数量
        :param price: 购买价格
        :param quality: 商品质量
        :return: 实际装载数量
        """
        # 检查总载货量
        total_amount = sum(sum(qualities.values()) for qualities in self.cargo_by_quality.values())
        available_space = self.capacity - total_amount
        actual_amount = min(amount, available_space)
        
        if actual_amount <= 0:
            return 0
        
        # 初始化嵌套字典如果需要
        if good not in self.cargo_by_quality:
            self.cargo_by_quality[good] = {}
            self.cargo[good] = 0
            
        # 更新货物数量
        if quality in self.cargo_by_quality[good]:
            self.cargo_by_quality[good][quality] += actual_amount
        else:
            self.cargo_by_quality[good][quality] = actual_amount
            
        # 更新总数量
        self.cargo[good] += actual_amount
        
        # 计算成本
        cost = actual_amount * price
        self.gold -= cost
        
        # 记录交易
        self.trade_history.append({
            "type": "buy",
            "good": good,
            "quality": quality,
            "amount": actual_amount,
            "price": price,
            "location": self.current_city.name if self.current_city else "Unknown"
        })
        
        return actual_amount
    
    def unload_cargo(self, good: str, price: float, quality: str = None) -> float:
        """
        卸载并出售货物
        :param good: 商品名称
        :param price: 出售价格
        :param quality: 指定要卸载的质量，如果为None则卸载所有质量
        :return: 销售收入
        """
        if good not in self.cargo_by_quality:
            return 0
            
        total_revenue = 0
        
        if quality:
            # 卸载特定质量的货物
            if quality in self.cargo_by_quality[good] and self.cargo_by_quality[good][quality] > 0:
                amount = self.cargo_by_quality[good][quality]
                revenue = amount * price
                self.gold += revenue
                
                # 记录交易
                self.trade_history.append({
                    "type": "sell",
                    "good": good,
                    "quality": quality,
                    "amount": amount,
                    "price": price,
                    "location": self.current_city.name if self.current_city else "Unknown"
                })
                
                # 更新库存
                self.cargo[good] -= amount
                self.cargo_by_quality[good][quality] = 0
                
                return revenue
        else:
            # 卸载所有质量的货物
            for q, amount in list(self.cargo_by_quality[good].items()):
                if amount > 0:
                    revenue = amount * price
                    self.gold += revenue
                    total_revenue += revenue
                    
                    # 记录交易
                    self.trade_history.append({
                        "type": "sell",
                        "good": good,
                        "quality": q,
                        "amount": amount,
                        "price": price,
                        "location": self.current_city.name if self.current_city else "Unknown"
                    })
                    
                    # 更新库存
                    self.cargo_by_quality[good][q] = 0
            
            # 重置总量
            self.cargo[good] = 0
            
            return total_revenue
    
    def set_route(self, current_city: 'City', destination: 'City', trade_map: 'TradeMap'):
        """
        设置航线并计算航行时间和成本
        :param trade_map: 贸易地图，用于计算航行时间和成本
        """
        self.current_city = current_city
        self.destination = destination
        self.days_in_transit = 0
        self.in_transit = True  # 设置为航行状态
        
        # 计算航行时间
        travel_time = trade_map.calculate_travel_time(
            current_city.name, destination.name, self.speed * self.sailing_skill
        )
        self.travel_time = travel_time
        
        # 计算并扣除航线成本
        route_cost = trade_map.calculate_route_cost(
            current_city.name, destination.name, self.size
        )
        
        # 交易技巧降低成本
        route_cost = route_cost / self.trading_skill
        
        self.gold -= route_cost
        self.route_costs.append({
            'from': current_city.name,
            'to': destination.name,
            'cost': route_cost,
            'day': 0  # 将在update时更新为实际日期
        })
        
        # 记录航行信息
        self.trade_history.append({
            "type": "route",
            "from": current_city.name,
            "to": destination.name,
            "estimated_days": travel_time,
            "cost": route_cost
        })
    
    def update(self) -> bool:
        """
        更新船只状态
        :return: 是否到达目的地
        """
        if not self.destination:
            self.in_transit = False  # 没有目的地时不在航行状态
            return False
        
        self.days_in_transit += 1
        
        # 更新最近一次航行成本记录的天数
        if self.route_costs:
            self.route_costs[-1]['day'] += 1
        
        if self.days_in_transit >= self.travel_time:
            self.current_city = self.destination
            self.destination = None
            self.days_in_transit = 0
            self.travel_time = 0
            self.gold_history.append(self.gold)
            self.in_transit = False  # 到达目的地后不再航行状态
            return True
        return False
    
    def improve_skill(self, skill_type: str, amount: float = 0.05):
        """提升船只技能"""
        if skill_type == "航海":
            self.sailing_skill = min(2.0, self.sailing_skill + amount)
        elif skill_type == "交易":
            self.trading_skill = min(2.0, self.trading_skill + amount)
    
    def improve_sailing_skill(self, amount: float = 0.05):
        """提升航海技能"""
        self.improve_skill("航海", amount)
    
    def improve_trading_skill(self, amount: float = 0.05):
        """提升交易技能"""
        self.improve_skill("交易", amount)
    
    def get_cargo_details(self) -> Dict:
        """获取货物详细信息，按质量分类"""
        return self.cargo_by_quality
    
    def get_status(self) -> Dict:
        """获取船只状态概览"""
        return {
            "name": self.name,
            "gold": self.gold,
            "capacity": self.capacity,
            "used_capacity": sum(sum(qualities.values()) for qualities in self.cargo_by_quality.values()),
            "speed": self.speed,
            "crew": self.crew_count,
            "location": self.current_city.name if self.current_city else "在海上",
            "destination": self.destination.name if self.destination else None,
            "travel_progress": f"{self.days_in_transit}/{self.travel_time}" if self.travel_time else "0/0",
            "sailing_skill": self.sailing_skill,
            "trading_skill": self.trading_skill
        }
    
    def get_total_route_costs(self) -> float:
        """获取历史总航线成本"""
        return sum(record['cost'] for record in self.route_costs) 