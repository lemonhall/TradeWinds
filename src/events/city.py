from .base import RandomEvent

class CityEvent(RandomEvent):
    """城市事件"""
    def __init__(self, name, description, price_modifier, affected_goods=None):
        super().__init__(name, description)
        self.price_modifier = price_modifier  # 价格修改系数
        self.affected_goods = affected_goods  # 受影响的商品，None表示所有商品
    
    def apply(self, simulation, ship=None, city=None):
        if city:
            goods_to_affect = self.affected_goods or list(city.current_prices.keys())
            for good in goods_to_affect:
                if good in city.current_prices:
                    city.current_prices[good] *= self.price_modifier
            return True
        return False 