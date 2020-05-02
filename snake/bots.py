import game
import random


class Bot(game.InputDevice):
    @classmethod
    def all_subclasses(cls):
        subclasses = cls.__subclasses__()
        for c in subclasses:
            subclasses += c.all_subclasses()
        return subclasses

    @classmethod
    def create(cls, name, game):
        return next(c for c in cls.all_subclasses() if c.__name__ == name)(game)

    @classmethod
    def get_available_types(cls):
        return [c.__name__ for c in cls.all_subclasses()]

    def __init__(self, game):
        self.game = game

    def get_valid_actions(self):
        valid_actions = []
        head_pos = self.game.snake.get_head_position()
        for dir in game.Direction:
            pos = head_pos + dir
            if self.game.room.is_free(pos) and not self.game.snake.occupies(pos):
                valid_actions.append(dir)
        return valid_actions

    def get_actions(self):
        raise NotImplementedError()


class RandomBot(Bot):
    def __init__(self, game):
        super().__init__(game)

    def get_actions(self):
        valid_actions = self.get_valid_actions()
        if len(valid_actions) == 0:
            return []
        return [random.choice(valid_actions)]


class GoTowardsEggBot(Bot):
    def __init__(self, game):
        super().__init__(game)

    def get_actions(self):
        valid_actions = self.get_valid_actions()
        if len(valid_actions) == 0:
            return []
        egg_pos = self.game.egg_position
        head_pos = self.game.snake.get_head_position()
        possible_future_positions = [head_pos + action for action in valid_actions]
        possible_future_egg_distances = [game.Position.manhattan_distance(egg_pos, pos) for pos in possible_future_positions]
        return [valid_actions[possible_future_egg_distances.index(min(possible_future_egg_distances))]]

