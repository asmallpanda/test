import jieba
import jieba.posseg as pseg


content = "那些迷蒙的岁月与腐朽的往事，都在妖娆的时空中撕裂当日的面具，露出真颜。"

print(pseg.lcut(content))

# 精确模式
res = jieba.lcut(content, cut_all=False)
print(res)

# 全模式
res = jieba.lcut(content, cut_all=True)
print(res)

# 搜索引擎模式
res = jieba.lcut_for_search(content)
print(res)

# 繁体分词
content1 = "烦恼即是菩提，我暂且不提"
print(jieba.lcut(content1))

# 自定义分词字典
jieba.load_userdict("./jieba_user_dict.txt")
print(jieba.lcut("八一双鹿更名为八一南昌篮球队"))

print(jieba.lcut("深圳市莆田区华强职业技术学校"))
jieba.add_word("华强职业技术学校")
print(jieba.lcut("深圳市莆田区华强职业技术学校"))
