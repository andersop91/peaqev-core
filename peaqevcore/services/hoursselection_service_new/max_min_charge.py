from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timedelta
from ..hoursselection_service_new.models.hour_price import HourPrice
from ..hoursselection_service_new.models.hour_type import HourType
from ..hoursselection_service_new.models.list_type import ListType
import copy

if TYPE_CHECKING:
    from .hourselection_service import HourSelectionService
from typing import Tuple
from .models.max_min_model import MaxMinModel

MINIMUM_DIFFERENCE = 0.1


class MaxMinCharge:
    def __init__(self, service: HourSelectionService, min_price: float | None) -> None:
        self.model = MaxMinModel(min_price=min_price)  # type: ignore
        self.parent = service
        self.active: bool = False

    @property
    def average_price(self) -> float | None:
        if not self.active:
            return None
        return self.model.caluclate_average_price(
            self.model.input_hours, self.total_charge, self.parent.dtmodel.dt
        )

    @property
    def original_average_price(self) -> float | None:
        return self.model.caluclate_average_price(
            self.model.original_input_hours,
            self.original_total_charge,
            self.parent.dtmodel.dt,
        )

    @property
    def total_charge(self) -> float | None:
        if not self.active:
            return None
        return self.model.calculate_total_charge(
            self.model.input_hours, self.parent.dtmodel.dt
        )

    @property
    def original_total_charge(self) -> float:
        return self.model.calculate_total_charge(
            self.parent.future_hours, self.parent.dtmodel.dt
        )

    @property
    def non_hours(self) -> list:
        return [
            hp.dt
            for hp in self.model.input_hours
            if hp.permittance == 0 and hp.dt >= self.parent.dtmodel.dt
        ]

    @property
    def dynamic_caution_hours(self) -> dict:
        return {
            hp.dt: hp.permittance
            for hp in self.model.input_hours
            if 0 < hp.permittance < 1 and hp.dt >= self.parent.dtmodel.dt
        }

    async def async_update(
        self,
        avg24,
        peak,
        max_desired: float,
        session_energy: float | None = None,
        car_connected: bool = False,
    ) -> None:
        if not car_connected:
            await self.async_setup(max_charge=peak)
        _session = session_energy or 0
        _desired = max_desired - _session
        _avg24 = round((avg24 / 1000), 1)
        self.model.expected_hourly_charge = peak - _avg24
        self.select_hours_for_charge(
            copy.deepcopy(self.model.original_input_hours), _desired
        )

    def select_hours_for_charge(
        self, hours: list[HourPrice], desired_charge: float
    ) -> None:
        hours = [hour for hour in hours if hour.permittance != 0 and not hour.passed]
        if self._get_charge_sum(hours) <= desired_charge:
            return
        total_charge = 0
        _desired = min([desired_charge, self._get_charge_sum(hours)])
        hours.sort(key=lambda x: x.price)
        for hour in hours:
            hour_charge = hour.permittance * self.model.expected_hourly_charge
            perm = min(
                1, max((_desired - total_charge) / self.model.expected_hourly_charge, 0)
            )
            total_charge += hour_charge * perm
            hour.permittance = round(perm, 2)
            if self._get_charge_sum(hours) == desired_charge:
                break
        self.model.input_hours = hours

    def _get_charge_sum(self, hours: list[HourPrice]) -> float:
        return sum(
            [
                hour.permittance * self.model.expected_hourly_charge
                for hour in hours
                if not hour.passed
            ]
        )

    def _set_expected_charge(self, desired, peak, avg24) -> float:
        return (desired - self.total_charge) / (peak - avg24)

    async def async_initial_charge(self, avg24, peak) -> float:
        _avg24 = round((avg24 / 1000), 1)
        self.model.expected_hourly_charge = peak - _avg24
        total = 24 * (peak - _avg24)  # todo: fix 24 to be dynamic
        total -= len(self.non_hours) * (peak - _avg24)
        total -= sum(self.dynamic_caution_hours.values()) * (peak - _avg24)
        return total

    async def async_sum_charge(self, avg24, peak) -> float:
        total = 0
        for k in self.model.input_hours:
            total += (peak - avg24) * k.permittance
        return total

    def _service_caution_hours(self) -> dict:
        return {
            hp.dt: hp.permittance
            for hp in self.parent.model.hours_prices
            if not hp.passed and 0.0 < hp.permittance < 1.0
        }

    def _service_non_hours(self) -> list:
        return [
            hp.dt
            for hp in self.parent.model.hours_prices
            if not hp.passed and hp.permittance == 0.0
        ]

    async def async_setup(
        self,
        max_charge: float,
    ) -> None:
        if max_charge == 0:
            self.active = False
            return
        if not self.active:
            self.model.input_hours = copy.deepcopy(self.parent.future_hours)
            self.model.original_input_hours = copy.deepcopy(self.model.input_hours)
            self.active = True
