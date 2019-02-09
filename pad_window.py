import win32gui  # pip install pywin32
from PIL import ImageGrab  # pip install Pillow
from bbox import Bbox
from gem import Gem




class PadWindow:
    def __init__(self, window_name="夜神模擬器"):
        self.window_name = window_name

    def get_window_info(self):
        handle = win32gui.FindWindow(0, self.window_name)
        if handle == 0:
            raise AttributeError("Please open emulator")
        else:
            x1, y1, x2, y2 = tuple(win32gui.GetWindowRect(handle))
            return Bbox((x1, y1, x2, y2))

    def get_gem_board_bbox(self):
        window_bbox = self.get_window_info()
        x1, y1, x2, y2 = window_bbox.xyxy()
        w = window_bbox.w
        h = window_bbox.h

        gems_bbox = Bbox((x1 + w * 0.01, y1 + h * 0.55, x2 - w * 0.01, y2 - h * 0.007))
        return gems_bbox

    def get_full_screen_img(self):
        window_bbox = self.get_window_info()
        img_ready = ImageGrab.grab(window_bbox)
        img_ready.show()

    def get_gems(self):
        gems_bbox = self.get_gem_board_bbox()
        gems = gems_bbox.split_grid(6, 5)
        gems = [[Gem(gem) for gem in gem_line] for gem_line in gems]

        return gems
