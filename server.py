import asyncio

# Словарь для хранения подключенных клиентов и их обработчиков
connected_clients = {}

# Функция для обработки подключения клиента
async def handle_client(reader, writer):
    # Получаем информацию о клиенте
    addr = writer.get_extra_info('peername')
    print(f"Client connected: {addr}")
    
    # Добавляем клиента в словарь подключенных клиентов
    connected_clients[addr] = writer
    
    try:
        while True:
            # Получаем данные от клиента
            data = await reader.read(1024)
            if not data:
                break
            
            # Отправляем данные другим подключенным клиентам
            for client_addr, client_writer in connected_clients.items():
                if client_addr != addr:  # Исключаем отправку себе
                    client_writer.write(data)
                    await client_writer.drain()
                    
    except asyncio.CancelledError:
        print(f"Connection with {addr} was cancelled")
    except Exception as e:
        print(f"Error occurred with {addr}: {e}")
    finally:
        # Удаляем клиента из словаря при отключении
        del connected_clients[addr]
        writer.close()
        await writer.wait_closed()
        print(f"Connection with {addr} closed")

async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 12345)
    addr = server.sockets[0].getsockname()
    print(f'Server started on {addr}')
    
    async with server:
        await server.serve_forever()

asyncio.run(main())
