#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import random


def get_random_float(min, max, digits=4):
    """

    :param min:
    :param max:
    :param digits:
    :return:
    """
    return round(random.uniform(min, max), digits)


def get_random_int(min, max):
    """

    :param min:
    :param max:
    :return:
    """
    return round(random.randint(min, max))