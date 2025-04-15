import random
from typing import Optional

def update_simulation(simulation):
    """更新模拟的状态，包括船只位置、城市价格等"""
    # 更新城市价格
    for city in simulation.cities.values():
        city.update_prices()
        city.update_quality_distribution()
        city.record_price_history()

    # 更新船只状态和位置
    for ship_name, ship in simulation.ships.items():
        if ship.in_transit:
            # 船只在航行中，更新位置
            update_ship_in_transit(simulation, ship)
        else:
            # 船只在港口，决定下一步行动
            if ship.current_city:
                simulation.perform_trading_strategy(ship)
            
    # 随机触发事件
    trigger_random_events(simulation)

def update_ship_in_transit(simulation, ship):
    """更新正在航行中的船只状态"""
    # 增加航行天数
    ship.days_in_transit += 1
    
    # 检查是否到达目的地
    if ship.days_in_transit >= ship.travel_time:
        # 到达目的地
        destination = ship.destination
        destination_name = destination.name if hasattr(destination, 'name') else destination
        ship.current_city = simulation.cities[destination_name] if isinstance(destination, str) else destination
        ship.destination = None
        ship.days_in_transit = 0
        ship.travel_time = 0
        ship.in_transit = False
        
        # 记录资金历史
        ship.gold_history.append(ship.gold)
        
        # 记录事件
        log_entry = f"第{simulation.day}天: {ship.name} 抵达 {destination_name if isinstance(destination, str) else destination.name}"
        simulation.event_log.append(log_entry)
        
        # 随机增加航海或贸易技能（10%几率）
        if random.random() < 0.1:
            if random.random() < 0.5:
                ship.improve_sailing_skill()
                simulation.event_log.append(f"第{simulation.day}天: {ship.name} 航海技能提升")
            else:
                ship.improve_trading_skill()
                simulation.event_log.append(f"第{simulation.day}天: {ship.name} 贸易技能提升")

def set_ship_route(simulation, ship, destination_name):
    """设置船只新的航行路线"""
    if destination_name == ship.current_city.name:
        return False  # 已经在目的地
    
    # 计算航行时间和成本
    travel_time, route_cost = calculate_travel_params(simulation, ship, ship.current_city.name, destination_name)
    
    # 设置船只航行状态
    ship.set_route(ship.current_city, simulation.cities[destination_name], simulation.trade_map)
    
    # 记录事件
    log_entry = f"第{simulation.day}天: {ship.name} 从 {ship.current_city.name} 出发前往 {destination_name}，预计航行时间: {travel_time}天"
    simulation.event_log.append(log_entry)
    
    return True

def calculate_travel_params(simulation, ship, from_city, to_city):
    """计算旅行参数（时间和成本）"""
    # 从地图获取基础航行时间和成本
    base_travel_time = simulation.trade_map.calculate_travel_time(from_city, to_city, ship.speed)
    route_cost = simulation.trade_map.calculate_route_cost(from_city, to_city, ship.crew_count)
    
    # 应用船只的航海技能调整（减少时间，减少成本）
    travel_time = max(1, int(base_travel_time * (1 - 0.05 * ship.sailing_skill)))
    adjusted_cost = route_cost * (1 - 0.03 * ship.sailing_skill)
    
    # 应用随机天气事件对航行时间的影响
    weather_impact = apply_weather_events(simulation, ship)
    travel_time = max(1, int(travel_time * weather_impact))
    
    return travel_time, adjusted_cost

def apply_weather_events(simulation, ship):
    """应用天气事件对航行的影响"""
    # 清除之前的天气事件
    ship.weather_events = []
    
    # 50%的概率触发天气事件
    if random.random() < 0.5:
        weather_event = random.choice(simulation.weather_events)
        ship.weather_events.append(weather_event)
        
        # 记录事件
        log_entry = f"第{simulation.day}天: {ship.name} 在航行途中遇到 {weather_event.name} - {weather_event.description}"
        simulation.event_log.append(log_entry)
        
        return weather_event.speed_multiplier
    
    return 1.0  # 无天气事件时的默认值

def trigger_random_events(simulation):
    """触发随机事件"""
    # 对每个城市触发事件
    for city_name, city in simulation.cities.items():
        # 10%的概率触发城市事件
        if random.random() < 0.1:
            event = random.choice(simulation.city_events)
            affected_goods = event.affected_goods if event.affected_goods else list(city.base_prices.keys())
            
            # 应用事件效果
            for good in affected_goods:
                if good in city.base_prices:
                    city.modify_price_multiplier(good, event.price_modifier)
            
            # 记录事件
            log_entry = f"第{simulation.day}天: {city_name} 发生 {event.name} - {event.description}"
            simulation.event_log.append(log_entry)
    
    # 对每个在航行中的船只可能触发海盗事件
    for ship_name, ship in simulation.ships.items():
        if ship.in_transit and random.random() < 0.05:  # 5%的概率
            pirate_event = random.choice(simulation.pirate_events)
            
            # 计算海盗造成的损失
            gold_loss = int(ship.gold * pirate_event.steal_percent)
            ship.gold -= gold_loss
            
            # 记录事件
            log_entry = f"第{simulation.day}天: {ship.name} 在航行途中遭遇 {pirate_event.name} - {pirate_event.description}，损失 {gold_loss} 金币"
            simulation.event_log.append(log_entry) 