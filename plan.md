# Comprehensive Plan to Address Device Control Issue

## Plan:

1. **Review Fuzzy Logic Implementation**:
   - Analyze the `fuzzy_tsukamoto(temp, humidity)` function to ensure that the membership functions and fuzzy inference rules are correctly defined. This will help in determining if the output values for the heater, fan, and humidifier are being calculated appropriately.

2. **Modify Control Logic**:
   - In the `control_device_fuzzy(temp, humidity)` function, consider implementing additional constraints or conditions to ensure that only one device can be activated at a time based on the fuzzy logic output. This may involve adjusting the thresholds or adding logic to prioritize which device should be turned on.

3. **Testing**:
   - After making the necessary changes, thoroughly test the system to ensure that triggering one device does not inadvertently activate others. This will involve simulating different temperature and humidity conditions to observe the behavior of the relays.

4. **Documentation**:
   - Update any relevant documentation to reflect the changes made to the fuzzy logic and control logic, ensuring that future developers understand the modifications.

## Follow-up Steps:
- Implement the changes in the `device_control.py` and `main.py` files.
- Test the functionality to confirm that the issue is resolved.
- Document any changes made for future reference.
