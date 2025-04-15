class RandomEvent:
    """随机事件基类"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def apply(self, simulation, ship=None, city=None):
        pass 