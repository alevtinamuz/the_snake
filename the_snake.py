from abc import abstractmethod
from random import randint

import pygame as pg

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

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Цвета для объектов
APPLE_COLOR = RED
SNAKE_COLOR = GREEN
MONEY_COLOR = YELLOW
BORDER_COLOR = (93, 216, 228)
BOARD_BACKGROUND_COLOR = BLACK
MONEY_TEXT_COLOR = YELLOW

# Цвета для интерфейса
BUTTON_TEXT_COLOR = BLACK
BUTTON_BACKGROUND_COLOR = WHITE

# Скорость движения змейки:
SPEED = 6

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игрового объекта.

    Attributes:
        body_color (tuple): Цвет объекта.
        position (tuple): Позиция на игровом поле.
    """

    def __init__(
        self,
        body_color: tuple[int, int, int] = WHITE,
        position: tuple[int, int] = (
            GRID_WIDTH // 2 * GRID_SIZE,
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
        raise NotImplementedError(
            f'Класс {self.__class__.__name__}'
            'не реализует обязательный метод draw().'
        )


class Apple(GameObject):
    """Класс Яблока, унаследованный от GameObject.

    Attributes:
        body_color (tuple): Цвет объекта.
        position (tuple): Позиция на игровом поле.
    """

    def __init__(
        self,
        snake_positions: list[tuple[int, int]],
        body_color: tuple[int, int, int] = APPLE_COLOR
    ) -> None:
        """Инициализция яблока красным цветом."""
        super().__init__(body_color=body_color)
        self.randomize_position(snake_positions)

    def randomize_position(
        self,
        snake_positions: list[tuple[int, int]]
    ) -> None:
        """Устанавливает случайную позицию для яблока.
        И проверяет не находится ли там сейчас змея.
        """
        while self.position in snake_positions:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )

    def draw(self) -> None:
        """Отрисовывает яблоко в виде квадрата."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Money(Apple):
    """Класс Монеток, унаследованный от Apple.

    Attributes:
        body_color (tuple): Цвет объекта.
        position (tuple): Позиция на игровом поле.
        quantity (int): Количество собранных монеток.
    """

    def __init__(
        self,
        snake_positions: list[tuple[int, int]],
        body_color: tuple[int, int, int] = MONEY_COLOR
    ) -> None:
        """Инициализация монетки желтым цветом. Счетчик равен нулю."""
        super().__init__(
            snake_positions=snake_positions,
            body_color=body_color
        )
        self.quantity = 0

    def draw_quantity(
        self,
        text_color: tuple[int, int, int] = MONEY_TEXT_COLOR
    ) -> None:
        """Отображает на экране текующее количество собранных монеток."""
        font = pg.font.Font(size=36)
        text = font.render(str(self.quantity), False, text_color)
        text_rect = text.get_rect(center=(20, 20))
        screen.fill(BOARD_BACKGROUND_COLOR, text_rect)
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

    def __init__(
        self,
        body_color: tuple[int, int, int] = SNAKE_COLOR
    ) -> None:
        """Инициализация змейки зеленым цветом, длиной равной единице,
        направлением движения вправо.
        """
        super().__init__(body_color=body_color)
        self.reset()

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
        direction_x, direction_y = self.direction

        next_position_x += direction_x * GRID_SIZE
        next_position_y += direction_y * GRID_SIZE

        self.positions.insert(0, (next_position_x, next_position_y))

        self.__last = self.positions[-1]

        if len(self.positions) - self.length == 1 and not self.eaten_apple:
            self.positions.pop()

        self.eaten_apple = False

    def draw(self) -> None:
        """Отрисовывает голову и сегменты тела змейки. Затирает хвост."""
        # Отрисовка головы змейки
        head_rect = pg.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.__last:
            last_rect = pg.Rect(self.__last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

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
        rect (pg.Rect): Прямоугольник, задающий размер и положение кнопки.
        font (pg.font.Font): Шрифт текста кнопки.
        action (int): При нажатии происходит изменение состояния.
        background_color (tuple): Цвет фона кнопки.
        text (str): Текст, отображаемый на кнопке.
        text_color (tuple): Цвет текста кнопки.
    """

    def __init__(
        self,
        rect: pg.Rect,
        font: pg.font.Font,
        action: int = STATE,
        background_color: tuple[int, int, int] = BUTTON_BACKGROUND_COLOR,
        text: str = 'Start',
        text_color: tuple[int, int, int] = BUTTON_TEXT_COLOR,
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
        pg.draw.rect(screen, self.background_color, self.rect)
        text = self.font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


def handle_quit(event: pg.event) -> None:
    """Обрабатывает событие выхода из игры."""
    if event.type == pg.QUIT:
        pg.quit()
        raise SystemExit


def handle_menu_click(event: pg.event, button: Button) -> bool:
    """Обрабатывает событие нажатие по стартовой кнопке."""
    return (
        event.type == pg.MOUSEBUTTONDOWN
        and button.rect.collidepoint(event.pos)
    )


def handle_game_key(event: pg.event, game_object: Snake) -> None:
    """Обрабытывает движения змейки.
    Обновляет snake.direction в зависимости от нажатой кнопки.
    """
    if event.type == pg.KEYDOWN:
        if event.key == pg.K_UP and game_object.direction != DOWN:
            game_object.next_direction = UP
        elif event.key == pg.K_DOWN and game_object.direction != UP:
            game_object.next_direction = DOWN
        elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
            game_object.next_direction = LEFT
        elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
            game_object.next_direction = RIGHT


def handle_keys(game_object: Snake, button: Button) -> None:
    """Общий Keylogger. Обрабатывает все события в зависимости от STATE."""
    global STATE
    for event in pg.event.get():
        handle_quit(event)
        if STATE == MENU:
            if handle_menu_click(event, button):
                STATE = GAME
                game_object.reset()
        elif STATE == GAME:
            handle_game_key(event, game_object)


def main():
    """Главная функция игры.
    Инициализирует объекты, запускает основной цикл игры.
    """
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)
    money = Money(snake.positions)
    start_button = Button(
        rect=pg.Rect(
            (
                GRID_WIDTH // 2 * GRID_SIZE - 100,
                GRID_HEIGHT // 2 * GRID_SIZE - 50
            ),
            (200, 100)
        ),
        font=pg.font.Font(None, size=36),
    )

    while True:
        clock.tick(SPEED)
        handle_keys(snake, start_button)

        if STATE == MENU:
            start_button.draw()

        elif STATE == GAME:
            snake.update_direction()
            snake.move()

            # Змейка съедает яблоко
            if snake.get_head_position() == apple.position:
                apple.randomize_position(snake.positions)
                snake.eaten_apple = True
                snake.length += 1

            # Змейка собирает монетку.
            elif snake.get_head_position() == money.position:
                money.randomize_position(snake.positions)

                money.quantity += 1

            position_x, position_y = snake.get_head_position()

            # Змейка сталкивается со своими сегментами или выходит за край.
            colides_with_self = (
                snake.get_head_position() in snake.positions[4:]
            )
            out_of_bounds = (
                position_x < 0
                or position_x >= SCREEN_WIDTH
                or position_y < 0
                or position_y >= SCREEN_HEIGHT
            )
            if colides_with_self or out_of_bounds:
                apple.randomize_position(snake.positions)
                money.randomize_position(snake.positions)
                money.quantity = 0
                snake.reset()

            snake.draw()
            apple.draw()
            money.draw()
            money.draw_quantity()
        pg.display.update()


if __name__ == '__main__':
    main()
