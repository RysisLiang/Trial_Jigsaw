#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import time
from datetime import datetime
from threading import Timer


class my_timer(object):

    def __init__(self, api):
        self.api = api

    def refresh(self, interval=30):
        print('TimeNow: %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        self.api.refresh()
        time.sleep(3)
        self.api.switch_iframe()

        if not self.api.is_login():
            self.api.main(is_open=False)

        t = Timer(interval, self.refresh, (interval,))
        t.start()
