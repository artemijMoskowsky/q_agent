import pygame
from py_mapper import load_map
import q_agent as q
import json
import numpy as np

pygame.init()

window = pygame.display.set_mode((500,500))

# Общая награда, за все жизни
total_reward = -100000000000

class Block:
    def __init__(self, x, y, width, height, finish):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.finish = finish
        self.rect = pygame.Rect(x, y, width, height)
    def render(self, window):
        if self.finish:
            pygame.draw.rect(window, (0,255,0), self.rect)
        else:
            pygame.draw.rect(window, (255,255,255), self.rect)

# Создаём класс игрока
class Player:
    def __init__(self, x, y, width, height, speed):
        # Задаём координаты игрока
        self.x = x
        self.y = y
        # Сохраняем копию начальных координат
        self.sx = x
        self.sy = y
        # Задаём ширину игрока
        self.width = width
        # Задаём высоту игрока
        self.height = height
        # Задаём скорость игрока
        self.speed = speed
        # Создаём квадрат для отрисовки местоположения игрока
        self.rect = pygame.Rect(x, y, width, height)
        # Указываем начальное действие
        self.action = 3
        # Указываем мёртв игрок или нет
        self.dead = False
        # Создаём список координат на которых побывал игрок
        self.cords = [(x, y)]
        # Создаём агента
        self.agent = q.Agent(20, 20, 4)
        # Создаём переменную для общей награды которую игрок получит за 1 жизнь
        self.total_reward = 0
    # Создаём метод передвижения
    def move(self, blocks):
        

        # Получение действия которое выбирает агент
        self.action = self.agent.choose_action(self.x/25, self.y/25)

        # Ручное управление (отключено) -----

        # if keys[pygame.K_w]:
        #     self.action = 0
        # elif keys[pygame.K_s]:
        #     self.action = 1
        # elif keys[pygame.K_a]:
        #     self.action = 2
        # elif keys[pygame.K_d]:
        #     self.action = 3

        # -----------------------------------

        # Задаём награду за ход (-1 для того чтобы агент пытался усовершенствовать маршрут)
        reward = -1

        # Действие вверх
        if self.action == 0:
            self.y -= self.speed
        # Действие вниз
        elif self.action == 1:
            self.y += self.speed
        # Действие влево
        elif self.action == 2:
            self.x -= self.speed
        # Действие вправо
        elif self.action == 3:
            self.x += self.speed

        # Если игрок не был на этих координатах, обновляем награду на 1 (это сделано чтобы агент более усердно изучал карту)
        if not (self.x, self.y) in self.cords:
            reward = 1
            # Запоминаем координаты
            self.cords.append((self.x, self.y))

        # Перебираем список блоков
        for block in blocks:
            # Если игрок вошел в блок
            if block.x == self.x and block.y == self.y:
                # Если блок не является финишем, а обычной стеной
                if block.finish == False:
                    # Игрок умирает
                    self.dead = True
                    # Награда за действие -400
                    reward = -400
                # Если блок является финишем
                else:
                    # Награда за действие 100
                    reward = 100
                    # Игрок умирает
                    self.dead = True
            # Отрисовка блоки
            block.render(window)

        # Обновляем общую награду игрока
        self.total_reward += reward

        # Обновляем данные агента в зависимости от состояния (х, у), награды, действия и состояния после выбора действия (х, у)
        self.agent.update_table(self.rect.x/25, self.rect.y/25, reward, self.action, self.x/25, self.y/25)

        # Обновляем координаты квадрата
        self.rect.x = self.x
        self.rect.y = self.y
    
    # Создаём метод отрисовки
    def render(self, window):
        pygame.draw.rect(window, (0,0,255), self.rect)

    # Создаём метод обновления всех параметров, кроме агента
    def update(self):
        self.x = self.sx
        self.y = self.sy
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.action = 3
        self.dead = False
        self.total_reward = 0

# Загружаем карту из png
py_map = load_map((20,20), "py_map.png")

blocks = []

for idy, row in enumerate(py_map):
    for idx, column in enumerate(row):
        if column == [255,255,255]:
            blocks.append(Block(idx*25,idy*25,25,25,False))
        elif column == [0,255,0]:
            blocks.append(Block(idx*25,idy*25,25,25,True))

game_running = True

# Создаём игрока
player = Player(25,25,25,25,25)

# Сохраняем таблицу агента, до того как он изменил ёё при передвижении
last_table = np.copy(player.agent.q_table)

tick = 10

clock = pygame.time.Clock()
while game_running:
    clock.tick(tick)
    window.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        

    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        tick = 100
    elif keys[pygame.K_DOWN]:
        tick = 10

    # Сохраняем таблицу агента, до того как он изменил ёё при передвижении
    table = np.copy(player.agent.q_table)

    player.move(blocks)
    if player.dead:
        if total_reward > player.total_reward:
            # Возвращаем старые значения таблицы
            player.agent.q_table = np.copy(last_table)
        else:
            # Сохраняем таблицу агента, до того как он изменил ёё при передвижении
            last_table = np.copy(player.agent.q_table)
            # Сохраняем значения таблицы
            with open("brain.json", "w") as file:
                file.write(json.dumps({"data": table.tolist()}, indent=2))
        player.update()
    player.render(window)

    pygame.display.flip()    