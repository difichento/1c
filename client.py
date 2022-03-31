import socket


def prepare():
    host = input("Введите ip и порт сервера через enter (если точно их не знаете - введите q.)\n")
    if host == "q":
        return ('0.0.0.0', 7080)
    port = input()
    return host, port


def main(host, port):
    """
    Сервер сделан так, что клиент просто по кругу посылает и получает данные
    """
    # создание сокета
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((host, port))

    while True:
        # получаем данные
        server_message = client_sock.recv(1024)

        # "сигнал" завершения
        if server_message == b'0':
            client_sock.close()
            break

        server_message = server_message.decode()
        print(server_message)

        # клиент отправляет данные
        client_input = input()
        while len(client_input) == 0:
            client_input = input()
            print()
        try:
            client_sock.send(client_input.encode())
        except BrokenPipeError:
            print("Проблемы с соединением")
            client_sock.close()
            break


if __name__ == '__main__':
    # pr = prepare()
    # main(pr[0], pr[1])
    # не уверен что это нужно, поэтому просто оставляю возможность запуститься так
    main('0.0.0.0', 7080)
