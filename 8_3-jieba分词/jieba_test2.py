import jieba
import jieba as jieba

test = "test.txt"
stop = "jieba_stop_words.txt"
#txt = open(test, encoding="utf-8").read()  #加载待处理数据文件
with open(test,encoding='utf-8') as f:
    txt = f.read()
with open(stop, encoding="utf-8")  as f:
    lines = f.readlines()
stopwords = [line.strip() for line in lines] #加载停用词
words = jieba.lcut(txt)     #分词
counts = {}                 #计数{word，frequency}
for word in words:
    if word not in stopwords:          #不在停用词表中
        if len(word) == 1:
            continue
        else:
            counts[word] = counts.get(word, 0) + 1

items = list(counts.items())
items.sort(key=lambda x: x[1], reverse=True)
for i in range(30):
    word, count = items[i]
    print("{:<10}{:>7}".format(word, count))
#txt.close()