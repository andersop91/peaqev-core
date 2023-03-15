from statistics import mean
from ....models.hourselection.cautionhourtype import CautionHourType, MAX_HOURS

def normalize_prices(prices:list) -> list:
    min_price = min(prices)
    c = 0
    if min_price <= 0:
        c = abs(min_price) + 0.01
    ret = []
    for p in prices:
        pp = p+c
        divider = min_price if min_price > 0 else c
        ret.append(round(pp-divider,3))
    return ret

def get_offset_dict(normalized_hourdict: dict):
        ret = {}
        _prices = [p-min(normalized_hourdict.values()) for p in normalized_hourdict.values()]
        average_val = mean(_prices)
        for i in range(0,24):
            try:
                ret[i] = round((_prices[i]/average_val) - 1,2)
            except:
                ret[i] = 1
        return ret

def rank_prices(
        hourdict: dict, 
        normalized_hourdict: dict, 
        cautionhour_type: CautionHourType, 
        range_start: int = 0,
        adjusted_average:float = None, 
        blocknocturnal:bool = False
        ) -> dict:
    """Rank the normalized pricelist to find out which are going to become non- or caution-hours"""
    
    _adj_avg = adjusted_average
    if not isinstance(adjusted_average, (float,int)):
        _adj_avg = mean(hourdict.values()) 

    adj_average_norm = _adj_avg * (mean(normalized_hourdict.values())/mean(hourdict.values()))
    cautions = [h for h in normalized_hourdict if normalized_hourdict[h] > (adj_average_norm * 0.7)]
    cautions_dict = _cap_pricelist_available_hours(cautions, normalized_hourdict, cautionhour_type, blocknocturnal, range_start)
    maxval = max(hourdict.values())
    ret = {}
    
    for k, v in cautions_dict.items():
        ret[k] = {
            "val": hourdict[k], 
            "permax": round(hourdict[k] / maxval,2), 
            "force_non": v
            }
    if blocknocturnal:
        return ret
    else:
        return _discard_excessive_hours(ret)

def _cap_pricelist_available_hours(cautions: list, normalized_hourdict:dict, cautionhour_type: CautionHourType, blocknocturnal:bool, range_start: int) -> dict:
    ret = {c: False for c in cautions}
    _demand = 24 - MAX_HOURS.get(cautionhour_type)
    hours_sorted = [k for k, v in sorted(normalized_hourdict.items(), key=lambda item: item[1])]
    iterations = 0

    while len(cautions) < _demand and iterations < len(hours_sorted)*2:
        iterations+=1
        idx = hours_sorted.index(cautions[-1])
        if idx <= len(hours_sorted) -1:
            while idx+1 < len(hours_sorted):
                idx += 1
                next = hours_sorted[idx]
                if next not in cautions:
                    cautions.append(next)
                    ret[next] = True
                    break
        if idx >= 0:
            while idx-1 >= 0:
                idx -= 1
                prev = hours_sorted[idx]
                if prev not in cautions:
                    cautions.append(prev)
                    ret[prev] = True
                    break

    for i in get_nocturnal_stop(blocknocturnal, range_start):
        if i not in cautions:
            ret[i] = True
    return _sort_by_key(ret)

def _sort_by_key(input: dict) -> dict:
    _keys = list(input.keys())
    _keys.sort()
    return {i: input[i] for i in _keys}

def get_nocturnal_stop(blocknocturnal: bool = False, range_start: int = 0) -> list:
    _base = [23,0,1,2,3,4,5,6]
    print(range_start)
    if blocknocturnal:
        if range_start == 0:
            return _base
        ret = []
        for b in _base:
            if b >= range_start:
                ret.append(b-range_start)
            else:
                ret.append(24-range_start+b)
        return ret
    return []

def _discard_excessive_hours(hours: dict):
    """There should always be at least four regular hours before absolute_top_price kicks in."""
    while len(hours) >= 20:
        to_pop = dict(sorted(hours.items(), key=lambda item: item[1]['val']))    
        hours.pop(list(to_pop.keys())[0])
    return hours