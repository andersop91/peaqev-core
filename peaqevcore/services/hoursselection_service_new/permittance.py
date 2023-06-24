from .models.hour_price import HourPrice
from ...models.hourselection.cautionhourtype import CautionHourType
from .models.hour_type import HourType
from statistics import mean


# def set_initial_permittance(
#     hour_prices: list[HourPrice], price_mean: float, price_stdev: float
# ) -> None:
#     for hp in hour_prices:
#         print(hp.dt, hp.price, price_mean, price_stdev)
#         if hp.hour_type == HourType.BelowMin:
#             hp.permittance = 1.0
#         elif hp.hour_type == HourType.AboveMax:
#             hp.permittance = 0.0
#         elif hp.price < price_mean - price_stdev:
#             hp.permittance = 1.0
#         elif hp.price > price_mean + price_stdev:
#             hp.permittance = 0.0
#         else:
#             hp.permittance = round(
#                 1.0 - ((hp.price - price_mean + price_stdev) / (2 * price_stdev)), 2
#             )
#     # return hour_prices


def set_initial_permittance(
    hours: list[HourPrice],
    price_mean: float,
    price_stdev: float,
    avg7: float | None = None,
) -> None:
    scaling_factor = scale_permittance(price_stdev)
    for hour in hours:
        if hour.hour_type == HourType.BelowMin:
            hour.permittance = 1.0
        elif hour.hour_type == HourType.AboveMax:
            hour.permittance = 0.0
        else:
            diff_avg_price = price_mean - hour.price
            diff_avg_7day_price = (avg7 or price_mean) - hour.price
            hour.permittance = mean(
                [
                    max(0, min(1, diff_avg_price / (price_mean * scaling_factor))),
                    max(
                        0,
                        min(
                            1,
                            diff_avg_7day_price
                            / ((avg7 or price_mean) * scaling_factor),
                        ),
                    ),
                ]
            )


def scale_permittance(stdev: float) -> float:
    if stdev == 0:
        return 1.0
    return max(0.1, min(1.0, 1.0 / (1.0 + stdev)))


def set_scooped_permittance(
    hour_prices: list[HourPrice], caution_hour_type: CautionHourType
) -> None:
    lo_cutoff = 0.4
    hi_cutoff = 0.75
    max_hours = 24  # todo: add support for 96 if quarterly
    match caution_hour_type:
        case CautionHourType.SUAVE:
            hi_cutoff = 0.7
        case CautionHourType.INTERMEDIATE:
            lo_cutoff = 0.5
            hi_cutoff = 0.7
        case CautionHourType.AGGRESSIVE:
            lo_cutoff = 0.6
        case CautionHourType.SCROOGE:
            lo_cutoff = 0.6
            max_hours = 8  # todo: add support for 32 if quarterly

    for hp in hour_prices:
        _t = hp.permittance
        if hp.permittance <= lo_cutoff:
            hp.permittance = 0.0
        elif hp.permittance >= hi_cutoff:
            hp.permittance = 1.0
        else:
            hp.permittance = round(hp.permittance, 2)
    # return hour_prices
