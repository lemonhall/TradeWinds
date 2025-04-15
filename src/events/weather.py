from .base import RandomEvent

class WeatherEvent(RandomEvent):
    """天气事件"""
    def __init__(self, name, description, speed_modifier, duration):
        super().__init__(name, description)
        self.speed_modifier = speed_modifier  # 对船只速度的影响
        self.duration = duration  # 持续时间（天）
    
    def apply(self, simulation, ship=None, city=None):
        if ship and ship.in_transit:
            # 记录原始速度
            if not hasattr(ship, 'original_speed'):
                ship.original_speed = ship.speed
                
            # 应用速度修正
            ship.speed = max(1, ship.original_speed * self.speed_modifier)
            
            # 添加天气事件到船只
            ship.weather_events.append({
                'event': self,
                'remaining_days': self.duration
            })
            
            return True
        return False 