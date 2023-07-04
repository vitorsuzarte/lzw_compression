import time


def encodeLZ78(FileIn, FileOut):
    input_file = open(FileIn, 'rb')
    encoded_file = open(FileOut, 'wb')
    start = time.time()
    binary_data = input_file.read()
    dict_of_codes = {bytes([binary_data[0]]): b'1'}
    encoded_file.write(b'\x00' + bytes([binary_data[0]]))
    binary_data = binary_data[1:]
    combination = b''
    code = 2
    for byte in binary_data:
        combination += bytes([byte])
        if combination not in dict_of_codes:
            dict_of_codes[combination] = bytes(str(code), 'utf-8')
            if len(combination) == 1:
                encoded_file.write(b'\x00' + combination)
            else:
                encoded_file.write(dict_of_codes[combination[:-1]]
                                   + combination[-1:])
            code += 1
            combination = b''
    end = time.time()
    input_file.close()
    encoded_file.close()
    print(f"ENCODE TIME: {end - start}")
    return True


def decodeLZ78(FileIn, FileOut):
    coded_file = open(FileIn, 'rb')
    decoded_file = open(FileOut, 'wb')
    start = time.time()
    binary_data = coded_file.read()
    dict_of_codes = {b'': b''}
    decoded_file.write(dict_of_codes[b''])
    binary_data = binary_data[1:]
    combination = b''
    code = 1
    for byte in binary_data:
        if byte in b'1234567890':
            combination += bytes([byte])
            continue

        if combination not in dict_of_codes:
            dict_of_codes[combination] = b''
            decoded_file.write(dict_of_codes[combination] + bytes([byte]))
            combination = b''
            code += 1
    end = time.time()
    coded_file.close()
    decoded_file.close()
    print(f"DECODE TIME: {end - start}")


encodeLZ78('Imagens/01.png', 'encoded.bin')
decodeLZ78('encoded.bin', 'decoded.png')
