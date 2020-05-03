import enum
import time
import copy
import random
from collections import deque

@enum.unique
class Direction(enum.Enum):
    UP    = (0, -1)
    DOWN  = (0, 1)
    LEFT  = (-1, 0)
    RIGHT = (1, 0)


class Snake():
    def __init__(self, start_position, start_direction=Direction.RIGHT, length=1):
        if length <= 0:
            raise ValueError('length must be > 0')
        self.elements = deque()
        for i in range(length):
            self.elements.append(start_position)
        self.direction = start_direction

    def step(self):
        new_head_pos = (self.elements[0][0] + self.direction.value[0],
                        self.elements[0][1] + self.direction.value[1])
        self.elements.pop()
        self.elements.appendleft(new_head_pos)

    def set_direction(self, direction):
        self.direction = direction

    def enlarge(self, num_elements=1):
        for i in range(num_elements):
            self.elements.append(copy.deepcopy(self.elements[-1]))

    def get_head_position(self):
        return self.elements[0]

    def in_self_collision(self):
        for i in range(1, len(self.elements)):
            if self.elements[i] == self.elements[0]:
                return True
        return False

    def occupies(self, position):
        return position in self.elements


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
        if position[0] < 0 or position[0] > self.width:
            raise IndexError('x must be between 0 and {}'.format(self.width))
        if position[1] < 0 or position[1] > self.height:
            raise IndexError('y must be between 0 and {}'.format(self.height))
        return self.fields[position[1] * self.width + position[0]]

    def is_inside(self, position):
        if position[0] < 0 or position[0] >= self.width:
            return False
        if position[1] < 0 or position[1] >= self.height:
            return False
        return True

    def is_free(self, position):
        return self.is_inside(position) and self.get_field_value(position) == Field.FREE


@enum.unique
class GameState(enum.Enum):
    RUNNING = 1
    GAME_OVER = 2


class Game():
    def __init__(self, room=Room(60, 60), initial_snake_length=2):
        self.room = room
        self.score = 0
        start_position = (self.room.width // 2, self.room.height // 2)
        self.snake = Snake(start_position=start_position, length=initial_snake_length)
        self.randomize_egg_position()
        self.state = GameState.RUNNING

    def randomize_egg_position(self):
        self.egg_position = (random.randrange(0, self.room.width), random.randrange(0, self.room.height))

    def step(self):
        if self.state == GameState.RUNNING:
            self.snake.step()
            if self.snake.get_head_position() == self.egg_position:
                self.snake.enlarge()
                self.randomize_egg_position()
                self.score += 1
            if not self.room.is_inside(self.snake.get_head_position()):
                self.state = GameState.GAME_OVER
            if self.snake.in_self_collision():
                self.state = GameState.GAME_OVER

    def process_actions(self, actions):
        for action in actions:
            self.process_action(action)

    def process_action(self, action):
        self.snake.set_direction(action)


class Display():
    @classmethod
    def all_subclasses(cls):
        subclasses = cls.__subclasses__()
        for c in subclasses:
            subclasses += c.all_subclasses()
        return subclasses

    @classmethod
    def create(cls, name):
        return next(c for c in cls.all_subclasses() if c.__name__ == name)()

    @classmethod
    def get_available_types(cls):
        return [c.__name__ for c in cls.all_subclasses()]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def render(self, game):
        raise NotImplementedError()

    def on_eat_egg(self):
        pass


class InputDevice():
    @classmethod
    def all_subclasses(cls):
        subclasses = cls.__subclasses__()
        for c in subclasses:
            subclasses += c.all_subclasses()
        return subclasses

    @classmethod
    def create(cls, name):
        return next(c for c in cls.all_subclasses() if c.__name__ == name)()

    @classmethod
    def get_available_types(cls):
        return [c.__name__ for c in cls.all_subclasses()]

    def __init__(self):
        pass

    def get_actions(self):
        raise NotImplementedError()


class NoDisplay(Display):
    def render(self, game):
        pass


class DummyInputDevice(InputDevice):
    def get_actions(self):
        return []


def run_game_loop(game, input_device, display, speed):
    while game.state != GameState.GAME_OVER:
        start_time = time.time()
        display.render(game)
        game.process_actions(input_device.get_actions())
        game.step()
        if speed is not None and speed > 0:
            current_time = time.time()
            loop_duration = 1.0 / speed
            sleep_time = loop_duration - (current_time - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

