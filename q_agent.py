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
        # self.q_table = np.zeros((x_space, y_space, action_space))

        # Если вы уже обучили агента, можете подгрузить данные из файла
        with open("brain.json", "r") as file:
            self.q_table = np.array(json.loads(file.read())["data"])

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