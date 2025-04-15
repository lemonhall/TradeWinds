import random
from typing import Tuple, Dict

def perform_trading_strategy(simulation, ship):
    """简单的交易策略：低价买入高价卖出，考虑商品质量"""
    if not ship.current_city:
        return
    
    current_city = ship.current_city
    other_cities = [name for name in simulation.city_names if name != current_city.name]
    if not other_cities: # 如果只有一个城市
        return
    
    # 寻找当前城市最适合购买并转卖到其他城市的商品
    best_buy, best_destination, best_quality = _find_best_trade(simulation, ship, current_city, other_cities)
    
    # 先卖掉所有货物
    _sell_all_cargo(ship, current_city)
    
    # 如果找到了有利可图的交易
    if _execute_trade(ship, current_city, best_buy, best_destination, best_quality, simulation.trade_map):
        return # 完成交易决策，等待航行

    # 如果没有找到好的买入机会，或者没有装载任何货物，随机选择下一个目的地
    next_city_name = random.choice(other_cities)
    ship.set_route(current_city, simulation.cities[next_city_name], simulation.trade_map)
    
def _find_best_trade(simulation, ship, current_city, other_cities) -> Tuple[str, object, str]:
    """
    寻找最佳交易商品、目的地和质量
    
    考虑不同质量的商品和船只偏好
    """
    best_buy = None
    best_buy_score = 0
    best_destination = None
    best_quality = "普通"
    
    for good in current_city.current_prices:
        # 获取当前城市中所有可用质量的商品
        available_qualities = current_city.get_available_qualities(good)
        
        if not available_qualities:  # 没有库存，跳过
            continue
            
        # 遍历每种可用质量
        for quality, amount in available_qualities.items():
            if amount <= 0:
                continue
                
            # 获取当前质量商品的价格
            buy_price = current_city.get_quality_price(good, quality)
            if buy_price <= 0:
                continue
                
            # 在其他城市寻找最高价和对应的城市
            potential_destinations = []
            for city_name in other_cities:
                city = simulation.cities[city_name]
                # 假设在其他城市能以普通质量卖出（保守估计）
                # 实际上，应该查询能获得的最高价格
                sell_price = city.current_prices[good]
                potential_destinations.append((sell_price, city_name))
            
            if not potential_destinations:
                continue
                
            max_price, dest_city_name = max(potential_destinations, key=lambda x: x[0])
            
            # 计算利润率而不是绝对利润
            profit_ratio = max_price / buy_price if buy_price > 0 else 0
            
            # 根据船只偏好调整评分
            score_adjustment = 1.0
            if ship.quality_preference == "质量" and quality in ["精良", "极品"]:
                score_adjustment = 1.2  # 偏好高质量的船只更愿意交易高质量商品
            elif ship.quality_preference == "价格" and quality in ["粗糙", "普通"]:
                score_adjustment = 1.1  # 偏好低价的船只更愿意交易便宜商品
                
            score = profit_ratio * score_adjustment
            
            if score > best_buy_score:
                best_buy_score = score
                best_buy = good
                best_destination = simulation.cities[dest_city_name]
                best_quality = quality
            
    return best_buy, best_destination, best_quality

def _sell_all_cargo(ship, city):
    """卖出船上所有货物，考虑质量"""
    has_cargo_sold = False
    for good in list(ship.cargo.keys()): # 使用 list 避免在迭代时修改字典
        if ship.cargo[good] > 0:
            ship.unload_cargo(good, city.current_prices[good])
            has_cargo_sold = True
    
    # 如果有货物售出，记录资金历史
    if has_cargo_sold:
        ship.gold_history.append(ship.gold)
        
def _execute_trade(ship, current_city, best_buy, best_destination, best_quality, trade_map):
    """
    执行交易，如果成功返回True
    考虑商品质量因素
    """
    if best_buy and best_destination:
        # 获取指定质量商品的价格
        buy_price = current_city.get_quality_price(best_buy, best_quality)
        if buy_price <= 0:
            return False
            
        # 用50%的资金购买
        budget = ship.gold * 0.5
        amount_to_buy = budget / buy_price
        
        # 尝试装载货物，指定质量
        loaded_amount = ship.load_cargo(
            best_buy, amount_to_buy, buy_price, best_quality
        )
        
        # 如果成功装载了货物，设定去最高价城市的路线
        if loaded_amount > 0:
            # 记录资金历史
            ship.gold_history.append(ship.gold)
            ship.set_route(current_city, best_destination, trade_map)
            return True
            
    return False 