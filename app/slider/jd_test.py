#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import base64
import random
import re
import time

import cv2
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app.slider import base64_to_image
from app import get_random_float


class JD_Slider(object):

    def __init__(self):
        super(JD_Slider, self).__init__()
        # 实际地址
        self.url = 'https://union.jd.com/login'
        options = ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        # 账户信息
        self.username = "15820156923" # 账户名称
        self.password = "" # 账户密码
        # 下载图片的临时路径
        self.target_path = "../static/temp/target.png"
        self.template_path = "../static/temp/template.png"
        # 网页图片缩放
        self.zoom = 1

    def _open(self):
        self.driver.get(self.url)

    def _close(self):
        self.driver.close()

    def main(self):
        """
        程序入口
        :return:
        """
        print("开始准备")
        try:
            self._open()
            time.sleep(1)
            self._switch_iframe()
            self._login()
            self._crack_slider()
        except:
            print("程序出现异常")
        finally:
            print("结束程序")

    def _switch_iframe(self):
        """
        切换iframe
        :return:
        """
        # 找到“嵌套”的iframe
        iframe = self.driver.find_element_by_xpath('//iframe')
        if iframe:
            print("切换到iframe")
            self.driver.switch_to.frame(iframe)
        else:
            print("没有找到iframe")

    def _login(self):
        """
        登录
        :return:
        """
        print("填写账号")
        input_ele = self.driver.find_element_by_id("loginname")
        input_ele.clear()

        time.sleep(random.uniform(0.1, 0.5))
        input_ele.send_keys(self.username[0:3])
        time.sleep(random.uniform(0.5, 0.8))
        input_ele.send_keys(self.username[3:])
        time.sleep(random.uniform(0.2, 0.8))

        input_ele.send_keys(Keys.ENTER)
        print("点击登录")

    # 滑块
    def _crack_slider(self):
        """
        解析滑块
        :return:
        """
        # 获取图片
        pic_success = self._get_pic()
        if pic_success:
            # 模板匹配
            target = cv2.imread(self.target_path)
            template = cv2.imread(self.template_path)
            distance = self._match_templet(target, template)
            print("位移距离 distance = %d" % distance)

            # 轨迹
            tracks = self._get_tracks3(distance * self.zoom)

            # 移动滑块
            slider_success = self._slider_action(tracks)
            if slider_success:
                print("等待下一次尝试")
                time.sleep(5)
                print("开始下一次尝试")
                self._crack_slider()
            else:
                print("程序结束")
        else:
            print("结束")

    def _get_pic(self):
        """
        下载图片到本地
        :return:
        """
        print("查找缺口图片")
        time.sleep(3)
        try:
            target = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='JDJRV-bigimg']/img")))
            template = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='JDJRV-smallimg']/img")))
            if target and template:
                print("开始下载图片")
                target_base64 = target.get_attribute('src')
                template_base64 = template.get_attribute('src')
                target_base64_str = re.sub(r'data:[a-z]*/[a-z]*;base64,', '', target_base64)
                template_base64_str = re.sub(r'data:[a-z]*/[a-z]*;base64,', '', template_base64)
                # save
                base64_to_image(target_base64_str, self.target_path)
                base64_to_image(template_base64_str, self.template_path)

                time.sleep(1)

                # zoom
                local_img = Image.open(self.target_path)
                size_loc = local_img.size
                self.zoom = 281 / int(size_loc[0])
                print("计算缩放比例 zoom = %f" % round(self.zoom, 4))
                return True
            else:
                print("未找到缺口图片")
                return False
        except:
            print("获取缺口图片异常")
            return False

    def _slider_action(self, tracks):
        """
        移动滑块
        :return:
        """
        print("开始移动滑块")
        # 点击滑块
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'JDJRV-slide-btn')))
        if slider:
            ActionChains(self.driver).click_and_hold(slider).perform()

            # 正向滑动
            for track in tracks['forward_tracks']:
                yoffset_random = random.uniform(-2, 4)
                ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=yoffset_random).perform()

            time.sleep(random.uniform(0.2, 0.6))

            # 反向滑动
            for back_tracks in tracks['back_tracks']:
                yoffset_random = random.uniform(-2, 2)
                ActionChains(self.driver).move_by_offset(xoffset=back_tracks, yoffset=yoffset_random).perform()

            # 抖动
            ActionChains(self.driver).move_by_offset(
                xoffset=get_random_float(-1, -3),
                yoffset=get_random_float(-2, 2)
            ).perform()
            ActionChains(self.driver).move_by_offset(
                xoffset=get_random_float(1, 3),
                yoffset=get_random_float(-2, 2)
            ).perform()

            time.sleep(get_random_float(0.2, 0.6))
            ActionChains(self.driver).release().perform()

            print("滑块移动成功")
            return True
        else:
            print("未找到滑块")
            return False

    # test 测试验证方法
    def _match_profile(self, image_path):
        """
        通过轮廓识别来找到位置
        :param image_path: 带有缺口的图片
        :return:
        """
        image = cv2.imread(image_path)
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        # canny = cv2.Canny(blurred, 200, 400)
        canny = cv2.Canny(blurred, 50, 370)

        cv2.imshow('image2', blurred)
        cv2.imshow('image3', canny)
        cv2.imshow('image4', image)

        """
        它返回了你所处理的图像，轮廓的点集，各层轮廓的索引
        """
        binary, contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # binary, contours, hierarchy = cv2.findContours(canny, 3, cv2.CHAIN_APPROX_SIMPLE)
        for i, contour in enumerate(contours):
            M = cv2.moments(contour)
            if M['m00'] == 0:
                cx = cy = 0
            else:
                cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']

            # 轮廓筛选
            if 20 < cv2.contourArea(contour) < 2000 and 50 < cv2.arcLength(contour, True) < 350:
                # if cx < 400:
                #     continue
                x, y, w, h = cv2.boundingRect(contour)  # 外接矩形
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.imshow('image1', image)

                print("选择的值 ：area = {}, length = {}, cx = {}, cy = {}".format(
                    cv2.contourArea(contour),
                    cv2.arcLength(contour, True),
                    cx,
                    cy
                ))
                print("选择的值 ：x = {}, y = {}, w = {}, h = {}".format(x, y, w, h))

        cv2.imshow('image1-1', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return 0

    def _match_templet(self, img_target, img_template):
        """
        模板匹配（用于寻找缺口）
        :param img_target: 带有缺口的背景图
        :param img_template: 缺口的滑块图
        :return: 缺口所在的位置的x轴距离
        """
        print("图片缺口模板匹配")

        # 滑块图片处理
        tpl = self.__handle_slider_img(img_template) # 误差来源就在于滑块的背景图为白色
        # cv2.imshow("template", tpl)

        # 图片高斯滤波
        blurred = cv2.GaussianBlur(img_target, (3, 3), 0)
        # cv2.imshow("blurred2", blurred)

        # 图片灰度化
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("gray2", gray)

        width, height = tpl.shape[:2]

        # 图片二值化（针对jd，二值化后的效果不是很好）
        # ret, target = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        # ret, target = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
        # cv2.imshow("target", target)
        # 二值化模板匹配
        # result = cv2.matchTemplate(target, tpl, cv2.TM_CCOEFF_NORMED) # 使用二值化图片

        # 灰度化模板匹配
        result = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED) # 使用灰度化图片
        print("result = {}".format(len(np.where(result >= 0.5)[0])))

        # 查找数组中匹配的最大值
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        left_up = max_loc
        right_down = (left_up[0] + height, left_up[1] + width)
        cv2.rectangle(img_target, left_up, right_down, (7, 279, 151), 2)
        print('匹配结果区域起点x坐标为：%d' % max_loc[0])
        cv2.imshow('dectected', img_target)

        return left_up[0]

    def __handle_slider_img(self, image):
        """
        对滑块进行二值化处理
        :param image: cv类型的图片对象
        :return:
        """
        kernel = np.ones((8, 8), np.uint8)  # 去滑块的前景噪声内核
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 灰度化

        # 灰化背景
        width, heigth = gray.shape
        for h in range(heigth):
            for w in range(width):
                if gray[w, h] == 0:
                    gray[w, h] = 96
        # cv2.imshow('gray', gray)

        # 排除背景
        binary = cv2.inRange(gray, 96, 96)
        res = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)  # 开运算去除白色噪点
        # cv2.imshow('res1', res)
        return res

    def _get_gap(self, img1, img2):
        """
        获取缺口偏移量
        :param img1: 不带缺口图片
        :param img2: 带缺口图片
        :return:
        """
        left = 68
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.__is_pixel_equal(img1, img2, i, j):
                    left = i
                    return left
        return left

    def __is_pixel_equal(self, img1, img2, x, y):
        """
        判断两个像素是否相同
        :param img1:
        :param img2:
        :param x:
        :param y:
        :return:
        """
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        threshold = 60
        if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(
                pix1[2] - pix2[2] < threshold)):
            return True
        else:
            return False

    # ---- 拖拽轨迹计算 start ----

    def _get_tracks0(self, distance):
        """
        根据偏移量获取移动轨迹1
        :param distance: 偏移量
        :return: 移动轨迹
        """
        trace = []
        mid = distance * 3 / 5
        # 设置初始位置、初始速度、时间间隔
        current, v, t = 0, 0, 0.2
        distance += 20

        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3
            s = v * t + 0.5 * a * (t ** 2)
            v = v + a * t
            current += s
            trace.append(round(s))

        back_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]
        return {'forward_tracks': trace, 'back_tracks': back_tracks}

    def _get_tracks1(self, distance):
        """
        根据偏移量获取移动轨迹1
        :param distance: 偏移量
        :return: 移动轨迹
        """
        trace = []
        mid = distance * round(random.uniform(3, 4), 4) / 5
        # 设置初始位置、初始速度、时间间隔
        current, v, t = 0, 500, 0.005
        distance += 20

        while current < distance:
            if current < mid:
                a = random.uniform(2.4, 2.8)
            else:
                a = random.uniform(-3, -2)

            s = v * t + 0.5 * a * (t ** 2)
            v = v + a * t
            current += s
            trace.append(round(s))

        back_tracks = [-3, -3, -3, -2, -2, -2, -2, -2, -1, -1, -1, -1, -1]
        return {'forward_tracks': trace, 'back_tracks': back_tracks}

    def _get_tracks2(self, distance):
        """
        根据偏移量获取移动轨迹2
        :param distance: 偏移量
        :return: 移动轨迹
        """
        trace = []
        mid = distance * 3 / 5
        # 设置初始位置、初始速度、时间间隔
        current, v0, t = 0.0, 0.9, 0.2

        while current < distance:
            if current < mid:
                a = round(random.uniform(0.5, 0.8), 2)
            else:
                a = round(random.uniform(-0.7, -0.9), 2)
            move = v0 * t + 1 / 2 * a * (t ** 2)
            move = int(move)
            v = v0 + a * t
            # 重置初速度
            v0 = v
            # 重置起点
            current += move
            trace.append(round(move))

        return {'forward_tracks': trace, 'back_tracks': []}

    def _get_tracks3(self, distance):
        """
        根据偏移量获取移动轨迹3
        :param distance: 偏移量
        :return: 移动轨迹
        """
        track = []
        mid1 = round(distance * random.uniform(0.1, 0.2))
        mid2 = round(distance * random.uniform(0.65, 0.76))
        mid3 = round(distance * random.uniform(0.84, 0.88))
        # 设置初始位置、初始速度、时间间隔
        current, v, t = 0, 0, 0.2
        distance = round(distance)

        while current < distance:
            # 四段加速度
            if current < mid1:
                a = random.randint(10, 15)
            elif current < mid2:
                a = random.randint(30, 40)
            elif current < mid3:
                a = -70
            else:
                a = random.randint(-25, -18)

            # 初速度 v0
            v0 = v
            # 当前速度 v = v0 + at
            v = v0 + a * t
            v = v if v >= 0 else 0
            move = v0 * t + 1 / 2 * a * (t ** 2)
            move = round(move if move >= 0 else 1)
            # 当前位移
            current += move
            # 加入轨迹
            track.append(move)

        print("current={}, distance={}".format(current, distance))

        # 超出范围
        back_tracks = []
        out_range = distance - current
        if out_range < -8:
            sub = int(out_range + 8)
            back_tracks = [-1, sub, -3, -1, -1, -1, -1]
        elif out_range < -2:
            sub = int(out_range + 3)
            back_tracks = [-1, -1, sub]

        print("forward_tracks={}, back_tracks={}".format(track, back_tracks))
        return {'forward_tracks': track, 'back_tracks': back_tracks}

    def _get_tracks4(self, distance):
        """
        根据偏移量和手动操作模拟计算移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        tracks = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 时间间隔
        t = 0.2
        # 初始速度
        v = 0

        while current < distance:
            if current < mid:
                a = random.uniform(2, 5)
            else:
                a = -(random.uniform(12.5, 13.5))
            v0 = v
            v = v0 + a * t
            x = v0 * t + 1 / 2 * a * t * t
            current += x

            if 0.6 < current - distance < 1:
                x = x - 0.53
                tracks.append(round(x, 2))

            elif 1 < current - distance < 1.5:
                x = x - 1.4
                tracks.append(round(x, 2))
            elif 1.5 < current - distance < 3:
                x = x - 1.8
                tracks.append(round(x, 2))

            else:
                tracks.append(round(x, 2))

        print(sum(tracks))
        return {'forward_tracks': tracks, 'back_tracks': []}

    # ---- 拖拽轨迹计算 end ----


if __name__ == '__main__':
    c = JD_Slider()
    # c.main()

    # t1 = c.__get_tracks1(122)
    # print("t1 = {}".format(t1))
    #
    # t2 = c._get_tracks2(122)
    # print("t2 = {}".format(t2))
    #
    # t3 = c._get_tracks3(122)
    # print("t2 = {}".format(t3))

    # sf
    # a = "../static/sf/bg_1.jpeg"
    # b = "../static/sf/slider_1.png"

    # wy
    # index = 2
    # a = "../../static/wy/bg_{}.jpg".format(index)
    # b = "../../static/wy/slider_{}.png".format(index)

    # jd
    index = 8
    a = "../../static/jd/bg_{}.png".format(index)
    b = "../../static/jd/slider_{}.png".format(index)

    # 轮廓识别 筛选很难，要求图片的较高
    # res = c._match_profile(a)

    # 模板匹配。
    target = cv2.imread(a)
    template = cv2.imread(b)
    res = c._match_templet(target, template)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 图像完整匹配
    # img1 = Image.open("../static/slider/original_2.png")
    # img2 = Image.open("../static/slider/bg_2.png")
    # res = c.get_gap(img1, img2)
    print(res)
