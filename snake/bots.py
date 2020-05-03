import game
import random


def propagate(pos, direction):
    return (pos[0] + direction.value[0], pos[1] + direction.value[1])


def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


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
        head_pos = self.game.get_snake_elements()[0]
        for dir in game.Direction:
            pos = propagate(head_pos, dir)
            if self.game.is_free(pos):
                valid_actions.append((dir, pos))
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
        return [random.choice(valid_actions)[0]]


class GoTowardsEggBot(Bot):
    def __init__(self, game):
        super().__init__(game)

    def get_actions(self):
        valid_actions = self.get_valid_actions()
        if len(valid_actions) == 0:
            return []
        egg_pos = self.game.get_egg_position()
        head_pos = self.game.get_snake_elements()[0]
        possible_future_positions = [pos for (_, pos) in valid_actions]
        possible_future_egg_distances = [manhattan_distance(egg_pos, pos) for pos in possible_future_positions]
        best_index = possible_future_egg_distances.index(min(possible_future_egg_distances))
        return [valid_actions[best_index][0]]

