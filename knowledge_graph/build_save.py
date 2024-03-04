import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif']=['simsun']   # 设置中文字体
plt.figure(figsize=(20, 16))

object_list = set()
measurement_list = set()
edge_list = []
filter_word = ['合计', '平均', '最大值', '最小值']

f1 = open('origin.txt', 'r', encoding='utf-8')
for line in f1.readlines():
    ob, me = line.strip().split('-')
    for word in filter_word:
        if word in me:
            me = me.replace(word, "")
            break
    object_list.add(ob)
    measurement_list.add(me)
    edge_list.append((ob, me, {'weight': 1}))

print(object_list)
print(measurement_list)

#
# object_list = ['居民特殊病', '职工特殊病', '职工特殊病']
# measurement_list = ['统筹基金', '大病保险',  '公务员补贴', '大额医疗补助']
#
# # 创建节点
G = nx.Graph()
G.add_nodes_from(object_list, type_name='search_object')
G.add_nodes_from(measurement_list, type_name='search_measurement')
#
# # 创建边
# edge_list = [('居民特殊病', '统筹基金', {'weight': 1}), ('居民特殊病', '大病保险', {'weight': 1}), ('居民特殊病', '公务员补贴', {'weight': 1}),
#              ('职工特殊病', '统筹基金', {'weight': 1}), ('职工特殊病', '大病保险', {'weight': 1}), ('职工特殊病', '大额医疗补助', {'weight': 1}), ]
G.add_edges_from(edge_list)
#
# # 节点染色(按照创建顺序)
color_map = []
color_map += ['red'] * len(object_list)
color_map += ['green'] * len(measurement_list)
#
# fh = open("test.adjlist", "wb")
# nx.write_adjlist(G, fh)
# #
# # print(G.nodes.data())
# nx.draw(G, with_labels=True, font_size=10, node_color=color_map)
# plt.show()