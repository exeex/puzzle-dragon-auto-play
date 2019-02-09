from bbox import Bbox
from data import GEM_COLORS


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
        print(color_labels)
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


if __name__ == '__main__':
    g = Gem(Bbox((0, 0, 10, 10)))
