# src/app_state/schedule_time.py
from src.app_state_manager.base import StateComponent
from src.core.decorators import lock_it_for_update

class ScheduleTimeState(StateComponent):
    def __init__(self, lock):
        super().__init__(lock)
        self._data = {}

    @lock_it_for_update(StateComponent.lock)
    def set(self, value):
        super().set_data(value)

    @lock_it_for_update(StateComponent.lock)
    def update(self, key, value):
        super().update(key, value)

    @lock_it_for_update(StateComponent.lock)
    def remove(self, key):
        super().remove(key)