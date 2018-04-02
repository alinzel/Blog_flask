# -*- coding: utf-8 -*-
# @Time    : 18-3-28 下午4:03
# @Author  : Zwl
# @Email   : 944951481@qq.com
# @File    : 快速排序.py
# @Software: PyCharm

# arr = [3,9,1,5,2,6,8,4,7]
arr = [3, 1, 5]
def qsort(arr):
	# TODO 确定位置
	key = parition(arr)
	# TODO 切片
	l = qsort(arr[1:key+1])
	r = qsort(arr[key+1 :])
	print(l,r)
	l_key = parition(l)
	r_key = parition(r)
	return l +[arr[0]] + r

def parition(arr):
	list = [arr[0]]
	j = 0
	for i in arr[1 :]:
		if i < arr[0]:
			list.insert(j, i)
			j += 1
			# print(list)
		else:
			list.append(i)
	# print(list)
	# print(list.index(arr[0]))
	print(list)
	return list.index(arr[0])


# parition(arr)
print(arr)
print(qsort(arr))



