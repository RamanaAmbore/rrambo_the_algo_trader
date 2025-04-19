# src/app_state/schedule_time.py
from src.app_state.base import StateComponent
from src.core.decorators import locked_update

class ScheduleTimeState(StateComponent):
    def __init__(self, lock):
        super().__init__(lock)
        self._data = {}

    @locked_update(StateComponent.lock)
    def set(self, value):
        super().set_data(value)

    @locked_update(StateComponent.lock)
    def update(self, key, value):
        super().update(key, value)

    @locked_update(StateComponent.lock)
    def remove(self, key):
        super().remove(key)