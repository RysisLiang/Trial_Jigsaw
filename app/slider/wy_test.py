#!/usr/bin/env python 
# -*- coding:utf-8 -*-

import cv2


class WY_Slider(object):
    """
    wy
    """

    def __init__(self):
        super(WY_Slider, self).__init__()

    def _match_test1(self, target, template):
        """
        图像匹配方式1
        :param target:
        :param template:
        :return:
        """
        img_rgb = cv2.imread(target)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) # 灰度化
        cv2.imshow('Dectected1', img_gray)

        img_template = cv2.imread(template, cv2.IMREAD_GRAYSCALE) # 灰
        cv2.imshow('Dectected2', img_template)

        height, width = img_template.shape
        print(width, height)

        # 模板匹配
        result = cv2.matchTemplate(img_gray, img_template, cv2.TM_CCOEFF_NORMED)

        # 查找数组中匹配的最大值
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        left_up = max_loc
        right_down = (left_up[0] + height, left_up[1] + width)
        cv2.rectangle(img_rgb, left_up, right_down, (7, 279, 151), 2)
        result_x = max_loc[0]

        # 使用二分法查找阈值的精确值
        # L = 0
        # R = 1
        # while run < 20:
        #     run += 1
        #     threshold = (R + L) / 2
        #     print("threshold = {}".format(threshold))
        #     if threshold < 0:
        #         print('Error')
        #         return None
        #     loc = np.where(result >= threshold)
        #     print("loc = {}".format(len(loc[1])))
        #
        #     # 期望结果个数
        #     target_num = 5
        #
        #     if len(loc[1]) > target_num:
        #         L += (R - L) / 2
        #     elif len(loc[1]) < 1:
        #         R -= (R - L) / 2
        #     else:
        #         reult_x = loc[1][0]
        #         break
        #
        # # 框
        # for pt in zip(*loc[::-1]):
        #     cv2.rectangle(img_rgb, pt, (pt[0] + width, pt[1] + height), (7, 279, 151), 2)

        print("目标区域起点x坐标为：%d" % result_x)
        cv2.imshow("dectected", img_rgb)
        return result_x


if __name__ == '__main__':
    c = WY_Slider()

    # sf
    # a = "../static/sf/bg_1.jpeg"
    # b = "../static/sf/slider_1.png"

    # wy
    index = 2
    a = "../../static/wy/bg_{}.jpg".format(index)
    b = "../../static/wy/slider_{}.png".format(index)

    # jd
    # index = 8
    # a = "../../static/jd/bg_{}.png".format(index)
    # b = "../../static/jd/slider_{}.png".format(index)
    # # res = c._match_profile(a) # 轮廓识别 筛选很难，要求图片的较高

    # 模板匹配。
    res = c._match_test1(a, b)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(res)
