import logging
import time
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class KillSwitch:
    def __init__(
        self, 
        sensor: str, 
        update_interval:int = 120, 
        grace_interval:int = 120
        ):
        self._update_interval: int = update_interval
        self._grace_interval: int = grace_interval
        self._bound_sensor: str = sensor
        self._last_update: int = 0
        self._grace_period: bool = False
        self._grace_period_start: int = 0
        self._is_dead: bool = False

    @property
    def is_dead(self) -> bool:
        return self._is_dead

    @property
    def check(self):
        if self._grace_period:
            if time.time() - self._grace_period_start > self._grace_interval:
                _LOGGER.error(f"{datetime.now()} - Error! The grace-period for sensor {self._bound_sensor} has timed out. Peaqev will stop charging. Please check {self._bound_sensor} and it's integration.")
                self._is_dead = True
                #self.__init__(self._bound_sensor, self._update_interval, self._grace_interval)
        elif time.time() - self._last_update > self._update_interval:
            _LOGGER.warning(f"{datetime.now()} - Caution! The sensor {self._bound_sensor} has not been updated for {self._update_interval} seconds. In {self._grace_interval} seconds the charger will be stopped unless this sensor comes alive again.")
            self._grace_period = True
            self._grace_period_start = time.time()

    @property
    def update(self):
        self._last_update = time.time()
        self._grace_period = False
        self._grace_period_start = 0


# k = KillSwitch("magnus_sensor", 3, 6)
# k.update()
# time.sleep(1)
# k.check()
# k.update()
# time.sleep(4)
# k.check()
# time.sleep(5)
# k.check()
# time.sleep(2)
# k.check()
