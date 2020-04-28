from game import Display
from game import Event
from game import Position
from game import Field
import curses

class CursesDisplay(Display):
    def __init__(self):
        super().__init__()

    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.noecho()  # don't echo pressed keys
        curses.cbreak()  # capture input without Enter
        curses.curs_set(False) # don't display cursor
        self.stdscr.keypad(True)  # enable arrow keys
        self.stdscr.nodelay(True) # don't block on getch()
        return self

    def __exit__(self, type, value, traceback):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def render_game(self, game):
        room_pad = curses.newpad(game.room.height, game.room.width)
        for y in range(game.room.height):
            for x in range(game.room.width):
                pos = Position(x, y)
                if game.room.get_field_value(pos) == Field.FREE:
                    room_pad.addch(y, x, ord('a'))
                elif game.room.get_field_value(pos) == Field.WALL:
                    room_pad.addch(y, x, ord('X'))

        for pos in game.snake.elements:
            room_pad.addch(pos.y, pos.x, ord('S'))

        room_pad.noutrefresh(0, 0, 1, 0, game.room.height, game.room.width)

        curses.doupdate()

    def render_test(self, game):
        pad = curses.newpad(100, 100)
        # These loops fill the pad with letters; addch() is
        # explained in the next section
        for y in range(0, 99):
            for x in range(0, 99):
                pad.addch(y,x, ord('a') + (x*x+y*y) % 26)

        # Displays a section of the pad in the middle of the screen.
        # (0,0) : coordinate of upper-left corner of pad area to display.
        # (5,5) : coordinate of upper-left corner of window area to be filled
        #         with pad content.
        # (20, 75) : coordinate of lower-right corner of window area to be
        #          : filled with pad content.
        pad.refresh( 0,0, 5,5, 20,75) 

    def render_test2(self, game):
        pad = curses.newpad(game.room.height + 2, game.room.width + 2)
        for y in range(game.room.height):
            for x in range(game.room.width):
                pos = Position(x, y)
                if game.room.get_field_value(pos) == Field.FREE:
                    pad.addch(y + 1, x + 1, ord(' '))
                elif game.room.get_field_value(pos) == Field.WALL:
                    pad.addch(y + 1, x + 1, curses.ACS_BLOCK)
                if pos == game.egg_position:
                    pad.addch(y, x, ord('O'))
        for pos in game.snake.elements:
            pad.addch(pos.y, pos.x, ord('S'))

        pad.border()
        pad.refresh(0, 0, 1, 1, curses.COLS, curses.LINES)


    def render(self, game):
        self.render_test2(game)

    def get_events(self):
        c = self.stdscr.getch()
        if c == curses.KEY_UP:
            return [Event.KEY_UP]
        if c == curses.KEY_DOWN:
            return [Event.KEY_DOWN]
        if c == curses.KEY_LEFT:
            return [Event.KEY_LEFT]
        if c == curses.KEY_RIGHT:
            return [Event.KEY_RIGHT]
        return []
