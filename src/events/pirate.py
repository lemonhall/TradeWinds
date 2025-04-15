from .base import RandomEvent

class PirateEvent(RandomEvent):
    """海盗事件"""
    def __init__(self, name, description, steal_percent):
        super().__init__(name, description)
        self.steal_percent = steal_percent  # 损失的货物/金钱百分比
    
    def apply(self, simulation, ship=None, city=None):
        if ship and ship.in_transit:
            # 货物损失
            for good in list(ship.cargo.keys()):
                stolen_amount = ship.cargo[good] * self.steal_percent
                ship.cargo[good] -= stolen_amount
                
            # 金钱损失
            stolen_gold = ship.gold * self.steal_percent
            ship.gold -= stolen_gold
            
            return True
        return False 