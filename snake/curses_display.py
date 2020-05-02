from game import Display
from game import InputDevice
from game import Direction
from game import Position
from game import Field
import curses

class CursesDisplay(Display, InputDevice):
    def __init__(self):
        super().__init__()

    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.start_color()  # we want to use color
        curses.noecho()  # don't echo pressed keys
        curses.cbreak()  # capture input without Enter
        curses.curs_set(False) # don't display cursor
        self.stdscr.keypad(True)  # enable arrow keys
        self.stdscr.nodelay(True) # don't block on getch()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        return self

    def __exit__(self, type, value, traceback):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def render_test2(self, game):
        height, width = self.stdscr.getmaxyx()
        # we want to draw the outer border so we need two more characters
        # in each direction
        if game.room.height + 2 > height or \
           game.room.width + 2 > width:
            raise IndexError('Window is only {} x {} but game needs {} x {}.'.format(
                             width, height, game.room.width, game.room.height))
        pad = curses.newpad(game.room.height + 2, game.room.width + 2)
        for y in range(game.room.height):
            for x in range(game.room.width):
                pos = Position(x, y)
                if game.room.get_field_value(pos) == Field.FREE:
                    pad.addch(y + 1, x + 1, ord(' '))
                elif game.room.get_field_value(pos) == Field.WALL:
                    pad.addch(y + 1, x + 1, curses.ACS_BLOCK)
                if pos == game.egg_position:
                    pad.addch(y + 1, x + 1, ord('O'))
        for pos in game.snake.elements:
            if pos.x >= 0 and pos.y >= 0 and pos.x <= width and pos.y <= height:
                pad.addch(pos.y + 1, pos.x + 1, curses.ACS_BLOCK, curses.color_pair(1))

        pad.border()
        pad.refresh(0, 0, 0, 0, curses.COLS, curses.LINES)

    def render(self, game):
        self.render_test2(game)

    def get_actions(self):
        c = self.stdscr.getch()
        if c == curses.KEY_UP:
            return [Direction.UP]
        if c == curses.KEY_DOWN:
            return [Direction.DOWN]
        if c == curses.KEY_LEFT:
            return [Direction.LEFT]
        if c == curses.KEY_RIGHT:
            return [Direction.RIGHT]
        return []

    def on_eat_egg(self):
        curses.beep()
