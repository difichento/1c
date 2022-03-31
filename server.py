import socket
from random import randint
import threading
import json


def load_words():
    words = []
    with open("words.txt", "r") as words_file:
        for word in words_file:
            words.append(word[:-1])
    return words


words = load_words()
alphabet = list('абвгдежзийклмнопрстуфхцчшщъыьэюя')


def convert_to_dict(word):
    '''
    Превращает слово в dict, где:
    ключ - буква
    значение - list позиций, на которых она стоит

    (нужно, чтобы быстро заменять * на буквы)
    '''
    word = word.lower()
    word_dict = {}
    for num, letter in enumerate(word):
        if letter in word_dict.keys():
            word_dict[letter].append(num)
        else:
            word_dict[letter] = [num]
    return word_dict


def game(client_socket, client_addr):
    """
    Функция игры. Обмен данными происходит в ней
    """
    # загадываем слово
    word_str = words[randint(0, len(words) - 1)]
    word = convert_to_dict(word_str)

    client_answer = ["*"] * len(word_str)
    tries_num = len(word_str) * 2
    used_letters = []

    # начало
    client_socket.send(
        f"\nПОЛЕ ЧУДЕС.\nВам загаданно слово из {len(word_str)} букв.\nУ вас {tries_num} попыток, чтобы отгадать его.\n\
{''.join(client_answer)}\nПишите по одной букве (е=ё). Также можно написать все слово разом (стоит 1 попытку)\
\nЧтобы завршить игру введите ':q'\n".encode())

    # флаг чтобы начать заново
    client_win = False
    while True:
        # получаем букву
        letter = client_socket.recv(1024).decode("utf-8").lower()
        if not letter:
            return False
        if letter == ':q':
            return False
        if letter == 'ё':
            letter = 'е'

        print(f"{client_addr}: send- {letter}")

        # проверка на угаданное слов
        if letter == word_str:
            client_win = True
            break

        # обработка неправильного ввода
        if len(letter) == 0:
            continue
        elif len(letter) > 1:
            client_socket.send("Нужно отправить одну букву".encode())
            continue
        elif letter not in alphabet:
            client_socket.send("Нужно отправлять русскую букву в любом регистре".encode())
            continue
        elif letter in used_letters:
            client_socket.send("Эта буква уже была".encode())
            continue

        tries_num -= 1
        used_letters.append(letter)
        if letter in word.keys():
            for ind in word[letter]:
                client_answer[ind] = letter

            # проверка на победу
            if ''.join(client_answer) == word_str:
                client_win = True
                break

            # строка, создающаяся в процессе обработки буквы
            # потом объединяется со строкой, которая выводится всегда
            process_str = f"Вы угадали {len(word[letter])} букв{'у' if len(word[letter]) == 1 else 'ы'}\n"
        else:
            process_str = "Не угадали\n"

        # проверка на проигрыш
        if tries_num == 0:
            client_win = False
            break
        # строка, которая выводится в любом случае
        const_str = f"Попыток осталось: {tries_num}\nТекущее слово: {''.join(client_answer)}"
        client_socket.send(
            (process_str + const_str).encode())

    client_socket.send(
        f"{f'Поздравляю, вы угадали слово - {word_str}.' if client_win else f'Вы проиграли. Загаданное слово - {word_str}.'}\
            \nЧтобы продолжить введите 'да'".encode())

    # в main игра запускается, пока continue_flag = True
    continue_flag = client_socket.recv(1024).decode("utf-8") == 'да'
    return continue_flag


def start_game(client_socket, client_addr):
    while game(client_socket, client_addr):
        pass

    # посылаем b'0' как обозначение завершения для клиента
    client_socket.send(b'0')
    print("Closed connection with", client_addr)
    client_socket.close()


def load_cfg():
    """
    Загружает порт, ip, и максимальное количество клиентов из конфиг файла
    """
    try:
        cfg = open("config", "r")
        cfg = json.load(cfg)
    except:
        print("Вы сломали конфиг")
        return -1
    return cfg


def main():
    # создаем сокет
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    cfg = load_cfg()
    try:
        serv_sock.bind((cfg["host"], cfg["port"]))
    except OSError:
        print("Попробуйте изменить порт в config")
        exit(1)
    serv_sock.listen(cfg["max_users"])

    while True:
        # обрабатываем входящие подключения
        client_sock, client_addr = serv_sock.accept()
        print('Connected by', client_addr)

        # на каждого клиента выделяем поток
        new_thread = threading.Thread(target=start_game, args=(client_sock, client_addr,))
        new_thread.start()
        print("Made new thread:", new_thread.name)


if __name__ == '__main__':
    main()
