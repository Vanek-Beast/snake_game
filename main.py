# Импортируем библиотеки
import pygame as pg
from random import choice
import json
import os
import sys


# Класс кнопки
class ImageButton:
    def __init__(self, x, y, width, height, text, img_path, hov_img_path=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.img = pg.image.load(img_path)
        self.img = pg.transform.scale(self.img, (width, height))
        self.hov_img = self.img
        if hov_img_path:
            self.hov_img = pg.image.load(hov_img_path)
            self.hov_img = pg.transform.scale(self.hov_img, (width, height))
        self.rect = self.img.get_rect(topleft=(x, y))
        self.is_hovered = False

    def draw(self, screen):
        current_img = self.hov_img if self.is_hovered else self.img
        screen.blit(current_img, self.rect.topleft)
        font = pg.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def set_pos_x(self, x):
        self.x = x
        self.rect = self.img.get_rect(topleft=(self.x, self.y))

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            pg.event.post(pg.event.Event(pg.USEREVENT, button=self))


if os.path.isfile("user.json"):
    user = json.load(open("user.json", "r"))
else:
    user = {
        "easy": {
            "high_score": 0,
            "games_played": 0,
            "total_score": 0,
            "average_score": 0,
            "game_results": []
        },
        "normal": {
            "high_score": 0,
            "games_played": 0,
            "total_score": 0,
            "average_score": 0,
            "game_results": []
        },
        "hard": {
            "high_score": 0,
            "games_played": 0,
            "total_score": 0,
            "average_score": 0,
            "game_results": []
        }
    }
# Основные переменные игры
width, height = 854, 480
tile_size = 30
range_x = (tile_size // 2, width - tile_size // 2, tile_size)
range_y = (tile_size // 2, height - tile_size // 2, tile_size)
lev = {1: "easy", 2: "normal", 3: "hard"}
pg.init()
screen = pg.display.set_mode([width, height])
pg.display.set_caption("Змейка")
clock = pg.time.Clock()
# Фон и шрифты
bg = pg.image.load("background.png")
font = pg.font.Font(None, 72)
font_small = pg.font.Font(None, 35)
font_smallest = pg.font.Font(None, 27)


# Функция для сохранения профиля
def save_profile():
    file_path = os.path.join(os.getcwd(), 'user.json')
    with open(file_path, 'w') as file:
        json.dump(user, file)


# Функция для обновления профиля
def update_profile(level, length):
    global user
    user[lev[level]]["high_score"] = max(user[lev[level]]["high_score"], length)
    user[lev[level]]["games_played"] += 1
    user[lev[level]]["total_score"] += length
    user[lev[level]]["average_score"] = round(user[lev[level]]["total_score"] / user[lev[level]]["games_played"])
    user[lev[level]]["game_results"].append(length)


# Функция для определения координат (X:Y) случайной позиции на игровом поле
def get_random_position(obstacles, blocks):
    possible_positions = [
        (x, y)
        for x in range(*range_x)
        for y in range(*range_y)
        if (x, y) not in [ob.center for ob in obstacles] and not has_adjacent_block((x, y), blocks)
    ]
    return choice(possible_positions) if possible_positions else None


# Функция для проверки наличия соседнего блока
def has_adjacent_block(pos, blocks):
    adjacent_positions = [
        (pos[0] - tile_size, pos[1] - tile_size),
        (pos[0] + tile_size, pos[1] + tile_size),
        (pos[0] + tile_size, pos[1] - tile_size),
        (pos[0] - tile_size, pos[1] + tile_size),
        (pos[0] - tile_size, pos[1]),
        (pos[0] + tile_size, pos[1]),
        (pos[0], pos[1] - tile_size),
        (pos[0], pos[1] + tile_size)
    ]
    for adj in adjacent_positions:
        if adj in [block.center for block in blocks]:
            return True
    return False


# Главный цикл игры
def game_loop(level):
    snake = pg.Rect(0, 0, tile_size - 2, tile_size - 2)
    snake.center = get_random_position([], [])
    food = pg.Rect(0, 0, tile_size - 2, tile_size - 2)
    food.center = get_random_position([snake], [])
    block = pg.Rect(0, 0, tile_size - 2, tile_size - 2)
    blocks = []
    blocks_count = 0
    snake_speed = 8
    if level == 2:
        blocks_count = 10
        snake_speed = 10
    elif level == 3:
        blocks_count = 20
        snake_speed = 12
    for i in range(blocks_count):
        block.center = get_random_position([snake, food] + blocks, blocks)
        if block.center:  # Проверка на None
            blocks.append(pg.Rect(block))
    snake_dir = (0, 0)
    length = 1
    segments = [pg.Rect(snake)]
    running = True
    while running:
        # Цикл обработки событий
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            # Обработка нажатий WASD
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w and snake_dir != (0, tile_size):
                    snake_dir = (0, -tile_size)
                if event.key == pg.K_s and snake_dir != (0, -tile_size):
                    snake_dir = (0, tile_size)
                if event.key == pg.K_a and snake_dir != (tile_size, 0):
                    snake_dir = (-tile_size, 0)
                if event.key == pg.K_d and snake_dir != (-tile_size, 0):
                    snake_dir = (tile_size, 0)
                if event.key == pg.K_ESCAPE:
                    if pause_menu():
                        running = False
        screen.fill((155, 188, 15))
        snake.move_ip(snake_dir)
        segments.append(pg.Rect(snake))
        segments = segments[-length:]
        [pg.draw.rect(screen, (120, 149, 12), segment) for segment in segments]
        # Рисуем еду
        pg.draw.rect(screen, (15, 56, 15), food)
        [pg.draw.rect(screen, (255, 255, 255), bl) for bl in blocks]
        # Поедание
        if snake.center == food.center:
            food_pos = get_random_position(segments + blocks, [])
            if food_pos:
                food.center = food_pos
                length += 1
            else:
                running = False
                update_profile(level, length)
                after_game_menu(length, 1)  # В случае выигрыша
        # Столкновение с границами и телом змейки
        snake_collision = pg.Rect.collidelist(snake, segments[:-1] + blocks) != -1
        if (snake.left < 0 or snake.right > screen.get_width() or
                snake.top < 0 or snake.bottom > screen.get_height() or snake_collision):
            update_profile(level, length)
            if after_game_menu(length):
                snake.center, food.center = get_random_position([], []), get_random_position([snake], [])
                length, snake_dir = 1, (0, 0)
                segments = [snake.copy()]
                blocks = []
                for i in range(blocks_count):
                    block.center = get_random_position([snake, food] + blocks, blocks)
                    if block.center:  # Проверка на None
                        blocks.append(pg.Rect(block))
            else:
                running = False
        pg.display.update()
        clock.tick(snake_speed)


# Функция для отрисовки пост-игрового меню
def after_game_menu(score, win=0):
    again_button = ImageButton(screen.get_width() / 2 - 252 / 2, 100, 252, 54, "Играть снова", "button.png",
                               "hovered_button.png")
    back_button = ImageButton(screen.get_width() / 2 - 252 / 2, 175, 252, 54, "К уровням", "button.png",
                              "hovered_button.png")
    buttons = (again_button, back_button)
    running = True
    while running:
        if win:
            text_surface = font.render(f'Победа!!! Количество очков - {score}', True, (255, 255, 255))
        else:
            text_surface = font.render(f'Количество очков - {score}', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen.get_width() / 2, 50))
        screen.blit(bg, (0, 0))
        screen.blit(text_surface, text_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.USEREVENT:
                if event.button == again_button:
                    return True
                elif event.button == back_button:
                    return False
            for button in buttons:
                button.set_pos_x(screen.get_width() / 2 - 252 / 2)
                button.handle_event(event)
        for button in buttons:
            button.check_hover(pg.mouse.get_pos())
            button.draw(screen)
        pg.display.flip()


# Функция для отрисовки главного меню
def main_menu():
    # Задание кнопок
    start_button = ImageButton(screen.get_width() / 2 - 252 / 2, 100, 252, 54, "Новая игра", "button.png",
                               "hovered_button.png")
    settings_button = ImageButton(screen.get_width() / 2 - 252 / 2, 175, 252, 54, "Настройки", "button.png",
                                  "hovered_button.png")
    records_button = ImageButton(screen.get_width() / 2 - 252 / 2, 250, 252, 54, "Рекорды", "button.png",
                                 "hovered_button.png")
    rules_button = ImageButton(screen.get_width() / 2 - 252 / 2, 325, 252, 54, "Правила", "button.png",
                               "hovered_button.png")
    exit_button = ImageButton(screen.get_width() / 2 - 252 / 2, 400, 252, 54, "Выход", "button.png",
                              "hovered_button.png")
    buttons = (start_button, settings_button, records_button, rules_button, exit_button)
    running = True
    while running:
        text_surface = font.render('Игра "Змейка"', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen.get_width() / 2, 50))
        screen.blit(bg, (0, 0))
        screen.blit(text_surface, text_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.USEREVENT:
                if event.button == settings_button:
                    settings_menu()
                elif event.button == start_button:
                    levels_menu()
                elif event.button == records_button:
                    records_menu()
                elif event.button == rules_button:
                    rules_menu()
                elif event.button == exit_button:
                    save_profile()
                    running = False
                    pg.quit()
                    sys.exit()
            for button in buttons:
                button.set_pos_x(screen.get_width() / 2 - 252 / 2)
                button.handle_event(event)
        for button in buttons:
            button.check_hover(pg.mouse.get_pos())
            button.draw(screen)
        pg.display.flip()


# Функция для отрисовки меню настроек
def settings_menu():
    profile_button = ImageButton(screen.get_width() / 2 - 252 / 2, 100, 252, 54, "Профиль", "button.png",
                                 "hovered_button.png")
    graphics_button = ImageButton(screen.get_width() / 2 - 252 / 2, 175, 252, 54, "Разрешение", "button.png",
                                  "hovered_button.png")
    back_button = ImageButton(screen.get_width() / 2 - 252 / 2, 250, 252, 54, "Назад", "button.png",
                              "hovered_button.png")
    buttons = (profile_button, graphics_button, back_button)
    running = True
    while running:
        text_surface = font.render('Настройки', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen.get_width() / 2, 50))
        screen.blit(bg, (0, 0))
        screen.blit(text_surface, text_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.USEREVENT:
                if event.button == profile_button:
                    profile_menu()
                elif event.button == graphics_button:
                    graphics_menu()
                elif event.button == back_button:
                    running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
            for button in buttons:
                button.set_pos_x(screen.get_width() / 2 - 252 / 2)
                button.handle_event(event)
        for button in buttons:
            button.check_hover(pg.mouse.get_pos())
            button.draw(screen)
        pg.display.flip()


# Функция для отрисовки меню графики
def graphics_menu():
    gr1_button = ImageButton(screen.get_width() / 2 - 252 / 2, 100, 252, 54, "854x480", "button.png",
                             "hovered_button.png")
    gr2_button = ImageButton(screen.get_width() / 2 - 252 / 2, 175, 252, 54, "1280x720", "button.png",
                             "hovered_button.png")
    gr3_button = ImageButton(screen.get_width() / 2 - 252 / 2, 250, 252, 54, "Full HD", "button.png",
                             "hovered_button.png")
    back_button = ImageButton(screen.get_width() / 2 - 252 / 2, 325, 252, 54, "Назад", "button.png",
                              "hovered_button.png")
    buttons = (gr1_button, gr2_button, gr3_button, back_button)
    running = True
    while running:
        text_surface = font.render('Настройки графики', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen.get_width() / 2, 50))
        screen.blit(bg, (0, 0))
        screen.blit(text_surface, text_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.USEREVENT:
                if event.button == gr1_button:
                    change_video_mode(854, 480)
                elif event.button == gr2_button:
                    change_video_mode(1280, 720)
                elif event.button == gr3_button:
                    change_video_mode(1920, 1080, pg.FULLSCREEN)
                elif event.button == back_button:
                    running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
            for button in buttons:
                button.set_pos_x(screen.get_width() / 2 - 252 / 2)
                button.handle_event(event)
        for button in buttons:
            button.check_hover(pg.mouse.get_pos())
            button.draw(screen)
        pg.display.flip()


# Функция для отрисовки правил
def rules_menu():
    back_button = ImageButton(screen.get_width() / 2 - 252 / 2, 250, 252, 54, "Назад", "button.png",
                              "hovered_button.png")
    running = True
    while running:
        title_surface = font.render('Правила', True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen.get_width() / 2, 50))
        rules = ["Используйте клавиши WASD, чтобы менять направление движения",
                 "Ешьте, чтобы расти",
                 "Избегайте столкновений с границами, препятствиями и самим собой"]
        screen.blit(bg, (0, 0))
        screen.blit(title_surface, title_rect)
        for i, r in enumerate(rules):
            r_surface = font_small.render(r, True, (255, 255, 255))
            r_rect = r_surface.get_rect(center=(screen.get_width() / 2, 100 + 50 * i))
            screen.blit(r_surface, r_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.USEREVENT:
                if event.button == back_button:
                    running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
            back_button.set_pos_x(screen.get_width() / 2 - 252 / 2)
            back_button.handle_event(event)
        back_button.check_hover(pg.mouse.get_pos())
        back_button.draw(screen)
        pg.display.flip()


# Функция для отрисовки профиля
def profile_menu():
    back_button = ImageButton(screen.get_width() / 2 - 252 / 2, 410, 252, 54, "Назад", "button.png",
                              "hovered_button.png")
    running = True

    while running:
        screen.blit(bg, (0, 0))  # Заполняем экран фоном
        title_surface = font.render('Личная статистика', True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen.get_width() / 2, 30))
        text = ["Легкий уровень", "Средний уровень", "Сложный уровень"]
        screen.blit(title_surface, title_rect)

        for i, r in enumerate(text):
            r_surface = pg.font.Font(None, 40).render(r, True, (255, 255, 255))
            r_rect = r_surface.get_rect(center=(screen.get_width() / 2, 75 + 115 * i))

            r1_surface = font_smallest.render(f"Максимальный результат: {user[lev[i + 1]]['high_score']}", True,
                                              (255, 255, 255))
            r1_rect = r1_surface.get_rect(center=(screen.get_width() / 2, 100 + 115 * i))

            r2_surface = font_smallest.render(f"Всего игр: {user[lev[i + 1]]['games_played']}", True, (255, 255, 255))
            r2_rect = r2_surface.get_rect(center=(screen.get_width() / 2, 120 + 115 * i))

            r3_surface = font_smallest.render(f"Средний результат: {user[lev[i + 1]]['average_score']}", True,
                                              (255, 255, 255))
            r3_rect = r3_surface.get_rect(center=(screen.get_width() / 2, 140 + 115 * i))

            screen.blit(r_surface, r_rect)
            screen.blit(r1_surface, r1_rect)
            screen.blit(r2_surface, r2_rect)
            screen.blit(r3_surface, r3_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.USEREVENT:
                if event.button == back_button:
                    running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

            back_button.set_pos_x(screen.get_width() / 2 - 252 / 2)
            back_button.handle_event(event)

        back_button.check_hover(pg.mouse.get_pos())
        back_button.draw(screen)
        pg.display.flip()


# Функция для отрисовки рекордов
def records_menu():
    back_button = ImageButton(screen.get_width() / 2 - 252 / 2, 410, 252, 54, "Назад", "button.png",
                              "hovered_button.png")
    running = True
    while running:
        title_surface = font.render('Лучшие результаты', True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen.get_width() / 2, 30))
        text = ["Легкий уровень",
                "Средний уровень",
                "Сложный уровень"]
        screen.blit(bg, (0, 0))
        screen.blit(title_surface, title_rect)
        for i, r in enumerate(text):
            r_surface = font_small.render(r, True, (255, 255, 255))
            r_rect = r_surface.get_rect(center=(screen.get_width() / 2, 75 + 115 * i))
            screen.blit(r_surface, r_rect)
            for j, t in enumerate(sorted(user[lev[i + 1]]["game_results"], reverse=True)):
                if j < 3:
                    t_surface = font_smallest.render(f"{j + 1}#------{t}", True, (255, 255, 255))
                    t_rect = t_surface.get_rect(center=(screen.get_width() / 2, 100 + 115 * i + 30 * j))
                    screen.blit(t_surface, t_rect)
                else:
                    break
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.USEREVENT:
                if event.button == back_button:
                    running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
            back_button.set_pos_x(screen.get_width() / 2 - 252 / 2)
            back_button.handle_event(event)
        back_button.check_hover(pg.mouse.get_pos())
        back_button.draw(screen)
        pg.display.flip()


# Функция для отрисовки меню паузы
def pause_menu():
    continue_button = ImageButton(screen.get_width() / 2 - 252 / 2, 175, 252, 54, "Продолжить", "button.png",
                                  "hovered_button.png")
    exit_button = ImageButton(screen.get_width() / 2 - 252 / 2, 250, 252, 54, "К уровням", "button.png",
                              "hovered_button.png")
    buttons = (continue_button, exit_button)
    running = True
    while running:
        text_surface = font.render('Пауза', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen.get_width() / 2, 50))
        screen.blit(bg, (0, 0))
        screen.blit(text_surface, text_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.USEREVENT:
                if event.button == continue_button:
                    running = False
                elif event.button == exit_button:
                    return True
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
            for button in buttons:
                button.set_pos_x(screen.get_width() / 2 - 252 / 2)
                button.handle_event(event)
        for button in buttons:
            button.check_hover(pg.mouse.get_pos())
            button.draw(screen)
        pg.display.flip()
    return False


# Функция для отрисовки меню выбора сложности
def levels_menu():
    easy_button = ImageButton(screen.get_width() / 2 - 252 / 2, 100, 252, 54, "Легкий", "button.png",
                              "hovered_button.png")
    normal_button = ImageButton(screen.get_width() / 2 - 252 / 2, 175, 252, 54, "Средний", "button.png",
                                "hovered_button.png")
    hard_button = ImageButton(screen.get_width() / 2 - 252 / 2, 250, 252, 54, "Сложный", "button.png",
                              "hovered_button.png")
    back_button = ImageButton(screen.get_width() / 2 - 252 / 2, 325, 252, 54, "Назад", "button.png",
                              "hovered_button.png")
    buttons = (easy_button, normal_button, hard_button, back_button)
    running = True
    while running:
        text_surface = font.render('Выберите сложность уровня', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen.get_width() / 2, 50))
        screen.blit(bg, (0, 0))
        screen.blit(text_surface, text_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_profile()
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.USEREVENT:
                if event.button == easy_button:
                    game_loop(1)
                elif event.button == normal_button:
                    game_loop(2)
                elif event.button == hard_button:
                    game_loop(3)
                elif event.button == back_button:
                    running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
            for button in buttons:
                button.set_pos_x(screen.get_width() / 2 - 252 / 2)
                button.handle_event(event)
        for button in buttons:
            button.check_hover(pg.mouse.get_pos())
            button.draw(screen)
        pg.display.flip()


# Функция для изменения настроек игры
def change_video_mode(w, h, full_screen=0):
    global width, height, screen, tile_size, range_x, range_y
    width, height = w, h
    screen = pg.display.set_mode((width, height), full_screen)
    if w == 854:
        tile_size = 30
    elif w == 1280:
        tile_size = 45
    elif w == 1920:
        tile_size = round(67.5 * screen.get_width() / width)
    range_x = (tile_size // 2, screen.get_width() - tile_size // 2, tile_size)
    range_y = (tile_size // 2, screen.get_height() - tile_size // 2, tile_size)


if __name__ == "__main__":
    main_menu()
