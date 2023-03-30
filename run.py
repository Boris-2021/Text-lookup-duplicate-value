# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :run.py.py
# @Time      :2023/3/17 15:17
# @Author    :Boris_zhang

import yaml
from data_processor import DataProcessor
from data_cluster import DataCluster

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

processor_config = config['data_processor']
cluster_config = config['data_cluster']


# 使用DataProcessor处理数据
print(rf"......【{processor_config['input_file']}】数据进行扫描，统一格式处理......")
processor = DataProcessor(processor_config['input_file'], sheet_name=processor_config['sheet_name'])
df = processor.process()

if 'output_file' in processor_config:
    processor.save_processed_data(processor_config['output_file'])
print(r"------扫描统一格式处理完成------")
# 使用DataCluster进行数据聚类
print(r"------加载分词词典------")
DataCluster = DataCluster()
print(rf"-------开始相似行的聚合,比较{cluster_config['columns']}字段的信息的一致性。（相似度阈值{cluster_config['threshold']}）------")
print(rf"-------分词模式是否开启：{cluster_config['isjieba']}--------")
DataCluster.scan_list(df, cluster_config['output_file'], cluster_config['columns'],
                      threshold=cluster_config['threshold'], isjieba=cluster_config['isjieba'])
