#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from app.my_timer import my_timer
from app.slider.jd_test import JD_Slider

if __name__ == '__main__':
    # jd_test main
    jd = JD_Slider(url='https://union.jd.com/login', username='15140128843', pwd='')
    jd.main()

    # 定时器
    tm = my_timer(jd)
    tm.refresh(10)