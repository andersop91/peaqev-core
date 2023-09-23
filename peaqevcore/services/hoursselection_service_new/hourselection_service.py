from datetime import timedelta, datetime
import logging
from .models.stop_string import AllowanceObj, set_allowance_obj
from .models.datetime_model import DateTimeModel
from .models.hour_price import HourPrice
from .models.hourselection_service_model import HourSelectionServiceModel
from ...models.hourselection.hourselection_options import HourSelectionOptions
from .hourselection_calculations import normalize_prices, do_recalculate_prices, get_average_kwh_price
from .permittance import (
    set_initial_permittance,
    set_scooped_permittance,
    set_blank_permittance,
    set_min_allowed_hours,
)
from statistics import stdev, mean
from .max_min_charge import MaxMinCharge

_LOGGER = logging.getLogger(__name__)

class HourSelectionService:
    def __init__(self, options: HourSelectionOptions = HourSelectionOptions()):
        self.options = options
        self.dtmodel = DateTimeModel()
        self.model = HourSelectionServiceModel()
        self.max_min = MaxMinCharge(service=self, min_price=self.options.min_price)

    @property
    def all_hours(self) -> list[HourPrice]:
        self.update()
        return self.model.hours_prices

    @property
    def future_hours(self) -> list[HourPrice]:
        self.update()
        return self.model.get_future_hours(self.dtmodel)

    @property
    def display_future_hours(self) -> list[HourPrice]:
        if self.max_min.active and not self.max_min.overflow:
            return self.max_min.future_hours(self.dtmodel)
        return self.future_hours

    @property
    def allowance(self) -> AllowanceObj:
        self.update()
        return set_allowance_obj(self.dtmodel, self.display_future_hours)

    @property
    def average_kwh_price(self) -> float:
        return round(get_average_kwh_price(self.future_hours), 2)

    @property
    def offset_dict(self) -> dict:
        return self.model.get_offset_dict(self.dtmodel.dt)

    def update(self):  
        self.model.hours_prices = [hp for hp in self.model.hours_prices if hp.dt.date() >= self.dtmodel.hdate]        
        # if len(self.model.hours_prices) > 1:
        #     print(f"hourseelection_service.model.hours_prices now has a len of {len(self.model.hours_prices)}. the oldest is {self.model.hours_prices[0].dt} and the newest is {self.model.hours_prices[-1].dt}")
        # else:
        #     raise Exception (f"hourseelection_service.model.hours_prices now has a len of {len(self.model.hours_prices)}. the oldest is {self.model.hours_prices[0].dt} and the newest is {self.model.hours_prices[-1].dt}")
        for hp in self.model.hours_prices:            
            hp.set_passed(self.dtmodel)        
        if len(self.model.get_future_hours(self.dtmodel)) >= 24:
            set_scooped_permittance(
                self.model.get_future_hours(self.dtmodel), self.options.cautionhour_type_enum
            )        

    async def async_update(self):
        self.update()

    def clean_prices(self, prices, prices_tomorrow) -> dict:
        expected_date = self.dtmodel.hdate
        price_dict: dict = {}
        for idx, i in enumerate(prices):
            price_dict[datetime(expected_date.year, expected_date.month, expected_date.day, idx, 0, 0)] = i
        if len(prices_tomorrow):
            expected_date = self.dtmodel.hdate_tomorrow
            for idx, i in enumerate(prices_tomorrow):
                price_dict[datetime(expected_date.year, expected_date.month, expected_date.day, idx, 0, 0)] = i
        return price_dict

    async def async_update_prices(self, prices: list[float], prices_tomorrow: list[float] = []):
        price_dict = self.clean_prices(prices, prices_tomorrow)
        self.model.prices_today = prices  # clean first
        self.model.prices_tomorrow = prices_tomorrow  # clean first
        if do_recalculate_prices(price_dict=price_dict, hours_prices=self.model.hours_prices, hdate=self.dtmodel.hdate):
            print(f"do recalculate prices {len(prices)} {len(prices_tomorrow)}")
            _LOGGER.debug(f"do recalculate prices {len(prices)} {len(prices_tomorrow)}")
            self._create_prices(prices, prices_tomorrow)
        else:
            print(f"NOT recalculate prices {len(prices)} {len(prices_tomorrow)}")
            _LOGGER.debug(f"NOT recalculate prices {len(prices)} {len(prices_tomorrow)}")
            await self.async_update()
        self.max_min.get_hours()

    async def async_update_adjusted_average(self, adjusted_average: float) -> None:
        self.model.adjusted_average = adjusted_average
        self.update()
        if len(self.model.hours_prices) > 0:
            self._set_permittance()
        else:
            await self.async_update()

    def _create_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> None:
        # todo: fix to allow 23, 24,25, 92, 96, 100 for dst-dates.
        self.model.hours_prices = []
        match len(prices):
            case 23 | 24 | 25:
                self._create_hour_prices(prices, prices_tomorrow, is_quarterly=False)
            case 92 | 96 | 100:
                self._create_hour_prices(prices, prices_tomorrow, is_quarterly=True)
            case _:
                raise ValueError(
                    f"Length of pricelist must be either 23,24,25,92,96 or 100. Your length is {len(prices)}"
                )

    def _create_hour_prices(
        self,
        prices: list[float],
        prices_tomorrow: list[float] = [],
        is_quarterly: bool = False,
    ) -> None:
        # todo: handle here first if prices or prices_tomorrow are 92 or 100 in length (dst shift)
        self.model.use_quarters = is_quarterly
        self.model.set_hourprice_lists(prices, prices_tomorrow, self.options, self.dtmodel.hdate, self.dtmodel.hdate_tomorrow, self.dtmodel.is_passed)
        self._set_permittance()

    def _set_permittance(self) -> None:
        prices = normalize_prices(
            [
                hp.price
                for hp in self.model.hours_prices
                if hp.dt.date() >= self.dtmodel.hdate
            ]
        )
        self.model.set_offset_dict(prices, self.dtmodel.dt.date())
        if not self.is_flat([h.price for h in self.model.hours_prices if not h.passed]):
            set_initial_permittance(
                self.model.hours_prices,
                self.model.adjusted_average,
                self.options.non_hours
            )
        else:
            set_blank_permittance(self.model.hours_prices)
        set_scooped_permittance(
            self.model.hours_prices,
            self.options.cautionhour_type_enum,
        )
        set_min_allowed_hours(
            self.model.hours_prices,
            self.options.cautionhour_type_enum,
        )

    @staticmethod
    def is_flat(prices: list[float]) -> bool:
        """if the fsd is below a score of 8(%) it is considered flat"""
        return stdev(prices)*100/mean(prices) < 8