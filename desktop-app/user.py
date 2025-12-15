class User:
    def __init__(self, name, ip_address):
        self._name = name
        self._ip_address = ip_address
        self._clock_id = ""  # ✅ Добавляем clock_id
    
    def get_display_name(self):
        """Получить отображаемое имя"""
        return f"{self._name} ({self._ip_address})"
    
    # Свойство: имя пользователя
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    # Свойство: IP-адрес пользователя
    @property
    def ip_address(self):
        return self._ip_address
    
    @ip_address.setter
    def ip_address(self, value):
        self._ip_address = value
    
    # ✅ Свойство: clock_id пользователя
    @property
    def clock_id(self):
        return self._clock_id
    
    @clock_id.setter
    def clock_id(self, value):
        self._clock_id = value