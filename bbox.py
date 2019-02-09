from PIL import ImageGrab,Image  # pip install Pillow

class Bbox(tuple):

    def __new__(cls, bbox_tuple, style='xyxy'):
        if style == 'xyxy':
            x1, y1, x2, y2 = bbox_tuple
        elif style == 'xywh':
            x1, y1, w, h = bbox_tuple
            x2 = x1 + w
            y2 = y1 + h
        return super(Bbox, cls).__new__(Bbox, (float(x1), float(y1), float(x2), float(y2)))

    def __init__(self, bbox_tuple: tuple, style='xyxy'):
        self.x1, self.y1, self.x2, self.y2 = self
        self.x = self.x1
        self.y = self.y1
        self.w = self.x2 - self.x1
        self.h = self.y2 - self.y1

    def xyxy(self):
        return self.x1, self.y1, self.x2, self.y2

    def xywh(self):
        return self.x, self.y, self.w, self.h

    def get_img(self):
        return ImageGrab.grab(self)

    def show(self):
        img = self.get_img()
        img.show()

    def split_vertical(self, ratio_tuple):
        ratio_sum = sum(ratio_tuple)
        ratio_tuple = (ratio / ratio_sum for ratio in ratio_tuple)  # normalize ratios
        hs = [self.h * ratio for ratio in ratio_tuple]
        ys = [self.y + sum(hs[:i]) for i in range(len(hs))]
        xs = [self.x for _ in range(len(hs))]
        ws = [self.w for _ in range(len(hs))]

        bboxs = [Bbox(_bbox, style='xywh') for _bbox in zip(xs, ys, ws, hs)]
        return bboxs

    def split_horizontal(self, ratio_tuple):

        ratio_sum = sum(ratio_tuple)
        ratio_tuple = (ratio / ratio_sum for ratio in ratio_tuple)  # normalize ratios
        ws = [self.w * ratio for ratio in ratio_tuple]
        xs = [self.x + sum(ws[:i]) for i in range(len(ws))]
        ys = [self.y for _ in range(len(ws))]
        hs = [self.h for _ in range(len(ws))]

        bboxs = [Bbox(_bbox, style='xywh') for _bbox in zip(xs, ys, ws, hs)]
        return bboxs

    def split_grid(self, x, y):
        lines = self.split_vertical([1 for _ in range(y)])
        boxs = []
        for line in lines:
            boxs.append(line.split_horizontal([1 for _ in range(x)]))
        return boxs

    def get_center_pos(self):
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    def get_avg_color(self):
        image = self.get_img().resize((1, 1), Image.ANTIALIAS)
        pixel = image.getdata()
        return tuple(pixel)[0]
