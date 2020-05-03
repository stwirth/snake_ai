from game import Display
from game import InputDevice
from game import Direction
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

    def render(self, game):
        height, width = self.stdscr.getmaxyx()
        # we want to draw the outer border so we need two more characters
        # in each direction
        if game.get_room_height() + 2 > height or \
           game.get_room_width() + 2 > width:
            raise IndexError('Window is only {} x {} but game needs {} x {}.'.format(
                             width, height, game.get_room_width(), game.get_room_height()))
        pad = curses.newpad(game.get_room_height() + 2, game.get_room_width() + 2)
        for y in range(game.get_room_height()):
            for x in range(game.get_room_width()):
                pos = (x, y)
                field_value = game.get_field_value(pos)
                if field_value == Field.FREE:
                    pad.addch(y + 1, x + 1, ord(' '))
                elif field_value == Field.WALL:
                    pad.addch(y + 1, x + 1, curses.ACS_BLOCK)
        egg_pos = game.get_egg_position()
        pad.addch(egg_pos[1] + 1, egg_pos[0] + 1, ord('O'))
        for pos in game.get_snake_elements():
            if pos[0] >= 0 and pos[1] >= 0 and pos[0] < width and pos[1] < height:
                pad.addch(pos[1] + 1, pos[0] + 1, curses.ACS_BLOCK, curses.color_pair(1))

        pad.border()
        pad.addstr(0, 3, 'Score:{:>3}'.format(game.get_score()))
        pad.refresh(0, 0, 0, 0, curses.COLS, curses.LINES)

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

