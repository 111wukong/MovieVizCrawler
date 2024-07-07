# -*-codeing = utf-8 -*-
# @Time:2022/7/11 14:59
# @Author:wukong
# @File:testCloud.py
# @Software:PyCharm
import jieba                                 #分词
from matplotlib import pyplot as plt         #绘图，数据可视化
from wordcloud import WordCloud              #词云
from PIL import  Image                       #图片处理
import  numpy as np                          #矩阵运算
import sqlite3                               #数据库

con = sqlite3.connect('movie.db')
cur = con.cursor()
sql = 'select instroduction from movie250'
data = cur.execute(sql)
text = " "
for item in data:
    #text = text + item[0]
    print(item[0])
