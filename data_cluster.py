# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :data_cluster.py
# @Time      :2023/3/17 11:27
# @Author    :Boris_zhang
import sys
import pandas as pd
import numpy as np
import jieba
import warnings
import string

warnings.filterwarnings("ignore")


class DataCluster:
    def __init__(self):
        # jieba添加字典
        jieba.load_userdict("lib/jiebaDict.txt")

    def SimSeq2set(self,list1, list2, columns_indexs, isjieba):

        def split_string(s, isjieba):
            # 去除标点符号
            exclude = set(string.punctuation)
            s = ''.join(ch for ch in s if ch not in exclude)
            # 按词拆分成列表
            if isjieba:
                try:
                    return jieba.lcut(s)
                except:
                    return []
            # 按单个字符拆成列表
            return list(s)

        def jaccard_similarity(s1, s2):
            s1, s2 = set(s1), set(s2)
            s3 = s1 & s2
            s4 = s1 | s2
            try:
                score = len(s3) / len(s4)
                # score保留两位小数
                score = round(score, 2)
            except:
                score = 0.
            return score

        # 取出目标列的部分
        seq1 = split_string(''.join([str(list1[idx]) for idx in columns_indexs if list1[idx] != None]), isjieba)
        seq2 = split_string(''.join([str(list2[idx]) for idx in columns_indexs if list2[idx] != None]), isjieba)
        # print(seq1, '\n', seq2)
        sim_score = jaccard_similarity(seq1, seq2)
        return sim_score

    # 展示进度
    def progress_bar(self, processed_rows, total_rows):
        percentage = round(float(processed_rows / total_rows * 100), 1)
        bar_length = int(percentage) // 2
        print("\r进度: {}% ({}/{}) ".format(percentage, processed_rows, total_rows), "▓" * bar_length, end="")
        sys.stdout.flush()

    def find_indexes(self, lst, args):
        indexes = []
        for s in args:
            try:
                index = lst.index(s)
                indexes.append(index)
            except:
                raise ValueError("输入字段参数有问题，请检查！")
        return indexes

    def scan_list(self, df, output_path, columns_name, threshold=0.7, isjieba=False):
        columns_list = df.columns.tolist()
        # 提取所对应查重列的在行列表中索引位置
        columns_indexs = self.find_indexes(columns_list, columns_name)
        df_list = df.values.tolist()
        total_len = len(df_list)
        # 初始化一个簇聚类空列表
        cluster_list = []
        clusterId = 0
        while df_list:
            start = 0
            # 添加簇首元素
            # 添加簇首元素
            new_cluster_first_element = df_list[start].copy()
            # 添加簇首元素的簇ID
            new_cluster_first_element.append(clusterId)
            # 添加簇首元素的相似度
            new_cluster_first_element.append(1.00)
            # 添加簇首元素到簇聚类列表
            cluster_list.append(new_cluster_first_element)
            # 初始化记录删除元素索引的列表
            del_index_list = [start]
            # clusterId变量向下兼容
            clusterId = clusterId
            for i in range(1, len(df_list)):

                sim_score = self.SimSeq2set(df_list[start], df_list[i], columns_indexs, isjieba)
                if sim_score >= float(threshold):
                    # 如果相似度大于0.5，则添加到簇中
                    new_cluster_element = df_list[i].copy()
                    # 添加簇元素的簇ID
                    new_cluster_element.append(clusterId)
                    # 添加簇元素的相似度
                    new_cluster_element.append(sim_score)
                    cluster_list.append(new_cluster_element)
                    # 将当前元素的索引添加到删除列表中
                    del_index_list.append(i)

            # 删除已经添加到簇中的元素
            df_list = np.delete(df_list, del_index_list, axis=0).tolist()

            now_len = len(df_list)
            # 展示进度
            self.progress_bar(total_len - now_len, total_len)
            # 簇ID加1
            clusterId += 1

        cluster_list_df = pd.DataFrame(cluster_list, columns=columns_list + ['clusterId', 'sim_score'])

        # 增加一列统计clusterId的数量
        cluster_list_df["clusterId_count"] = cluster_list_df["clusterId"].map(
            cluster_list_df["clusterId"].value_counts())
        # 按照clusterId_count降序排列
        cluster_list_df = cluster_list_df.sort_values(by=["clusterId_count", "clusterId"], ascending=False)
        # clusterId 重新排序
        clusterId = cluster_list_df["clusterId"].tolist()

        # 重排clusterId从0开始
        new_clusterId = []
        n = 0
        for i in range(len(clusterId)):
            if i == 0:
                new_clusterId.append(n)
            else:
                if clusterId[i] != clusterId[i - 1]:
                    n += 1
                    new_clusterId.append(n)
                else:
                    new_clusterId.append(n)
        cluster_list_df["clusterId"] = new_clusterId

        cluster_list_df.to_excel(output_path, index=False)


if __name__ == "__main__":
    df = pd.read_excel('processed_data.xlsx', sheet_name='Sheet1')
    DataCluster = DataCluster()
    DataCluster.scan_list(df, 'output_path.xlsx', ['ent_name', 'ent_address'], threshold=0.7)
