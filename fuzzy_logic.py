def fuzzy_tsukamoto(temp, humidity):
    # Membership functions for temperature (piecewise linear)
    cold = 1 if temp <= 0 else 0 if temp >= 22 else (22 - temp) / 22
    normal = 0 if temp <= 22 else 0 if temp >= 30 else (temp - 22) / 8
    hot = 0 if temp <= 30 else 1 if temp >= 40 else (temp - 30) / 10

    # Membership functions for humidity (piecewise linear)
    low = 1 if humidity <= 0 else 0 if humidity >= 40 else (40 - humidity) / 40
    normal_h = 0 if humidity <= 40 else 0 if humidity >= 60 else (humidity - 40) / 20
    high = 0 if humidity <= 60 else 1 if humidity >= 100 else (humidity - 60) / 40

    # Determine highest membership category for temperature
    temp_memberships = {'cold': cold, 'normal': normal, 'hot': hot}
    temp_category = max(temp_memberships, key=temp_memberships.get)

    # Determine highest membership category for humidity
    humidity_memberships = {'low': low, 'normal': normal_h, 'high': high}
    humidity_category = max(humidity_memberships, key=humidity_memberships.get)

    # Device control decisions based on highest membership categories
    heater_val = 100 if temp_category == 'cold' else 0
    fan_val = 100 if temp_category == 'hot' else 0
    humidifier_val = 100 if humidity_category == 'low' else 0

    return heater_val, fan_val, humidifier_val
