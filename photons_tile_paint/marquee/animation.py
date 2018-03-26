from photons_tile_paint.animation import Animation, coords_for_horizontal_line, put_characters_on_canvas, Finish
from photons_tile_paint.font.alphabet import characters as alphabet

from photons_app import helpers as hp

from photons_themes.canvas import Canvas

class TileMarqueeAnimation(Animation):
    every = 0.1
    acks = False
    coords = coords_for_horizontal_line
    duration = 0

    def setup(self):
        self.iteration = 0
        if self.options.user_coords:
            self.coords = None

    class State:
        def __init__(self, x):
            self.x = x

        def move_left(self, amount):
            return self.__class__(self.x - amount)

        def coords_for(self, original, characters):
            coords = []

            (left_x, top_y), (width, height) = original[0]
            left_x = left_x + self.x

            for char in characters:
                coords.append(((left_x, top_y), (char.width, height)))
                left_x += char.width

            return coords

    def next_state(self, prev_state, coords):
        right_x = 0
        left_x = 0
        for (user_x, top_y), (width, height) in coords:
            if user_x + width > right_x:
                right_x = user_x + width
            if user_x - self.options.text_width < left_x:
                left_x = user_x - self.options.text_width

        if prev_state is None:
            return self.State(right_x)

        nxt = prev_state.move_left(1)
        if nxt.x < left_x:
            self.iteration += 1
            if self.options.final_iteration(self.iteration):
                raise Finish("Reached max iterations")
            nxt = self.State(right_x)

        return nxt

    @hp.memoized_property
    def characters(self):
        characters = []
        for ch in self.options.text:
            characters.append(alphabet[ch])
        return characters

    def make_canvas(self, state, coords):
        canvas = Canvas()
        put_characters_on_canvas(canvas, self.characters, state.coords_for(coords, self.characters), self.options.text_color.color)
        return canvas