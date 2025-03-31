def fuzzy_tsukamoto(temp, humidity):
    # Membership functions for temperature
    dingin = max(0, min(1, (22 - temp) / (22 - 0)))
    normal = max(0, min((temp - 22) / (30 - 22), (30 - temp) / (30 - 22)))
    panas = max(0, min(1, (temp - 30) / (40 - 30)))
    
    # Membership functions for humidity
    rendah = max(0, min(1, (40 - humidity) / (40 - 0)))
    normal = max(0, min((humidity - 40) / (60 - 40), (60 - humidity) / (60 - 40)))
    tinggi = max(0, min(1, (humidity - 60) / (100 - 60)))
    
    # Inference based on fuzzy rules
    output_heater = min(dingin, rendah)
    output_fan = min(panas, normal)
    output_humidifier = min(dingin, normal)
    
    # Defuzzification using weighted average method
    heater_value = output_heater * 100  # Scale 0-100
    fan_value = output_fan * 100
    humidifier_value = output_humidifier * 100
    
    return heater_value, fan_value, humidifier_value
