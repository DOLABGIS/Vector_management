import psycopg2
from flask import Flask, jsonify, abort, make_response, request
import json
from shapely.geometry import LineString,MultiLineString
from shapely import wkt

import numpy as np
import tkinter
from tkinter import filedialog

app = Flask(__name__)

# connect to test db
conn = psycopg2.connect(database="test", user="postgres",
                        password="dogis2021", host="49.232.75.144", port="5432")

print("Opened database successfully")
cur = conn.cursor()

#根据两点坐标计算距离
def caldis(x1,y1,x2,y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

#输入三角形三个顶点，计算外接圆圆心及半径
def calcenter(x1,y1,x2,y2,x3,y3):
    y1=-y1  #计算公式是根据平面直角坐标推算的，原点在左下角，但是计算机屏幕坐标原点在右上角，所以计算式y坐标取负
    y2=-y2
    y3=-y3
    if (y1 != y3 and y1 != y2 and y2 != y3): #判断是否有y坐标相等，即三角形某边斜率为0的情况，避免出现坟分母为0的错误
        if(((x3-x1)/(y3-y1))-((x2-x1)/(y2-y1)))==0:
            x2=x2+1
        x=(((y1+y3)/2)+((x1+x3)/2)*((x3-x1)/(y3-y1))-((y1+y2)/2)-((x1+x2)/2)*((x2-x1)/(y2-y1)))/(((x3-x1)/(y3-y1))-((x2-x1)/(y2-y1)))
        y=-((x3-x1)/(y3-y1))*x+((y1+y3)/2)+(((x1+x3)/2)*((x3-x1)/(y3-y1)))
        return (x, -y, caldis(x, y, x1, y1))
    elif (y1 == y3 and y1 != y2 and y2 != y3):#若存在斜率为0的边则计算可简化
        x=(x1+x3)/2
        y=-((x2-x1)/(y2-y1))*x+((y1+y2)/2)+((x2-x1)/(y2-y1))*((x1+x2)/2)
        return (x, -y, caldis(x, y, x1, y1)) #返回值为元组（圆心横坐标x，圆心纵坐标y，外接圆半径r），计算出来的y值要返回屏幕坐标所以再次取负
    elif (y1 != y3 and y1 == y2 and y2 != y3):
        x = (x1 + x2) / 2
        y = -((x3 - x1) / (y3 - y1)) * x + ((y1 + y3) / 2) + ((x3 - x1) / (y3 - y1)) * ((x1 + x3) / 2)
        return (x, -y, caldis(x, y, x1, y1))
    elif (y1 != y3 and y1 != y2 and y2 == y3):
        x = (x3 + x2) / 2
        y = -((x3 - x1) / (y3 - y1)) * x + ((y1 + y3) / 2) + ((x3 - x1) / (y3 - y1)) * ((x1 + x3) / 2)
        return (x, -y, caldis(x, y, x1, y1))
    else:
        return None

def getfile(file_name):  #读入坐标存入pointlist列表
    query = "SELECT ST_AsEWKT(geom) from "+file_name+' limit 100;'
    cur.execute(query)
    geoms = cur.fetchall()
    conn.commit()
    pointlist=[]
    for pwkt in geoms:
        pwkt = str(pwkt)
        lon_lat = pwkt[pwkt.index('POINT(')+6:-4].split(" ")
        pointlist.append(lon_lat)
    
    return pointlist

def drawTIN_shengzhang():
    global pointlist,linelist
    j = 1
    k = 0
    mindis = ((float(pointlist[0][0]) - float(pointlist[1][0])) ** 2 + (float(pointlist[0][1]) - float(pointlist[1][1])) ** 2) ** 0.5
    x = len(pointlist)
    for i in range(1, x):
        dis = ((float(pointlist[0][0]) - float(pointlist[i][0])) ** 2 + (float(pointlist[0][1]) - float(pointlist[i][1])) ** 2) ** 0.5
        if dis < mindis:
            mindis = dis
            j = i
    linelist.append((k,j)) #首先计算出距起始点（点号为0）距离最短的点，以这两点的连线作为基线开始生长
    shengzhangjixian(k,j)

def shengzhangjixian(i,j): #根据某一基线开始生长的函数
    global pointlist,linelist
    x = len(pointlist)
    for k in range(0,x): #遍历没一个点，判断是否与基线构成D三角形
        n = 0 #n用于统计外接圆内的点数
        if ((k,i) not in linelist) and ((i,k) not in linelist) and ((j,k) not in linelist) and ((k,j) not in linelist):
            for y in range(0,x): #遍历每一个点，判断
                if y==i or y==j or y==k:
                    continue
                if(calcenter(float(pointlist[i][0]),float(pointlist[i][1]),float(pointlist[j][0]),float(pointlist[j][1]),float(pointlist[k][0]),float(pointlist[k][1]))==None):
                    continue
                else:
                    xyr=calcenter(float(pointlist[i][0]),float(pointlist[i][1]),float(pointlist[j][0]),float(pointlist[j][1]),float(pointlist[k][0]),float(pointlist[k][1]))
                if caldis(xyr[0],xyr[1],float(pointlist[y][0]),float(pointlist[y][1])) < xyr[2]: #判断点是否在外接圆内
                    n=n+1
                else:
                    continue
        else:continue

        if n == 0: #判断是否为D三角形
            linelist.append((k,i)) #将新生成的边的端点号加入线列表
            shengzhangjixian(k,i) #以生成的新边作为基线，迭代计算
            linelist.append((k,j))
            shengzhangjixian(k,j)
        else:continue



def point2wkt():
    global linelist
    geomlist=[]
    for pair in linelist:
        lwkt = "LINESTRING("+ pointlist[pair[0]][0] + " " +pointlist[pair[0]][1] +","+pointlist[pair[1]][0] + " " +pointlist[pair[1]][1]+")"
        lgeom = wkt.loads(lwkt)
        geomlist.append(lgeom)
    AllLine = MultiLineString(geomlist)
    linejson = AllLine.__geo_interface__
    return linejson

def getTIN1(file_name):
    global pointlist,linelist
    pointlist,linelist=[],[]
    pointlist=getfile(file_name)
    drawTIN_shengzhang()
    linewkt = point2wkt()
    return linewkt

if __name__ == '__main__':
    # MyTIN=getTIN1('poi')
    file_name ='qwer'
    fields=[]
    fields.append('gid')
    create_str = 'CREATE TABLE '+file_name+"("
    for f in fields:
        type_str=str(type(f))
        create_str = create_str+f+" "+type_str[type_str.index('class')+7:-2]+", "
    create_str = create_str+"PRIMARY KEY("+fields[0]+"));"
    print(1111)