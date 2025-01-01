# Definisi himpunan fuzzy
temp_fuzzy = {
    "low": [0, 15, 20],
    "normal": [18, 25, 30],
    "high": [28, 35, 40]
}

humidity_fuzzy = {
    "low": [0, 20, 40],
    "normal": [30, 50, 70],
    "high": [60, 80, 100]
}

control_fuzzy = {
    "off": [0, 0, 25],
    "low": [20, 40, 60],
    "medium": [50, 70, 90],
    "high": [80, 100, 100]
}

def fuzzy_membership(value, ranges):
    if ranges[0] <= value <= ranges[1]:
        return (value - ranges[0]) / (ranges[1] - ranges[0])
    elif ranges[1] <= value <= ranges[2]:
        return (ranges[2] - value) / (ranges[2] - ranges[1])
    else:
        return 0

def defuzzification(fuzzy_outputs):
    total_weight = 0
    weighted_sum = 0
    for output, degree in fuzzy_outputs.items():
        range_mid = (control_fuzzy[output][1] + control_fuzzy[output][2]) / 2
        weighted_sum += range_mid * degree
        total_weight += degree
    return weighted_sum / total_weight if total_weight != 0 else 0

def get_current_time():
    import time
    gmt_offset = 7 * 3600
    adjusted_time = time.time() + gmt_offset
    local_time = time.localtime(adjusted_time)
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        local_time[0], local_time[1], local_time[2], local_time[3], local_time[4], local_time[5]
    )