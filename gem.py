from bbox import Bbox
from data import GEM_COLORS
import numpy as np
from copy import deepcopy


class Gem:
    def __init__(self, bbox: Bbox):
        self.bbox = bbox
        self.img = bbox.get_img()
        self.color = bbox.get_avg_color()
        self.center = bbox.get_center_pos()
        self.gem_type = self.get_self_gem_type()

    def get_self_gem_type(self):
        mse_s = [self.mse_distance(self.color, color) for color in GEM_COLORS]
        color_labels = [i for i in range(len(GEM_COLORS))]

        color_labels = list(zip(mse_s, color_labels))
        color_labels.sort(key=lambda x: x[0])
        color = color_labels[0][1]

        return color

    @staticmethod
    def mse_distance(color_1: tuple, color_2: tuple):
        return (color_1[0] - color_2[0]) ** 2 + \
               (color_1[1] - color_2[1]) ** 2 + \
               (color_1[2] - color_2[2]) ** 2

    def show(self):
        self.bbox.show()

    def get_center_pos(self):
        return self.bbox.get_center_pos()


class GemMatrix:
    def __init__(self, gems=None):

        if gems:
            self.size_x = len(gems)
            self.size_y = len(gems[0])
            self.data = np.zeros((self.size_x, self.size_y)).astype(np.int)
            self.centers = np.zeros((self.size_x, self.size_y, 2)).astype(np.int)
            self.depth = 0

            for i in range(self.size_x):
                for j in range(self.size_y):
                    self.data[i, j] = gems[i][j].gem_type
                    self.centers[i, j, 0], self.centers[i, j, 1] = gems[i][j].center

        else:
            self.size_x = 5
            self.size_y = 6
            self.data = np.zeros((self.size_x, self.size_y)).astype(np.int)
            self.centers = np.zeros((self.size_x, self.size_y, 2)).astype(np.int)
            self.depth = 0

        self.selected_gem = None

    def clone(self):
        """ Create a deep clone of this game state.
                """
        new_gm = deepcopy(self)
        new_gm.depth += 1
        return new_gm

    def do_move(self, move):
        move()

    def get_moves(self):
        if not self.selected_gem:
            return [self.do_select]
        else:
            moves = []
            if self.selected_gem[0] > 0:
                moves.append(self.do_move_up)
            if self.selected_gem[0] < self.size_x - 1:
                moves.append(self.do_move_down)
            if self.selected_gem[1] > 0:
                moves.append(self.do_move_left)
            if self.selected_gem[1] < self.size_y - 1:
                moves.append(self.do_move_right)
            return moves

    def get_result(self, playerjm):
        """ Get the game result from the viewpoint of playerjm.
        """
        combo = self.calculate_combo()
        if (combo / (self.depth + 0.001)) > 1 / 7 and combo > 4:
            return 1. * combo
        else:
            return 0.

    def calculate_combo(self):
        return 1

    def swap(self, pos1, pos2):
        self.data[pos1], self.data[pos2] = self.data[pos2], self.data[pos1]

    def do_select(self, i=1, j=1):
        self.selected_gem = (i, j)

    def do_move_up(self):
        new_select = (self.selected_gem[0] - 1, self.selected_gem[1])
        self.swap(self.selected_gem, new_select)
        self.selected_gem = new_select

    def do_move_down(self):
        new_select = (self.selected_gem[0] + 1, self.selected_gem[1])
        self.swap(self.selected_gem, new_select)
        self.selected_gem = new_select

    def do_move_left(self):
        new_select = (self.selected_gem[0], self.selected_gem[1] - 1)
        self.swap(self.selected_gem, new_select)
        self.selected_gem = new_select

    def do_move_right(self):
        new_select = (self.selected_gem[0], self.selected_gem[1] + 1)
        self.swap(self.selected_gem, new_select)
        self.selected_gem = new_select

    def __repr__(self):
        return self.data.__repr__()


if __name__ == '__main__':
    gm = GemMatrix()
    gm.data = np.array([[2, 1, 2, 0, 0, 0],
                        [2, 1, 2, 0, 2, 1],
                        [2, 1, 1, 1, 2, 1],
                        [3, 3, 3, 3, 2, 1],
                        [1, 1, 1, 4, 4, 4]])
