from pad_window import PadWindow

w = PadWindow()
gems_img = w.get_gems()

print(gems_img[3][3].get_center_pos())
# color = gems_img[2][0].get_avg_color()
# print(color)
gems_img[4][4].show()

# for i in range(5):
#     for j in range(6):
#         print(i, j, gems_img[i][j].color)

# print(gems_img[2][0].gem_type)

# b = Bbox((200, 200, 400, 300), style='xywh')
# bboxs = b.split_horizontal([1, 1, 1, 1])
