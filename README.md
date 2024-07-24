# Q Агент учится проходить лабиринт
## Разработчики
 - [Московский Артемий](https://github.com/artemijMoskowsky)

## Коротко о проекте

Проект был написан для лучшего понимания что такое q агенты и как с ними работать, в проекте есть комментарии для рассмотрения работы агента

## Использованные библиотеки
- numpy - для массивов нейросети
- random - для обучения нейросети
- pygame - для визуального отображения

## Модули проекта
### game.py
Модуль в котором прописана основная часть игры, классы блока, персонажа, основной цикл игры, импортированы все остальные модули. А так же этот модуль является главным для запуска.
```python
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
```





### py_mapper.py
Модуль в котором подгружается карта из картинки, он сделан для того чтобы можно было удобно создавать карту
```python
import cv2
import numpy as np

def load_map(map_size: tuple, file_name):
    image = cv2.imread(file_name)
    map_pixels = image.reshape(-1, 3).tolist()
    py_map = []
    index = 0
    for i in range(map_size[1]):
        py_map.append([])
        for j in range(map_size[0]):
            py_map[i].append(map_pixels[index])
            index += 1
    return py_map
```


### q_agent.py
Модуль в котором прописан класс q агента, все его свойства и методы.
```python
import numpy as np
import random
import json

# Создаём класса агента
class Agent:
    def __init__(self, x_space, y_space, action_space):
        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 0.1
        # Задаём размерность состояний х
        self.x_space = x_space
        # Задаём размерность состояний у
        self.y_space = y_space
        # Задаём размерность действий
        self.action_space = action_space

        # Создаём пустую таблицу
        self.q_table = np.zeros((x_space, y_space, action_space))

        # Если вы уже обучили агента, можете подгрузить данные из файла
        # with open("brain.json", "r") as file:
        #     self.q_table = np.array(json.loads(file.read())["data"])

        # ВАЖНО! Если вы обучили нейросеть, то поставьте epsilon на 0

    # Создаём метод выбора действия
    def choose_action(self, x, y):
        # Используем "жадное обучение", если выпадит число меньше чем epsilon, то вместо выбора действия из таблицы, выпадает случайное действие
        if np.random.rand() < self.epsilon:
            # Возвращаем случайное действие
            return random.randint(0, self.action_space-1)
        # Если "жадное обучение" не произошло, то выбираем из таблицы
        else:
            # Возвращаем индекс максимального значения из таблицы
            return np.argmax(self.q_table[round(x), round(y)])
    # Обновляем таблицу опираясь на состояние х, состояние у, награду, действие, состояние х после действия, состояние у после действия
    def update_table(self, x, y, reward, action, next_x, next_y):
        # Обновляем таблицу используя модифицированное уравнение Беллмана
        self.q_table[round(x), round(y), action] = (1 - self.alpha) * self.q_table[round(x), round(y), action] + self.alpha * (reward + self.gamma * np.max(self.q_table[round(next_x), round(next_y)]))
```
## Примечания
В проект прикреплены данные после моего обучения, они сохранены как brain.json. Желательно этот файл удалить, это поможет вам отследить что ваш агент выполнил цель (после того как он проходит лабиринт этот файл создастся если его не было ранее). Так же, когда ваш агент достаточно обучился, вы можете выключить программу и зайти в файл q_agent.py и изменить следующий код:

<br>
Было:
```python
   def __init__(self, x_space, y_space, action_space):
        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 0.1
        # Задаём размерность состояний х
        self.x_space = x_space
        # Задаём размерность состояний у
        self.y_space = y_space
        # Задаём размерность действий
        self.action_space = action_space

        # Создаём пустую таблицу
        self.q_table = np.zeros((x_space, y_space, action_space))

        # Если вы уже обучили агента, можете подгрузить данные из файла
        # with open("brain.json", "r") as file:
        #     self.q_table = np.array(json.loads(file.read())["data"])

        # ВАЖНО! Если вы обучили нейросеть, то поставьте epsilon на 0
```

<br>
Стало
```python
    def __init__(self, x_space, y_space, action_space):
        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 0.0
        # Задаём размерность состояний х
        self.x_space = x_space
        # Задаём размерность состояний у
        self.y_space = y_space
        # Задаём размерность действий
        self.action_space = action_space

        # Создаём пустую таблицу
        # self.q_table = np.zeros((x_space, y_space, action_space))

        # Если вы уже обучили агента, можете подгрузить данные из файла
        with open("brain.json", "r") as file:
            self.q_table = np.array(json.loads(file.read())["data"])

        # ВАЖНО! Если вы обучили нейросеть, то поставьте epsilon на 0
```
