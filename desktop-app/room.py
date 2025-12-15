class Room:
    def __init__(self, name, ip_address):
        self._name = name
        self._ip_address = ip_address
        self._current_temperature = 0.0
        self._current_humidity = 0.0
        self._min_temperature = 18.0
        self._max_temperature = 26.0
        self._min_humidity = 30
        self._max_humidity = 60
        self._has_gas = False
    
    def update_sensor_data(self, temperature, humidity):
        """Обновление данных с датчиков"""
        self._current_temperature = temperature
        self._current_humidity = humidity
    
    def is_temperature_normal(self):
        """Проверка нормальной температуры"""
        return self._min_temperature <= self._current_temperature <= self._max_temperature
    
    def is_humidity_normal(self):
        """Проверка нормальной влажности"""
        return self._min_humidity <= self._current_humidity <= self._max_humidity
    
    # Свойство: имя комнаты
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    # Свойство: IP-адрес
    @property
    def ip_address(self):
        return self._ip_address
    
    @ip_address.setter
    def ip_address(self, value):
        self._ip_address = value
    
    # Свойство: текущая температура
    @property
    def current_temperature(self):
        return self._current_temperature
    
    @current_temperature.setter
    def current_temperature(self, value):
        self._current_temperature = value
    
    # Свойство: текущая влажность
    @property
    def current_humidity(self):
        return self._current_humidity
    
    @current_humidity.setter
    def current_humidity(self, value):
        self._current_humidity = value
    
    # Свойство: минимальная температура
    @property
    def min_temperature(self):
        return self._min_temperature
    
    @min_temperature.setter
    def min_temperature(self, value):
        self._min_temperature = value
    
    # Свойство: максимальная температура
    @property
    def max_temperature(self):
        return self._max_temperature
    
    @max_temperature.setter
    def max_temperature(self, value):
        self._max_temperature = value
    
    # Свойство: минимальная влажность
    @property
    def min_humidity(self):
        return self._min_humidity
    
    @min_humidity.setter
    def min_humidity(self, value):
        self._min_humidity = value
    
    # Свойство: максимальная влажность
    @property
    def max_humidity(self):
        return self._max_humidity
    
    @max_humidity.setter
    def max_humidity(self, value):
        self._max_humidity = value
    
    # Свойство: наличие газа
    @property
    def has_gas(self):
        return self._has_gas
    
    @has_gas.setter
    def has_gas(self, value):
        self._has_gas = value