import csv

from sklearn.model_selection import train_test_split

# 假设X是特征矩阵，y是对应的标签向量
X = ...  # 你的特征数据
y = ...  # 相应的目标变量或标签

# 划分数据集，test_size参数设置为40%

X = []
y = []
with open('intent_recognize.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        X.append(row[0])
        y.append(row[1])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

for i in range(len(X_train)):
    print(y_train[i] + ' ' + X_train[i])

print("-----")

for i in range(len(X_test)):
    print(y_test[i] + ' ' + X_test[i])