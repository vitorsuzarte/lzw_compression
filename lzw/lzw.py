import base64
import os
import sys
import time
import io
from PIL import Image
from base64 import b64encode

def get_file_content(file_path, is_compression = False):
    if file_info["is_image"] and is_compression:
        image = Image.open(file_path)
        file_info["image_width"] = image.size[0]
        file_info["image_heigth"] = image.size[1]
        pixel_array = list(image.getdata())
        pixel_string = ','.join([f"{r},{g},{b}" for r, g, b in pixel_array])
        return pixel_string
    else:
        with open(file_path, 'r') as file:
            return file.read()

def create_image_from_pixels(pixel_array, image_width, image_height):
    image = Image.new("RGB", (image_width, image_height))
    image.putdata(pixel_array)
    return image

def string_to_pixel_array(pixel_string):
    pixel_values = pixel_string.split(',')  # Split the string by the delimiter
    pixel_array = [(int(pixel_values[i]), int(pixel_values[i+1]), int(pixel_values[i+2])) 
                   for i in range(0, len(pixel_values), 3)]  # Convert string values to integers and organize as tuples
    return pixel_array

def write_to_file(file_path, content, is_decompression = False):
    if file_info["is_image"] and is_decompression:
        image = create_image_from_pixels(string_to_pixel_array(content), file_info["image_width"], file_info["image_heigth"])
        image.save(f"{file_info['decompression_file_path']}", f"{file_info['extension'][1:].upper()}")
    else:
        write = open(file_path, "w")
        write.write(content)
        write.close()


def encode():
    initial_time = time.time()
    
    [encoded_content_string, dictionary] = encode_lzw()
    
    write_to_file(file_info['compreesion_file_path'], encoded_content_string)
    
    final_time = time.time()
    
    final_size = os.path.getsize(file_info['compreesion_file_path'])
    
    return final_size, final_time - initial_time, dictionary


def getAlphabet(file_content):
    dictionary = dict()
    i = 0
    index = 1
    while i < len(file_content):
        if file_content[i] in dictionary:
            i = i + 1
        else:
            dictionary[file_content[i]] = index
            index = index + 1
    return dictionary, index


def encode_lzw():    
    file_content = get_file_content(file_info['file_name'], True)

    # iniciando o dicionario com o alfabeto usado no arquivo
    [dictionary, index] = getAlphabet(file_content)

    # processo de compressão lzw
    i = 0
    encoded = []
    while i < len(file_content):
        j = 0
        stringToBeSaved = file_content[i]
        # enquanto a string a ser salva está presente no dicionário E não estamos no fim do arquivo
        while stringToBeSaved in dictionary and i+j < len(file_content):
            
            # salva o indicie da entrada no dicionario principal
            indexInDictionary = dictionary[stringToBeSaved]
            length = len(stringToBeSaved)
            
            #garante que sempre exista uma proxima letra 
            if (i+j == len(file_content) - 1):
                break
            
            #busca a proxima letra para compor uma entrada maior
            j = j + 1
            stringToBeSaved = stringToBeSaved + file_content[i+j]
        
        i = i + length
        encoded.append(indexInDictionary)
        
        #salva no dicionário a entrada que não se encontrava no mesmo  
        if (stringToBeSaved not in dictionary):
            dictionary[stringToBeSaved] = index
        index = index + 1

    #transforma todos os códigos do array em uma só string separando-os por uma vírgula 
    encoded_content_string = ','.join((str(num) for num in encoded))

    return encoded_content_string, dictionary


def decode(dictionary):
    initial_time = time.time()
    
    file_content_string = get_file_content(file_info["compreesion_file_path"])
    file_content_list = [int(num) for num in file_content_string.split(',')]
    
    decoded_content_string = decode_lzw(file_content_list, dictionary)

    write_to_file(file_info["decompression_file_path"], decoded_content_string, True)

    final_time = time.time()
    return [final_time - initial_time]


def decode_lzw(compressed_content_list, dictionary):
    decoded_content_string = ''
    inverted_dict = {valor: chave for chave, valor in dictionary.items()}
    
    for value in compressed_content_list:
        if value in inverted_dict:
            decoded_content_string += inverted_dict[value]
    return decoded_content_string


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        exit("You must specify the text which will be encoded! (Run with python3 lz77.py abracadabra)")
    file_name = ' '.join(sys.argv[1:2])
    
    
    # file_name = "analisecompress-o/Imagens/01.png"
    name, extension = os.path.splitext(file_name)
    
    image_extensions = [".jpg", ".jpeg", ".png"]
    
    file_info = dict()
    file_info['file_name'] = file_name
    file_info['extension'] = extension
    file_info['decompression_file_path'] = f"{name}_descomprimido{extension}"
    file_info['compreesion_file_path'] = f"{name}_comprimido.txt"
    file_info['initial_size'] = os.path.getsize(file_name)
    file_info['is_image'] = extension in image_extensions
    
    [final_size, total_compression_time, dictionary] = encode()
    [total_decompression_time] = decode(dictionary)

    print(f"tamanho inicial do arquivo: {file_info['initial_size']}")
    print(f"tamanho do arquivo comprimido: {final_size}")
    print(f"tempo de compressao: {total_compression_time}")
    print(f"tempo de descompressao: {total_decompression_time}")
