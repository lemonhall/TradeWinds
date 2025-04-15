from typing import Dict, List, Optional, Tuple, Any
import random
import uuid
import math

class Ship:
    """船只类，代表游戏中的船只实体"""
    
    def __init__(self, name: str, ship_type: str, capacity: int, crew: int,
                 sailing_skill: float, trading_skill: float, owner: str,
                 current_city = None):
        # 基本属性
        self.id = str(uuid.uuid4())[:8]  # 生成唯一ID
        self.name = name
        self.ship_type = ship_type
        self.capacity = capacity  # 最大载重量
        self.crew = crew  # 船员数量
        self.sailing_skill = sailing_skill  # 航行技能影响速度
        self.trading_skill = trading_skill  # 贸易技能影响价格
        self.owner = owner  # "player" 或 NPC名称
        
        # 状态属性
        self.current_city = current_city  # 当前所在城市，None表示在海上
        self.destination_city = None  # 目标城市
        self.remaining_transit_time = 0  # 剩余航行时间
        self.in_transit = False  # 是否在航行中
        self.health = 100  # 船只健康度，100为最佳状态
        self.morale = 100  # 船员士气
        
        # 货物和资源
        self.cargo = {}  # 货物字典，格式: {物品名: {"quantity": 数量, "purchase_price": 购买价格}}
        self.supplies = 100  # 补给，影响航行时间和士气
        self.money = 0  # 船上携带的金钱
        
        # 累计数据
        self.total_distance_traveled = 0
        self.total_trades = 0
        self.total_profit = 0
    
    def set_sail_to(self, destination_city, travel_time: int) -> bool:
        """设置航行到目标城市"""
        if self.in_transit:
            return False
        
        # 检查补给是否足够
        required_supplies = max(1, travel_time // 2)
        if self.supplies < required_supplies:
            return False
        
        self.destination_city = destination_city
        self.remaining_transit_time = travel_time
        self.in_transit = True
        self.current_city = None
        
        # 消耗补给
        self.supplies -= required_supplies
        
        return True
    
    def arrive_at_destination(self) -> Optional[Dict]:
        """到达目标城市，返回一个事件字典描述到达情况"""
        if not self.in_transit or self.remaining_transit_time > 0:
            return None
        
        self.in_transit = False
        self.current_city = self.destination_city
        self.destination_city = None
        
        # 更新士气
        self.morale = min(100, self.morale + 10)
        
        # 创建到达事件
        event = {
            "type": "arrival",
            "ship_id": self.id,
            "ship_name": self.name,
            "city_name": self.current_city.name,
            "description": f"{self.name}已安全抵达{self.current_city.name}。"
        }
        
        return event
    
    def load_cargo(self, good_name: str, quantity: int, price_per_unit: float) -> bool:
        """装载货物"""
        # 检查是否在城市中
        if not self.current_city:
            return False
        
        # 检查现有货物总量
        current_total_cargo = self.get_cargo_count()
        if current_total_cargo + quantity > self.capacity:
            return False
        
        # 更新货物清单
        if good_name not in self.cargo:
            self.cargo[good_name] = {
                "quantity": quantity,
                "purchase_price": price_per_unit
            }
        else:
            # 计算平均购买价格
            current_quantity = self.cargo[good_name]["quantity"]
            current_price = self.cargo[good_name]["purchase_price"]
            
            new_quantity = current_quantity + quantity
            new_price = ((current_quantity * current_price) + (quantity * price_per_unit)) / new_quantity
            
            self.cargo[good_name] = {
                "quantity": new_quantity,
                "purchase_price": new_price
            }
        
        return True
    
    def unload_cargo(self, good_name: str, quantity: int) -> Tuple[bool, int, float]:
        """卸载货物，返回(成功与否, 实际卸载数量, 购买价格)"""
        if good_name not in self.cargo:
            return (False, 0, 0)
        
        available_quantity = self.cargo[good_name]["quantity"]
        purchase_price = self.cargo[good_name]["purchase_price"]
        
        actual_quantity = min(quantity, available_quantity)
        
        # 更新货物记录
        if actual_quantity == available_quantity:
            del self.cargo[good_name]
        else:
            self.cargo[good_name]["quantity"] -= actual_quantity
        
        return (True, actual_quantity, purchase_price)
    
    def buy_goods(self, good_name: str, quantity: int) -> bool:
        """从当前城市购买货物"""
        if not self.current_city:
            return False
        
        # 获取当前城市的货物价格
        price_per_unit = self.current_city.get_goods_buy_price(good_name, self.trading_skill)
        total_cost = price_per_unit * quantity
        
        # 检查金钱是否足够
        if self.money < total_cost:
            return False
        
        # 尝试从城市购买
        if not self.current_city.sell_goods(good_name, quantity):
            return False
        
        # 扣除金钱
        self.money -= total_cost
        
        # 装载货物
        success = self.load_cargo(good_name, quantity, price_per_unit)
        
        # 如果装载失败，退还金钱并恢复城市库存
        if not success:
            self.money += total_cost
            self.current_city.buy_goods(good_name, quantity, 0)  # 价格为0表示仅恢复库存
            return False
        
        # 记录交易
        self.total_trades += 1
        
        return True
    
    def sell_goods(self, good_name: str, quantity: int) -> bool:
        """在当前城市出售货物"""
        if not self.current_city:
            return False
        
        # 尝试卸载货物
        success, actual_quantity, purchase_price = self.unload_cargo(good_name, quantity)
        if not success or actual_quantity == 0:
            return False
        
        # 获取销售价格
        price_per_unit = self.current_city.get_goods_sell_price(good_name, self.trading_skill)
        total_revenue = price_per_unit * actual_quantity
        
        # 计算利润
        profit = total_revenue - (purchase_price * actual_quantity)
        self.total_profit += profit
        
        # 出售给城市
        self.current_city.buy_goods(good_name, actual_quantity, price_per_unit)
        
        # 增加金钱
        self.money += total_revenue
        
        # 记录交易
        self.total_trades += 1
        
        return True
    
    def repair_ship(self, amount: int = None) -> int:
        """修理船只，返回修理费用"""
        if not self.current_city:
            return 0
        
        # 如果未指定修理量，则修理到满
        if amount is None:
            amount = 100 - self.health
        
        # 限制修理量
        amount = min(amount, 100 - self.health)
        
        # 计算修理费用，每点健康度花费取决于船只大小
        repair_cost_per_point = math.ceil(self.capacity / 50)
        total_repair_cost = amount * repair_cost_per_point
        
        # 检查金钱是否足够
        if self.money < total_repair_cost:
            return 0
        
        # 进行修理
        self.money -= total_repair_cost
        self.health = min(100, self.health + amount)
        
        return total_repair_cost
    
    def resupply(self, amount: int = None) -> int:
        """补充船只补给，返回补给费用"""
        if not self.current_city:
            return 0
        
        # 如果未指定补给量，则补充到满
        if amount is None:
            amount = 100 - self.supplies
        
        # 限制补给量
        amount = min(amount, 100 - self.supplies)
        
        # 计算补给费用，基础价格 + 城市加成
        supply_cost_per_unit = 2 + self.current_city.port_quality * 0.5
        total_supply_cost = math.ceil(amount * supply_cost_per_unit)
        
        # 检查金钱是否足够
        if self.money < total_supply_cost:
            return 0
        
        # 进行补给
        self.money -= total_supply_cost
        self.supplies = min(100, self.supplies + amount)
        
        return total_supply_cost
    
    def pay_crew(self) -> bool:
        """支付船员工资，影响士气，返回是否成功支付"""
        # 计算工资，基于船员数量
        wage_per_crew = 2
        total_wages = self.crew * wage_per_crew
        
        # 检查金钱是否足够
        if self.money < total_wages:
            # 无法支付工资，降低士气
            self.morale = max(0, self.morale - 15)
            return False
        
        # 支付工资
        self.money -= total_wages
        
        # 提升士气
        self.morale = min(100, self.morale + 5)
        
        return True
    
    def get_cargo_count(self) -> int:
        """获取当前货物总量"""
        return sum(item["quantity"] for item in self.cargo.values())
    
    def get_cargo_value(self) -> float:
        """计算当前货物总价值"""
        total_value = 0
        for good_name, info in self.cargo.items():
            if self.current_city:
                # 使用当前城市的市场价格
                price = self.current_city.get_goods_sell_price(good_name, self.trading_skill)
            else:
                # 使用购买价格
                price = info["purchase_price"]
            
            total_value += price * info["quantity"]
        
        return total_value
    
    def get_total_assets(self) -> float:
        """计算船只总资产价值"""
        # 基础船值，基于类型和容量
        base_ship_value = {
            "小商船": 400,
            "中型商船": 800,
            "大型商船": 1600,
            "快速帆船": 1200,
            "战船": 2400
        }.get(self.ship_type, 800)
        
        # 根据健康状况调整价值
        ship_value = base_ship_value * (self.health / 100)
        
        # 添加货物价值和现金
        total_assets = ship_value + self.get_cargo_value() + self.money
        
        return total_assets
    
    def update_daily(self) -> List[Dict]:
        """每日更新，返回事件列表"""
        events = []
        
        # 在海上航行时消耗补给
        if self.in_transit:
            # 消耗补给
            supply_consumption = max(1, self.crew // 10)
            self.supplies = max(0, self.supplies - supply_consumption)
            
            # 补给不足时降低士气
            if self.supplies < 30:
                morale_drop = random.randint(1, 3)
                self.morale = max(0, self.morale - morale_drop)
                
                if self.morale < 20:
                    # 低士气可能导致叛变
                    if random.random() < 0.05:  # 5%几率
                        mutiny_event = {
                            "type": "mutiny",
                            "ship_id": self.id,
                            "ship_name": self.name,
                            "description": f"{self.name}的船员由于士气低落发生了叛变！"
                        }
                        events.append(mutiny_event)
                        
                        # 叛变后果: 失去一部分货物和金钱
                        lost_money = int(self.money * random.uniform(0.2, 0.4))
                        self.money -= lost_money
                        
                        # 随机选择一种货物丢失
                        if self.cargo:
                            lost_good = random.choice(list(self.cargo.keys()))
                            lost_amount = int(self.cargo[lost_good]["quantity"] * random.uniform(0.3, 0.6))
                            self.cargo[lost_good]["quantity"] -= lost_amount
                            
                            if self.cargo[lost_good]["quantity"] <= 0:
                                del self.cargo[lost_good]
        
        # 船只状态随时间自然下降
        self.health = max(0, self.health - random.uniform(0.1, 0.3))
        
        # 返回事件列表
        return events
    
    def __str__(self) -> str:
        status = "在航行中" if self.in_transit else f"停泊在{self.current_city.name if self.current_city else '未知'}"
        return f"{self.name} ({self.ship_type}): {status}, 健康度: {self.health:.1f}, 士气: {self.morale}" 