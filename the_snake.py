from abc import abstractmethod
from random import randint

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


class GameObject:
    """Базовый класс игрового объекта.

    Attributes:
        body_color (tuple): Цвет объекта.
        position (tuple): Позиция на игровом поле.
    """

    def __init__(self,
                 body_color: tuple[int, int, int] = (255, 255, 255),
                 position: tuple[int, int] = (GRID_WIDTH // 2 * GRID_SIZE,
                                              GRID_HEIGHT // 2 * GRID_SIZE
                                              )
                 ) -> None:
        self.position = position
        self.body_color = body_color

    @abstractmethod
    def draw(self) -> None:
        """Отрисовывает объект на экране.
        Должен быть переопределен в потомках.
        """
        pass


class Apple(GameObject):
    """Класс Яблока, унаследованный от GameObject.

    Attributes:
        body_color (tuple): Цвет объекта.
        position (tuple): Позиция на игровом поле.
    """

    def __init__(self, body_color: tuple[int, int, int] = (255, 0, 0)) -> None:
        """Инициализция яблока красным цветом."""
        super().__init__(body_color=body_color)

    def randomize_position(self) -> None:
        """Устанавливает случайную позицию для яблока."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self) -> None:
        """Отрисовывает яблоко в виде квадрата."""
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

    def __init__(self,
                 body_color: tuple[int, int, int] = (255, 255, 0)
                 ) -> None:
        """Инициализация монетки желтым цветом. Счетчик равен нулю."""
        super().__init__(body_color=body_color)
        self.quantity = 0

    def draw_quantity(self,
                      text_color: tuple[int, int, int] = (255, 255, 0)
                      ) -> None:
        """Отображает на экране текующее количество собранных монеток."""
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
                 length: int = 1,
                 direction: tuple[int, int] = RIGHT,
                 next_direction: tuple[int, int] | None = None,
                 body_color: tuple[int, int, int] = (0, 255, 0)
                 ) -> None:
        """Инициализация змейки зеленым цветом, длиной равной единице,
        направлением движения вправо.
        """
        super().__init__(body_color=body_color)
        self.positions: list[tuple[int, int]] = [self.position]
        self.length = length
        self.direction = direction
        self.next_direction = next_direction
        self.eaten_apple: bool = False
        self.__last: tuple[int, int] | None = None

    def update_direction(self) -> None:
        """Обновление направления движения, если оно поменялось."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Перемещает змейку в текущем направлении (direction).
        Добавляет голову и удаляет хвост, если яблоко не съедено.
        """
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

    def draw(self) -> None:
        """Отрисовывает голову и сегменты тела змейки. Затирает хвост."""
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

    def get_head_position(self) -> tuple[int, int]:
        """Возвращение координат головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сброс змейки в начальное состояние."""
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
        action (int): При нажатии происходит изменение состояния.
        background_color (tuple): Цвет фона кнопки.
        text (str): Текст, отображаемый на кнопке.
        text_color (tuple): Цвет текста кнопки.
    """

    def __init__(self,
                 rect: pygame.Rect,
                 font: pygame.font.Font,
                 action: int = STATE,
                 background_color: tuple[int, int, int] = (255, 255, 255),
                 text: str = 'Start',
                 text_color: tuple[int, int, int] = (0, 0, 0),
                 ) -> None:
        """Инициализация кнопки с определенным положением, шрифтом,
        цветом заднего фона, цветом текста, текстом, действием.
        """
        self.rect = rect
        self.background_color = background_color
        self.text = text
        self.font = font
        self.text_color = text_color
        self.action = action

    def draw(self) -> None:
        """Отрисовывает кнопку на экране."""
        pygame.draw.rect(screen, self.background_color, self.rect)
        text = self.font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


def handle_keys(game_object: Snake, button: Button) -> None:
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
    """Главная функция игры.
    Инициализирует объекты, запускает основной цикл игры.
    """
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
            colides_with_self = (
                snake.length >= 2
                and snake.get_head_position() in snake.positions[1:]
            )
            out_of_bounds = (
                position_x < 0
                or position_x >= SCREEN_WIDTH
                or position_y < 0
                or position_y >= SCREEN_HEIGHT
            )
            if colides_with_self or out_of_bounds:
                apple.randomize_position()
                money.randomize_position()
                money.quantity = 0
                snake.reset()


if __name__ == '__main__':
    main()
