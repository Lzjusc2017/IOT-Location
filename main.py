import scipy.io as scio
import numpy as np
import math

'''
    AP坐标是m为单位
    数据坐标是0.01m
    将AP坐标*100 = cm
'''


'''
    获取num个坐标和num个RSSI的值
    @param path：mat文件路径
    @param num：num个数据
    @version:1.0
'''
def getLocationRssRandom(path,num):
    # 加载mat数据
    data = scio.loadmat(path)
    offline_location = data['offline_location']
    offline_rss = data['offline_rss']
    # 打乱数据
    state = np.random.get_state()
    np.random.shuffle(offline_location)
    np.random.set_state(state)
    np.random.shuffle(offline_rss)
    return offline_location[:num],offline_rss[:num]

'''
    计算当前节点跟锚节点的距离
    @:param AP:AP坐标
    @:param node_x:节点x坐标
    @:param node_y:节点y坐标
    @:return 距离列表
'''
def getDistance(AP,node_x,node_y):
    # 参考AP
    distances = []
    for i in AP:
        distance = (i[0]-node_x)*(i[0]-node_x) + (i[1]-node_y)*(i[1]-node_y)
        distance = format(distance ** 0.5, '.2f')
        distances.append(distance)
    return distances
    # print(distances)

'''
    根据RSSI求得估计坐标
    @:param AP:AP坐标
    @:param A 距离1m的信号强度
    @:param n 衰减因子
    @:param RSSI 得到的RSSI
    @:return 坐标[x,y]
'''
def getLocation(AP,A,n,Location,RSSI):
    # 公式是RSSI = -(A+10nlgd)
    #
    # 先求得一个距离数组
    distances = []
    # print('Location',Location)
    for i in RSSI:
        index = abs(i)-A
        index = index/(10*n)
        distance = 10**index
        distance = format(distance,'.2f')
        distances.append(distance)
    # 根据距离求使用最小二乘法列出算式
    A = []      # (k-1)x2
    b = []
    # print('AP',AP)
    # print('distances[0]',float(distances[0])*float(distances[0]))
    for i in range(len(AP)-1):
        m = []
        temp = 2*(AP[len(AP)-1][0]-AP[i][0])
        m.append(temp)
        temp = 2 * (AP[len(AP)-1][1] - AP[i][1])
        m.append(temp)
        A.append(m)
        # 距离
        tempB = float(distances[i])*float(distances[0]) - float(distances[len(AP)-1]) *float(distances[len(AP)-1])
        tempB = tempB + (AP[len(AP)-1][0])*(AP[len(AP)-1][0]) - (AP[i][0])*(AP[i][0])
        tempB = tempB + (AP[len(AP) - 1][1]) * (AP[len(AP) - 1][1]) - (AP[i][1]) * (AP[i][1])
        b.append(tempB)
    # 转成mat
    A = np.mat(A)   # (5,2)
    b = np.mat(b).T   # ()
    # print('A',A.shape)
    # print('b',b.shape)
    # 需要矩阵求逆
    # a = np.array([[1, 2], [3, 4]])  # 初始化一个非奇异矩阵(数组)
    # print(np.linalg.inv(a))  # 对应于MATLAB中 inv() 函数
    temp = np.linalg.inv((A.T * A))*A.T*b
    c = []
    temp = temp.tolist()
    c.append(temp[0][0])
    c.append(temp[1][0])
    # print('c',c)
    # print('temp',temp)
    return c

'''
    根据已知坐标跟估算坐标求得误差.
    @:param location 已知坐标 [x,y]
    @:param prelocation 预测坐标[x,y]
    @:return 误差float
'''
def getErr(prelocation,location):
    # print('location',location)
    # print('prelocation',prelocation)
    # print('----',location-prelocation)
    list = location - prelocation
    error = list[0]*list[0] + list[1]*list[1]
    return error


if __name__ == "__main__":

    # num : 希望获得的num个数据
    # AP  : AP坐标
    num = 10
    AP = [[100, 100], [1000, 100], [1900, 100], [100, 1400], [1000, 1400], [1900, 1400]]
    # 1. 随机选择num个坐标和rss值
    offline_location,offline_rss = getLocationRssRandom('./offline_data_random.mat',num)
    # 2.当前节点距离锚节点的距离
    # getDistance(AP,2,2)
    # 3. 根据RSSI的值，获得当前的预估坐标
    # offline_location[0] --> [293,1215]
    for i in range(1,50):
        for j in range(1,50):
            prelocation = getLocation(AP,i,j,offline_location[0],offline_rss[0])
            myerror = getErr(prelocation,offline_location[0])
            # print('myerror i j',myerror,i,j)

    # 只有误差，如何根据遗传算法求出最佳的A和n呢.
