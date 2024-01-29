import networkx as nx
# import matplotlib.pyplot as plt
# plt.rcParams['font.sans-serif']=['simsun']   # 设置中文字体
#

fh = open("knowledge_graph/test.adjlist", "rb")
G = nx.read_adjlist(fh)


aggregation_dict = {}
filter_word = ['合计', '平均', '最大值', '最小值']

f1 = open('knowledge_graph/origin.txt', 'r', encoding='utf-8')
for line in f1.readlines():
    ob, me = line.strip().split('-')
    for word in filter_word:
        if word in me:
            me = me.replace(word, "")
            if me not in aggregation_dict.keys():
                aggregation_dict[me] = [word]
            else:
                if word not in aggregation_dict[me]:
                    aggregation_dict[me].append(word)


def get_target_node(node_name):
    result = list(G.adj[node_name])
    print("--知识图谱获得的目标节点：", result)
    return result


def get_target_aggregation(node_name):
    if node_name not in aggregation_dict.keys():
        return []
    else:
        return aggregation_dict[node_name]



# nx.draw(G, with_labels=True)
# plt.show()