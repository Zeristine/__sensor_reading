import math

def right_shift_and_get_last_bit(number): 
    return number >> 1, (number - (number >> 1 << 1))

def crc_calculate_1_loop(previous, current, step):
    xor_result = previous ^ current
    n = 0   
    right_shift_result = xor_result
    last_bit = 0
    while n != step:
        right_shift_result , last_bit = right_shift_and_get_last_bit(right_shift_result)
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

hex_string = "0xAA"

an_integer = int(hex_string, 16)

hex_value = hex(an_integer)
# messages = [[0x02, 0x03, 0x00, 0x06, 0x00, 0x01],
#             [0x02, 0x03, 0x00, 0x07, 0x00, 0x01],
#             [0x02, 0x03, 0x00, 0x08, 0x00, 0x01]]

# for message in messages:
#     high_byte, low_byte = crc_modbus_calculate(message)
#     print(hex(high_byte) + "," + hex(low_byte))
    