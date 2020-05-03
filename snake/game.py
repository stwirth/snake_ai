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
        self._elements = deque()
        for i in range(length):
            self._elements.append(start_position)
        self._direction = start_direction

    def get_elements(self):
        return self._elements

    def step(self):
        new_head_pos = (self._elements[0][0] + self._direction.value[0],
                        self._elements[0][1] + self._direction.value[1])
        self._elements.pop()
        self._elements.appendleft(new_head_pos)

    def set_direction(self, direction):
        self._direction = direction

    def enlarge(self, num_elements=1):
        for i in range(num_elements):
            self._elements.append(copy.deepcopy(self._elements[-1]))

    def get_head_position(self):
        return self._elements[0]

    def in_self_collision(self):
        element_iter = iter(self._elements)
        head = next(element_iter)  # makes following loop start at second element
        for element in element_iter:
            if element == head:
                return True
        return False

    def occupies(self, position):
        return position in self._elements


@enum.unique
class Field(enum.Enum):
    FREE = 1
    WALL = 2


class Room():
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._fields = [Field.FREE] * width * height

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_field_value(self, position):
        if position[0] < 0 or position[0] > self._width:
            raise IndexError('x must be between 0 and {}'.format(self._width))
        if position[1] < 0 or position[1] > self._height:
            raise IndexError('y must be between 0 and {}'.format(self._height))
        return self._fields[position[1] * self._width + position[0]]

    def is_inside(self, position):
        if position[0] < 0 or position[0] >= self._width:
            return False
        if position[1] < 0 or position[1] >= self._height:
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
        self._room = room
        self._score = 0
        start_position = (self._room.get_width() // 2, self._room.get_height() // 2)
        self._snake = Snake(start_position=start_position, length=initial_snake_length)
        self._randomize_egg_position()
        self._state = GameState.RUNNING

    def _randomize_egg_position(self):
        self._egg_position = (random.randrange(0, self._room.get_width()),
                              random.randrange(0, self._room.get_height()))

    def get_egg_position(self):
        return self._egg_position

    def get_room_width(self):
        return self._room.get_width()

    def get_room_height(self):
        return self._room.get_height()

    def get_field_value(self, pos):
        return self._room.get_field_value(pos)

    def get_snake_elements(self):
        return self._snake.get_elements()

    def get_state(self):
        return self._state

    def get_score(self):
        return self._score

    def is_free(self, pos):
        return self._room.is_free(pos) and pos not in self._snake.get_elements()

    def step(self):
        if self._state == GameState.RUNNING:
            self._snake.step()
            if self._snake.get_head_position() == self._egg_position:
                self._snake.enlarge()
                self._randomize_egg_position()
                self._score += 1
            if not self._room.is_inside(self._snake.get_head_position()):
                self._state = GameState.GAME_OVER
            if self._snake.in_self_collision():
                self._state = GameState.GAME_OVER

    def process_actions(self, actions):
        for action in actions:
            self.process_action(action)

    def process_action(self, action):
        self._snake.set_direction(action)


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
    while game.get_state() != GameState.GAME_OVER:
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

