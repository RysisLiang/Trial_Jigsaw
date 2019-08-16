#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import base64
import os
import re

import cv2
import numpy as np


def base64_to_cv2(base64_code):
    """
    base64转cv对象
    :param base64_code:
    :return:
    """
    img_data = base64.b64decode(base64_code)
    # 转换为np数组
    img_array = np.fromstring(img_data, np.uint8)
    # 转换成opencv可用格式
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
    return img


def base64_to_image(base64_code, img_name):
    """
    base64转image
    :param base64_code:
    :param img_name: 图片所在的path
    :return:
    """
    dir_path = re.sub(r'/[a-z]*.(png|jp(e)?g)$', '', img_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    img_data = base64.b64decode(base64_code)
    file = open(img_name, 'wb')
    file.write(img_data)
    file.close()
    return img_name