from random import randint
from abc import abstractmethod

import pygame

# Состояние игры (нахождение в меню или в игре)
MENU = False
GAME = True
STATE = MENU

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 6

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс игрового объекта.

    Attributes:
        body_color (tuple): Цвет объекта.
        position (tuple): Позиция на игровом поле.
    """

    def __init__(self,
                 body_color=(255, 255, 255),
                 position=(GRID_WIDTH // 2 * GRID_SIZE,
                           GRID_HEIGHT // 2 * GRID_SIZE
                           )
                 ):
        self.position = position
        self.body_color = body_color

    @abstractmethod
    def draw(self):
        pass


class Apple(GameObject):
    """Класс Яблока, унаследованный от GameObject.

    Attributes:
        body_color (tuple): Цвет объекта.
        position (tuple): Позиция на игровом поле.
    """

    def __init__(self, body_color=(255, 0, 0)):
        super().__init__(body_color=body_color)

    def randomize_position(self):
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self):
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Money(Apple):
    """Класс Монеток, унаследованный от Apple.

    Attributes:
        body_color (tuple): Цвет объекта.
        position (tuple): Позиция на игровом поле.
        quantity (int): Количество собранных монеток.
    """

    def __init__(self, body_color=(255, 255, 0)):
        super().__init__(body_color=body_color)
        self.quantity = 0

    def draw_quantity(self, text_color=(255, 255, 0)):
        font = pygame.font.Font(size=36)
        text = font.render(str(self.quantity), False, text_color)
        text_rect = text.get_rect(center=(20, 20))
        screen.blit(text, text_rect)


class Snake(GameObject):
    """Класс Змейки, унаследованный от GameObject.

    Attributes:
        body_color (tuple): Цвет объекта.
        position (tuple): Стартовая позиция на игровом поле.
        positions (list(tuple)): Содержит позиции всех сегментов змейки.
        length (int): Длина змейки.
        direction (tuple): Текущее направление змейки.
        next_direction (tuple): Следующее направление змейки.
        eaten_apple (bool): Флаг для обозначения, съедено ли яблоко.
        __last (tuple): Хвост змейки. Последний элемент positions.
    """

    def __init__(self,
                 length=1,
                 direction=RIGHT,
                 next_direction=None,
                 body_color=(0, 255, 0)
                 ):
        super().__init__(body_color=body_color)
        self.positions = [self.position]
        self.length = length
        self.direction = direction
        self.next_direction = next_direction
        self.eaten_apple = False
        self.__last = None

    def update_direction(self):
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        next_position_x, next_position_y = self.get_head_position()

        if self.direction == RIGHT:
            next_position_x += GRID_SIZE
        elif self.direction == LEFT:
            next_position_x -= GRID_SIZE
        elif self.direction == UP:
            next_position_y -= GRID_SIZE
        elif self.direction == DOWN:
            next_position_y += GRID_SIZE

        self.positions.insert(0, (next_position_x, next_position_y))

        self.__last = self.positions[-1]

        if len(self.positions) - self.length == 1 and not self.eaten_apple:
            self.positions.pop()

        self.eaten_apple = False

    def draw(self):
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.__last:
            last_rect = pygame.Rect(self.__last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        return self.positions[0]

    def reset(self):
        screen.fill(BOARD_BACKGROUND_COLOR)

        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.eaten_apple = False
        self.__last = None


class Button:
    """Класс кнопки.

    Attributes:
        rect (pygame.Rect): Прямоугольник, задающий размер и положение кнопки.
        font (pygame.font.Font): Шрифт текста кнопки.
        action (func): При нажатии происходит действие action.
        background_color (tuple): Цвет фона кнопки.
        text (str): Текст, отображаемый на кнопке.
        text_color (tuple): Цвет текста кнопки.
    """

    def __init__(self,
                 rect,
                 font,
                 action=STATE,
                 background_color=(255, 255, 255),
                 text='Start',
                 text_color=(0, 0, 0),
                 ):
        self.rect = rect
        self.background_color = background_color
        self.text = text
        self.font = font
        self.text_color = text_color
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.background_color, self.rect)
        text = self.font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


def handle_keys(game_object, button):
    """Keylogger для кнопки и змейки."""
    global STATE
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button.rect.collidepoint(event.pos):
                STATE = GAME
                game_object.reset()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    pygame.init()
    snake = Snake()
    apple = Apple()
    money = Money()

    money.randomize_position()
    apple.randomize_position()
    start_button = Button(rect=pygame.Rect((GRID_WIDTH // 2 * GRID_SIZE - 100,
                                            GRID_HEIGHT // 2 * GRID_SIZE - 50
                                            ),
                                           (200, 100)
                                           ),
                          font=pygame.font.Font(None, size=36),
                          )

    while True:
        clock.tick(SPEED)
        handle_keys(snake, start_button)
        if STATE == MENU:
            start_button.draw()
            pygame.display.update()
        elif STATE == GAME:
            snake.update_direction()
            snake.draw()
            snake.move()
            apple.draw()
            money.draw()
            money.draw_quantity()
            pygame.display.update()

            # Змейка съедает яблоко
            if snake.get_head_position() == apple.position:
                apple.randomize_position()
                snake.eaten_apple = True
                snake.length += 1

            # Змейка собирает монетку.
            if snake.get_head_position() == money.position:
                money.draw_quantity((0, 0, 0))
                money.randomize_position()

                money.quantity += 1

            position_x, position_y = snake.get_head_position()

            # Змейка сталкивается со своими сегментами или выходит за край.
            if ((snake.length >= 2
                 and snake.get_head_position() in snake.positions[1:]
                 )
                or position_x < 0 or position_x >= SCREEN_WIDTH
                or position_y < 0 or position_y >= SCREEN_HEIGHT
                ):
                apple.randomize_position()
                money.randomize_position()
                money.quantity = 0
                snake.reset()


if __name__ == '__main__':
    main()
