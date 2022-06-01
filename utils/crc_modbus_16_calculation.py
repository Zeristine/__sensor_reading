def right_shift_and_get_last_bit(number):
    return number >> 1, (number - (number >> 1 << 1))


def crc_calculate_1_loop(previous, current, step):
    xor_result = previous ^ current
    n = 0
    right_shift_result = xor_result
    last_bit = 0
    while n != step:
        right_shift_result, last_bit = right_shift_and_get_last_bit(
            right_shift_result)
        if last_bit == 1:
            right_shift_result = right_shift_result ^ 0xA001
        n = n + 1
    return right_shift_result


def crc_modbus_calculate(message_array):
    start = 0xFFFF
    if isinstance(message_array, list):
        for bit in message_array:
            start = crc_calculate_1_loop(start, bit, 8)
    high_byte, low_byte = divmod(start, 0x100)
    return high_byte, low_byte


def covnert_message_to_all_nummber(message_array):
    return [int(value, 16) if isinstance(value, str) else value for value in message_array]


def generate_modbus_message(message_array):
    message_converted = covnert_message_to_all_nummber(message_array)
    crc_high_byte, crc_low_byte = crc_modbus_calculate(message_converted)
    message_converted.append(crc_low_byte)
    message_converted.append(crc_high_byte)
    return message_converted


# Testing Area
# Sample
if __name__ == '__main__':
    soil_detection_temperature = [0x02, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x38]
    soil_detection_humidity = [0x02, 0x03, 0x00, 0x07, 0x00, 0x01, 0x35, 0xF8]
    soil_detection_ec = [0x02, 0x03, 0x00, 0x08, 0x00, 0x01, 0x05, 0xFB]
    print("Sample:")
    print(soil_detection_temperature)
    print(soil_detection_humidity)
    print(soil_detection_ec)
    # Test
    print("Mixed messages:")
    messages = [
        ["0x15", "0x06", "0x00", "0x00", "0x00", "0x255"]
        # [0x01, 0x03, 0x00, 0x01, 0x00, 0x01],
        # [0x02, 0x03, 0x00, 0x07, 0x00, 0x01],
        # [0x02, 0x03, 0x00, 0x08, 0x00, 0x01],
        # ["0x02", "0x03", '0x00', '0x07', '0x00', '0x01'],
        # ['0x02', '0x03', '0x00', '0x08', '0x00', '0x01']
    ]
    for message in messages:
        print(generate_modbus_message(message))
