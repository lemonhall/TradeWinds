import random
from typing import Dict, Tuple
from collections import defaultdict
import numpy as np

# 商品质量等级常量
QUALITY_LEVELS = {
    "粗糙": 0.7,   # 价格降低30%
    "普通": 1.0,   # 标准基准价格
    "精良": 1.5,   # 价格提高50%
    "极品": 2.5    # 价格提高150%
}

class City:
    def __init__(self, name: str, base_prices: Dict[str, float], production: Dict[str, float], consumption: Dict[str, float]):
        """
        初始化一个城市
        :param name: 城市名称
        :param base_prices: 商品基础价格字典 {商品名: 基础价格}
        :param production: 商品生产量字典 {商品名: 日产量}
        :param consumption: 商品消费量字典 {商品名: 日消费量}
        """
        self.name = name
        self.base_prices = base_prices
        self.current_prices = base_prices.copy()
        # 商品质量存储 {商品名: {质量等级: 数量}}
        self.inventory_by_quality = defaultdict(lambda: defaultdict(float))
        # 仍然保留总库存以便于兼容现有代码
        self.inventory = defaultdict(float)  
        self.production = production
        self.consumption = consumption
        self.price_history = {good: [] for good in base_prices}
        self.inventory_history = {good: [] for good in base_prices}
        
        # 城市特产和擅长的商品质量
        self.specialty_goods = self._generate_specialties(list(base_prices.keys()))
        
        # 初始化库存为7天的产量
        for good, amount in production.items():
            self._add_inventory_with_quality(good, amount * 7)
    
    def _generate_specialties(self, goods_list):
        """为城市生成特产商品，这些商品质量会更高"""
        num_specialties = min(3, len(goods_list))  # 最多3种特产
        specialties = random.sample(goods_list, num_specialties)
        return set(specialties)
    
    def _add_inventory_with_quality(self, good: str, amount: float):
        """添加库存时分配不同质量等级"""
        if amount <= 0:
            return
            
        # 根据城市特产调整质量分布
        if good in self.specialty_goods:
            # 特产商品有更高概率获得高质量
            quality_weights = {"粗糙": 0.1, "普通": 0.3, "精良": 0.4, "极品": 0.2}
        else:
            # 非特产商品的标准质量分布
            quality_weights = {"粗糙": 0.3, "普通": 0.5, "精良": 0.15, "极品": 0.05}
            
        # 根据权重分配库存
        total_weight = sum(quality_weights.values())
        remaining = amount
        
        for quality, weight in quality_weights.items():
            if quality != list(quality_weights.keys())[-1]:  # 不是最后一个质量等级
                quality_amount = amount * (weight / total_weight)
                self.inventory_by_quality[good][quality] += quality_amount
                remaining -= quality_amount
            else:  # 最后一个质量等级获得剩余数量，避免舍入误差
                self.inventory_by_quality[good][quality] += remaining
        
        # 更新总库存
        self.inventory[good] += amount
    
    def update(self):
        """每日更新城市经济状态"""
        # 更新库存
        for good, amount in self.production.items():
            self._add_inventory_with_quality(good, amount)
        
        for good, amount in self.consumption.items():
            self._consume_inventory(good, amount)
        
        # 根据供需关系调整价格
        for good in self.base_prices:
            # 避免除零错误，确保消费量至少为一个很小的值
            effective_consumption = self.consumption.get(good, 0.1)
            if effective_consumption <= 0:
                effective_consumption = 0.1
            base_demand = effective_consumption * 7
            
            # 检查库存是否为负数或零，避免 supply_ratio 计算错误
            current_inventory = self.inventory.get(good, 0)
            if current_inventory <= 0:
                supply_ratio = 0.01 # 设定一个非常低的比率
            else:
                supply_ratio = current_inventory / base_demand
                
            price_change = random.uniform(0.95, 1.05)  # 随机波动
            # S型调整函数对极低或极高的 supply_ratio 可能过于敏感，增加保护
            sigmoid_input = np.clip((supply_ratio - 1) * 2, -10, 10) # 限制输入范围
            price_adjustment = 1.0 / (1 + np.exp(-sigmoid_input)) 
            
            self.current_prices[good] = max(0.1, self.base_prices[good] * price_change * price_adjustment)
            self.price_history[good].append(self.current_prices[good])
            self.inventory_history[good].append(self.inventory.get(good, 0))
    
    def _consume_inventory(self, good: str, amount: float):
        """按质量顺序消耗库存（先消耗低质量）"""
        if amount <= 0:
            return
            
        # 消费顺序：先消耗低质量商品
        remaining = amount
        for quality in ["粗糙", "普通", "精良", "极品"]:
            available = self.inventory_by_quality[good][quality]
            consumed = min(available, remaining)
            self.inventory_by_quality[good][quality] -= consumed
            remaining -= consumed
            
            if remaining <= 0:
                break
        
        # 更新总库存
        self.inventory[good] = max(0, self.inventory[good] - amount)
    
    def get_best_quality_price(self, good: str) -> Tuple[str, float]:
        """获取可用的最高质量和相应价格"""
        if good not in self.current_prices:
            return "普通", 0
            
        base_price = self.current_prices[good]
        
        # 从高到低检查质量
        for quality in ["极品", "精良", "普通", "粗糙"]:
            if self.inventory_by_quality[good][quality] > 0:
                return quality, base_price * QUALITY_LEVELS[quality]
                
        # 如果所有质量都没有库存，返回普通质量但价格为0
        return "普通", 0
    
    def get_cheapest_quality_price(self, good: str) -> Tuple[str, float]:
        """获取可用的最便宜质量和相应价格"""
        if good not in self.current_prices:
            return "普通", 0
            
        base_price = self.current_prices[good]
        
        # 从低到高检查质量
        for quality in ["粗糙", "普通", "精良", "极品"]:
            if self.inventory_by_quality[good][quality] > 0:
                return quality, base_price * QUALITY_LEVELS[quality]
                
        # 如果所有质量都没有库存，返回普通质量但价格为0
        return "普通", 0
    
    def get_quality_price(self, good: str, quality: str) -> float:
        """获取指定质量的商品价格"""
        if good not in self.current_prices or quality not in QUALITY_LEVELS:
            return 0
            
        return self.current_prices[good] * QUALITY_LEVELS[quality]
        
    def get_available_qualities(self, good: str) -> Dict[str, float]:
        """获取商品所有可用的质量和数量"""
        result = {}
        for quality, amount in self.inventory_by_quality[good].items():
            if amount > 0:
                result[quality] = amount
        return result
    
    def trade(self, good: str, amount: float, quality: str = "普通") -> float:
        """
        进行商品交易
        :param good: 商品名称
        :param amount: 交易数量(正为买入，负为卖出)
        :param quality: 商品质量，默认为"普通"
        :return: 交易总价 (如果交易成功)
        """
        if good not in self.current_prices or quality not in QUALITY_LEVELS:
            print(f"Error: Good '{good}' or quality '{quality}' not available for trade in {self.name}.")
            return 0
        
        # 计算质量调整后的价格
        adjusted_price = self.current_prices[good] * QUALITY_LEVELS[quality]
        
        if amount > 0:  # 买入 (City sells)
            available_inventory = self.inventory_by_quality[good][quality]
            actual_amount = min(amount, available_inventory)
            if actual_amount <= 0:
                return 0 # 不能买入
            self.inventory_by_quality[good][quality] -= actual_amount
            self.inventory[good] -= actual_amount
            return actual_amount * adjusted_price
        elif amount < 0: # 卖出 (City buys)
            actual_amount = -amount # 卖出的数量是正数
            self.inventory_by_quality[good][quality] += actual_amount
            self.inventory[good] += actual_amount
            return actual_amount * adjusted_price # 返回的是卖出所得
        else: # amount == 0
            return 0
            
    def update_prices(self):
        """每日更新商品价格"""
        # 根据供需关系调整价格
        for good in self.base_prices:
            # 避免除零错误，确保消费量至少为一个很小的值
            effective_consumption = self.consumption.get(good, 0.1)
            if effective_consumption <= 0:
                effective_consumption = 0.1
            base_demand = effective_consumption * 7
            
            # 检查库存是否为负数或零，避免 supply_ratio 计算错误
            current_inventory = self.inventory.get(good, 0)
            if current_inventory <= 0:
                supply_ratio = 0.01  # 设定一个非常低的比率
            else:
                supply_ratio = current_inventory / base_demand
                
            price_change = random.uniform(0.95, 1.05)  # 随机波动
            # S型调整函数对极低或极高的 supply_ratio 可能过于敏感，增加保护
            sigmoid_input = np.clip((supply_ratio - 1) * 2, -10, 10)  # 限制输入范围
            price_adjustment = 1.0 / (1 + np.exp(-sigmoid_input)) 
            
            # 调整价格，但保持在基础价格的一定范围内
            new_price = self.base_prices[good] * price_change * price_adjustment
            min_price = self.base_prices[good] * 0.5
            max_price = self.base_prices[good] * 2.0
            self.current_prices[good] = max(min_price, min(new_price, max_price))
    
    def update_quality_distribution(self):
        """更新商品质量分布"""
        # 每日生产新商品
        for good, amount in self.production.items():
            self._add_inventory_with_quality(good, amount)
        
        # 每日消费商品
        for good, amount in self.consumption.items():
            self._consume_inventory(good, amount)
    
    def record_price_history(self):
        """记录价格历史"""
        for good in self.base_prices:
            self.price_history[good].append(self.current_prices[good])
            self.inventory_history[good].append(self.inventory.get(good, 0))
            
            # 保持历史记录在合理范围内
            if len(self.price_history[good]) > 365:  # 保留一年的数据
                self.price_history[good].pop(0)
                self.inventory_history[good].pop(0)
    
    def modify_price_multiplier(self, good: str, multiplier: float):
        """修改商品价格乘数，用于事件效果"""
        if good in self.current_prices:
            self.current_prices[good] = self.current_prices[good] * multiplier 