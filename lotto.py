# -*- coding: utf-8 -*-
"""
Created on Tue May 11 00:20:30 2021

@author: kasia
"""

import random as rd
from app_data import App_data

def check():
    num = rd.randint(10000,100000)
    digitSum = 0
    while (num > 0):
        rem = num%10
        digitSum = digitSum + rem
        num = num // 10

    if(digitSum in range(1,4)):
        return 100
    elif(digitSum in range(5,15)):
        return 20  
    elif(digitSum in range(32,42)):
        return 20
    elif(digitSum in range(42,45)):
        return 100
    else:
        return -5.00