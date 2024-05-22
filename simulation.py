import socket
import pygame
import random

# Инициализация Pygame
pygame.init()

# Установка размеров экрана
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Simulation")

# Загрузка изображения машины и изменение его размера
car_img = pygame.image.load("car.png")
car_img = pygame.transform.scale(car_img, (300, 150))  # Изменяем размер до 300x150

# Загрузка изображения фона
background_img = pygame.image.load("background_road.jpg")
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH * 2, SCREEN_HEIGHT))  # Увеличиваем ширину фона в 2 раза

# Создание сокета для получения рекомендованной скорости
def connect_to_server():
    server_address = ('localhost', 12345)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(server_address)
    return server_socket

def get_recommended_speed(server_socket):
    try:
        received_data = server_socket.recv(1024).decode()
        if received_data:
            recommended_speed = int(received_data)
            print("Received recommended speed:", recommended_speed)
            return recommended_speed
        else:
            return None
    except Exception as e:
        print("Error occurred while receiving recommended speed:", e)
        return None

# Функция для отрисовки машины на экране с учетом позиции экрана
def draw_car(x, y):
    screen.blit(car_img, (x, y))

# Функция для отрисовки фона на экране
def draw_background(bg_x):
    screen.blit(background_img, (bg_x, 0))  # Отображаем фон на заднем плане

# Функция для создания кнопки выхода
def draw_exit_button():
    font = pygame.font.Font(None, 36)
    text = font.render("Exit", True, (255, 255, 255))
    button_rect = pygame.Rect(SCREEN_WIDTH - 110, 10, 100, 40)
    pygame.draw.rect(screen, (255, 0, 0), button_rect)
    screen.blit(text, (SCREEN_WIDTH - 100, 15))
    return button_rect

# Основной игровой цикл
def main():
    clock = pygame.time.Clock()
    car_x, car_y = SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 160  # Начальная позиция машины (ближе к низу экрана)
    car_speed = 0  # Скорость машины
    bg_x = 0  # Начальная позиция фона
    total_distance = 0  # Общее пройденное расстояние
    recommended_speed = 20  # Начальная рекомендуемая скорость

    # Подключение к серверу
    server_socket = connect_to_server()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if exit_button.collidepoint(mouse_pos):
                    running = False

        # Получение рекомендованной скорости с сервера
        try:
            new_recommended_speed = get_recommended_speed(server_socket)
            if new_recommended_speed is not None:
                recommended_speed = new_recommended_speed
        except:
            pass

        if car_speed < recommended_speed:
            car_speed += 2  # Увеличиваем скорость разгона
        elif car_speed > recommended_speed:
            car_speed -= 5

        # Перемещение фона влево с корректной скоростью (1 км/ч = 0.27778 м/с)
        bg_x -= car_speed * 0.4 / 60 * 10  # Преобразуем скорость из км/ч в пиксели/кадр
        if bg_x <= -SCREEN_WIDTH:
            bg_x = 0

        # Обновление позиции машины по оси X в зависимости от скорости
        car_x = SCREEN_WIDTH // 2 - 350 + (car_speed * 2)  # Увеличиваем изменение позиции по оси X

        # Отклонение по оси Y
        car_y += random.randint(-1, 1) * random.randint(0, 10)

        # Ограничиваем отклонение по оси Y
        if car_y < SCREEN_HEIGHT - 200:
            car_y = SCREEN_HEIGHT - 200
        elif car_y > SCREEN_HEIGHT - 120:
            car_y = SCREEN_HEIGHT - 120

        # Отрисовка фона и машины
        draw_background(bg_x)
        draw_background(bg_x + SCREEN_WIDTH)  # Отрисовываем второй фон для бесшовного эффекта
        draw_car(car_x, car_y)

        # Обновление общего пройденного расстояния
        total_distance += car_speed * 0.27778 / 60  # car_speed в км/ч преобразуем в метры/секунду и умножаем на время кадра

        # Отображение текущей скорости сверху экрана
        font = pygame.font.Font(None, 36)
        text = font.render(f"Current Speed: {int(car_speed)} km/h, Recommended Speed: {int(recommended_speed)} km/h.", True, (0, 0, 0))
        screen.blit(text, (10, 10))

        # Вывод статистики
        distance_text = font.render(f"Total Distance: {int(total_distance)} m", True, (0, 0, 0))
        screen.blit(distance_text, (10, 50))

        # Отрисовка кнопки выхода
        exit_button = draw_exit_button()

        pygame.display.flip()
        clock.tick(60)  # Ограничение FPS

    pygame.quit()

if __name__ == "__main__":
    main()