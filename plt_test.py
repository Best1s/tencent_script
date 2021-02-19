# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['MSYH','SimHei']
from matplotlib import gridspec

a = list(range(10))
b = np.random.randint(1,100,10)
plt.figure(figsize=(7,7))
gs = gridspec.GridSpec(4,1)
ax1 = plt.subplot(gs[:3,0])
ax1.bar(a,b)
plt.xlabel('x Label')
plt.ylabel('y Label')
plt.title('title')

ax2 = plt.subplot(gs[3,0])
ax3 = plt.subplot(gs[4,0])
plt.axis('off')
rowLabels = ['第一行','第二行','第三行'] # 表格行名
cellText = [[1,2,3],[4,5,6],[7,8,9]] #表格每一行数据
table = plt.table(cellText=cellText, rowLabels=rowLabels, loc='center', cellLoc='center',rowLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10) #字体大小
table.scale(1, 1.5) #表格缩放
plt.show()