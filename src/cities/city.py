from typing import Dict, List, Optional
import random

class City:
    """表示贸易模拟中的一个城市"""
    
    def __init__(self, name: str, position: tuple, specialties: List[str] = None):
        self.name = name
        self.position = position  # (x, y) 坐标
        self.specialties = specialties or []  # 城市特产商品列表
        
        # 货物市场
        self.market: Dict[str, Dict] = {}
        
        # 市场特性
        self.market_size = random.uniform(0.8, 1.2)  # 市场规模修正
        self.tax_rate = random.uniform(0.05, 0.15)  # 交易税率
        
        # 港口特性
        self.port_quality = random.uniform(0.8, 1.2)  # 港口品质（影响装卸速度和成本）
        self.port_fee = int(50 * random.uniform(0.8, 1.2))  # 基础停泊费
        
        # 事件状态
        self.active_events = []  # 当前影响城市的事件
        
        # 初始化市场
        self._initialize_market()
    
    def _initialize_market(self) -> None:
        """初始化城市市场和商品价格"""
        # 这里会根据特产和基础商品列表初始化市场
        standard_goods = ["布料", "香料", "木材", "金属", "珠宝", "酒类", "粮食", "药材"]
        
        for good in standard_goods:
            # 特产商品有更高的供应量和更低的基础价格
            is_specialty = good in self.specialties
            
            # 基础价格（特产价格较低）
            base_price = random.randint(10, 100)
            if is_specialty:
                base_price = int(base_price * 0.7)
            
            # 当前价格在基础价格上有一定波动
            current_price = int(base_price * random.uniform(0.9, 1.1))
            
            # 供应量（特产供应更多）
            supply = random.randint(50, 200)
            if is_specialty:
                supply = int(supply * 1.5)
            
            # 需求量（特产需求较低，因为本地生产）
            demand = random.randint(50, 200)
            if is_specialty:
                demand = int(demand * 0.7)
            
            # 品质（特产品质更高）
            quality = random.uniform(0.8, 1.0)
            if is_specialty:
                quality = random.uniform(0.9, 1.2)
            
            self.market[good] = {
                "base_price": base_price,
                "current_price": current_price,
                "supply": supply, 
                "demand": demand,
                "quality": quality,
                "is_specialty": is_specialty,
                "price_history": [current_price]  # 记录价格历史
            }
    
    def update_market(self) -> None:
        """更新市场价格和供需关系"""
        for good_name, good_data in self.market.items():
            # 供需比率影响价格
            supply_demand_ratio = good_data["supply"] / max(1, good_data["demand"])
            
            # 价格调整因子 - 供应少于需求时价格上涨，反之下降
            price_adjust = 1.0
            if supply_demand_ratio < 0.8:
                # 供应短缺，价格上涨
                price_adjust = random.uniform(1.02, 1.05)
            elif supply_demand_ratio > 1.2:
                # 供应过剩，价格下降
                price_adjust = random.uniform(0.95, 0.98)
            else:
                # 供需平衡，价格小幅波动
                price_adjust = random.uniform(0.98, 1.02)
            
            # 应用事件影响
            for event in self.active_events:
                if event.get("type") == "market" and event.get("good") == good_name:
                    price_adjust *= event.get("price_modifier", 1.0)
            
            # 更新价格，但保持在基础价格的一定范围内
            new_price = int(good_data["current_price"] * price_adjust)
            min_price = int(good_data["base_price"] * 0.7)
            max_price = int(good_data["base_price"] * 1.5)
            good_data["current_price"] = max(min_price, min(new_price, max_price))
            
            # 记录价格历史
            good_data["price_history"].append(good_data["current_price"])
            if len(good_data["price_history"]) > 30:  # 仅保留最近30天
                good_data["price_history"].pop(0)
            
            # 随机调整供需
            good_data["supply"] += random.randint(-10, 15)
            good_data["supply"] = max(10, good_data["supply"])  # 确保至少有最小供应
            
            good_data["demand"] += random.randint(-10, 15)
            good_data["demand"] = max(10, good_data["demand"])  # 确保至少有最小需求
    
    def buy_goods(self, good_name: str, quantity: int, ship_trading_skill: float = 1.0) -> tuple:
        """从城市购买商品，返回(成功标志, 实际购买数量, 总价格, 商品品质)"""
        if good_name not in self.market or self.market[good_name]["supply"] < quantity:
            return False, 0, 0, 0
        
        # 应用交易技能修正（降低购买价格）
        price_modifier = max(0.9, 1.0 - (ship_trading_skill - 1) * 0.05)
        
        # 计算购买价格（包含税率）
        unit_price = int(self.market[good_name]["current_price"] * price_modifier)
        total_price = unit_price * quantity * (1 + self.tax_rate)
        
        # 减少供应
        self.market[good_name]["supply"] -= quantity
        
        # 增加需求（买入增加市场需求）
        self.market[good_name]["demand"] += int(quantity * 0.2)
        
        # 获取商品品质
        quality = self.market[good_name]["quality"]
        
        return True, quantity, int(total_price), quality
    
    def sell_goods(self, good_name: str, quantity: int, quality: float, ship_trading_skill: float = 1.0) -> tuple:
        """向城市出售商品，返回(成功标志, 实际售出数量, 总收入)"""
        if good_name not in self.market:
            return False, 0, 0
        
        # 应用交易技能修正（提高售出价格）
        price_modifier = min(1.1, 1.0 + (ship_trading_skill - 1) * 0.05)
        
        # 计算品质对价格的影响
        quality_modifier = quality / self.market[good_name]["quality"]
        
        # 计算售出价格（包含税率）
        unit_price = int(self.market[good_name]["current_price"] * price_modifier * quality_modifier)
        total_income = unit_price * quantity * (1 - self.tax_rate)
        
        # 增加供应
        self.market[good_name]["supply"] += quantity
        
        # 减少需求（卖出减少市场需求）
        self.market[good_name]["demand"] = max(10, self.market[good_name]["demand"] - int(quantity * 0.1))
        
        return True, quantity, int(total_income)
    
    def add_event(self, event_type: str, duration: int, **params) -> None:
        """添加影响城市的事件"""
        event = {
            "type": event_type,
            "duration": duration,
            **params
        }
        self.active_events.append(event)
    
    def update_events(self) -> None:
        """更新城市事件状态"""
        for event in self.active_events[:]:  # 创建副本以便安全删除
            event["duration"] -= 1
            if event["duration"] <= 0:
                self.active_events.remove(event)
    
    def get_port_fee(self, ship_size: int) -> int:
        """计算船只的停泊费用"""
        return int(self.port_fee * (1 + ship_size / 200))
    
    def calculate_distance(self, other_city) -> float:
        """计算与另一个城市的距离"""
        x1, y1 = self.position
        x2, y2 = other_city.position
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    def __str__(self) -> str:
        return f"城市: {self.name} - 特产: {', '.join(self.specialties)}" 