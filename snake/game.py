import enum
import time

@enum.unique
class Direction(enum.Enum):
    UP    = (0, -1)
    DOWN  = (0, 1)
    LEFT  = (-1, 0)
    RIGHT = (1, 0)


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return '[{}, {}]'.format(self.x, self.y)


class Snake():
    def __init__(self, start_position, start_direction=Direction.RIGHT, length=1):
        if length <= 0:
            raise ValueError('length must be > 0')
        self.elements = [start_position] * length
        self.direction = start_direction

    def step(self):
        self.elements[1:] = self.elements[:-1]
        self.elements[0].x += self.direction.value[0]
        self.elements[0].y += self.direction.value[1]

    def set_direction(self, direction):
        self.direction = direction

    def enlarge(self, num_elements):
        self.elements += [self.elements[-1]] * num_elements

    def get_head_position(self):
        return self.elements[0]

    def in_self_collision(self):
        return self.elements[0] in self.elements[1:]


@enum.unique
class Field(enum.Enum):
    FREE = 1
    WALL = 2


class Room():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fields = [Field.FREE] * width * height

    def get_field_value(self, position):
        if position.x < 0 or position.x > self.width:
            raise IndexError('x must be between 0 and {}'.format(self.width))
        if position.y < 0 or position.y > self.height:
            raise IndexError('y must be between 0 and {}'.format(self.height))
        return self.fields[position.y * self.width + position.x]

    def is_inside(self, position):
        if position.x <= 0 or position.x >= self.width:
            return False
        if position.y <= 0 or position.y >= self.height:
            return False
        return True


@enum.unique
class Event(enum.Enum):
    KEY_UP = 1
    KEY_DOWN = 2
    KEY_LEFT = 3
    KEY_RIGHT = 4


@enum.unique
class GameState(enum.Enum):
    RUNNING = 1
    GAME_OVER = 2


class Game():
    def __init__(self, room=Room(60, 40), initial_snake_length=1):
        self.room = room
        start_position = Position(self.room.width // 2, self.room.height // 2)
        self.snake = Snake(start_position=start_position, length=initial_snake_length)
        self.state = GameState.RUNNING

    def step(self):
        if self.state == GameState.RUNNING:
            self.snake.step()
            if not self.room.is_inside(self.snake.get_head_position()):
                self.state = GameState.GAME_OVER
            if self.snake.in_self_collision():
                self.state = GameState.GAME_OVER

    def process_events(self, events):
        for event in events:
            self.process_event(event)

    def process_event(self, event):
        if event == Event.KEY_UP:
            self.snake.set_direction(Direction.UP)
        elif event == Event.KEY_DOWN:
            self.snake.set_direction(Direction.DOWN)
        elif event == Event.KEY_RIGHT:
            self.snake.set_direction(Direction.RIGHT)
        elif event == Event.KEY_LEFT:
            self.snake.set_direction(Direction.LEFT)


class Display():
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def render(self, game):
        raise NotImplementedError()

    def get_events(self):
        raise NotImplementedError()


class DummyDisplay(Display):
    def render(self, game):
        print(game.snake.elements, game.state)

    def get_events(self):
        return []


def run_game_loop(display_type):
    game = Game()
    with display_type() as display:
        loop_rate = 10.0
        loop_duration = 1.0 / loop_rate
        while game.state != GameState.GAME_OVER:
            start_time = time.time()
            game.process_events(display.get_events())
            game.step()
            display.render(game)
            current_time = time.time()
            sleep_time = loop_duration - (current_time - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

