from pytube import YouTube
import matplotlib.pyplot as plt
from pydub import AudioSegment
from moviepy.video.io.VideoFileClip import VideoFileClip
import numpy as np
import math
from collections import Counter
import random
import base64
import ast
from Crypto.Hash import SHA256

LINK = "https://www.youtube.com/watch?v=etAywtK34V4"
AUDIO_FILE = "audio_clip.mp3"
WYNIK = "wynik.txt"
PIERWSZA_RAMKA = 3000000
LICZBA_RAMEK = 5000

#POBIERANIE FILMU I KONWERSJA DO PLIKU MP3
def generator(link, outputfile):
    yt = YouTube(link, use_oauth=True, allow_oauth_cache=True)
    stream = yt.streams.get_highest_resolution()
    filename = stream.download()
    clip = VideoFileClip(filename)
    clip.audio.write_audiofile(outputfile)
    clip.close()

#MIESZANIE BITÓW WEDŁUG WZORU
def mix_bits(input_bits):
    if(len(input_bits)<3):
        return input_bits
    
    mixed_bits = [input_bits[0],input_bits[1]]
    curentstep=2
    while(len(mixed_bits)<len(input_bits)):
        a=len(mixed_bits)-1
        b=0
        if(curentstep+a>len(input_bits)):
            a=len(input_bits)-curentstep
        for i in range(a):
            mixed_bits.insert(b*2+1, input_bits[curentstep])
            b=b+1
            curentstep=curentstep+1

    return mixed_bits

#WYKONYWANIE FUNKCJI XOR NA KAŻDYCH KOLEJNYCH 2 BITACH(TABLICA NA WYJŚCIU JEST 2 RAZY KRÓTSZA OD TABLICY NA WEJŚCIU)
def xor_operation(input_bits):
    result = []
    for i in range(0, len(input_bits), 2):
        result.append(input_bits[i] ^ input_bits[i+1])
    return result

#WPISANIE 4 NAJMNIEJ ZNACZĄCYCH BITÓW LICZBY DO TABLICY
def int_to_bits(n):
    n = n & 0xF
    bit_array = [int(bit) for bit in bin(n)[2:]]
    while len(bit_array) < 4:
        bit_array.insert(0, 0)
    return bit_array

#KONWERSJA TABLICY BITÓW NA TABLICE 8-BITOWYCH LICZB CAŁKOWITYCH
def bits_to_ints(bit_array):
    num_bits = len(bit_array)
    num_ints = num_bits // 8
    int_array = []

    for i in range(num_ints):
        start_index = i * 8
        end_index = start_index + 8
        segment = bit_array[start_index:end_index]
        segment_value = int("".join(map(str, segment)), 2)
        int_array.append(segment_value)
    return int_array

#KONWERSJA TABLICY BITÓW NA LICZBĘ CAŁKOWITĄ
def bits_to_int(bit_array):
    bit_string = ''.join(str(bit) for bit in bit_array)
    value = int(bit_string, 2)
    return value

#MIESZANIE I WYKONYWANIE FUNKCJI XOR NA WSZYSTKICH RAMKACH RAZEM
def long_postprocessing(num_of_values, input_values, start_value):
    result = []
    for i in range(num_of_values):
        bit_tab = int_to_bits(input_values[start_value+i])
        result.extend(bit_tab)
    mixed_segment = mix_bits(result)
    xored_segment = xor_operation(mixed_segment)
    return xored_segment


def generate_prime(lenght, start):
    audio = AudioSegment.from_file(AUDIO_FILE, format="mp3")
    frames = audio.get_array_of_samples()
    bits = long_postprocessing(LICZBA_RAMEK, frames, PIERWSZA_RAMKA)
    for i in range (len(bits)-lenght):
        num = bits_to_int(bits[(i+start):(i+start+lenght)])
        if num % 2 == 0:
            num += 1

        prime = check_prime(num)
        if prime:
            return prime
        
def check_prime(num):
    if num < 10000:
        return False

    if num % 2 == 0:
        return False

    for i in range(3, int(math.sqrt(num)) + 1, 2):
        if num % i == 0:
            return False
    return num

def find_d(p,q,e, phi):
    k=1
    while (((k*phi)+1)%e!=0):
        k+=1
    d=int(((k*phi)+1)/e)
    return d

def rsa(p, q):
    n = p*q
    phi = (p-1)*(q-1)
    e=65537
    while e<phi:
        if(math.gcd(e,phi)==1):
            break
        e+=1
    d = find_d(p,q, e, phi)
    return (n, e), (n, d)

def make_key(a,b):
    a = generate_prime(16, a)
    b = generate_prime(16, b)
    p, q = rsa(a, b)
    return p, q

def sign(message, rana, ranb):
    private_key, public_key = make_key(rana, ranb)
    hash_obj = SHA256.new(message.encode('utf-8'))
    code = [pow(ord(char),private_key[1],private_key[0]) for char in hash_obj]
    signature = base64.b64encode(bytes(str(code),'ascii')).decode()
    return message, signature, public_key

def decrypt(message, signature, public_key):
    decoded = base64.b64decode(signature).decode()
    code = ast.literal_eval(decoded)
    hash_obj = SHA256.new(message.encode('utf-8'))
    try:
        text = [chr(pow(char, public_key[1], public_key[0])) for char in code]
    except Exception as e:
        print("Podpis nieważny")
        return 0

    decrypted=''.join(text)
    if (decrypted == hash_obj):
        print("Podpis ważny")
    else:
        print("Podpis nieważny")


wiadomosc = "wiadomosc"
message, signature, public_key = sign(wiadomosc, 7, 4007)
print("Podpis: ",signature)
decrypt(message, signature, public_key)

print("Inny klucz publiczny:")
p, q=make_key(2007,6007)
decrypt(message, signature, q)

print("Inna wiadomosc:")
decrypt("inna wiadomosc", signature, public_key)



