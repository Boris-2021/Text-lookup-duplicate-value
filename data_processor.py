# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :data_processor.py
# @Time      :2023/3/15 15:40
# @Author    :Boris_zhang
import pandas as pd

# 设置pandas不省略中间内容
# pd.set_option('display.max_columns', None)


class DataProcessor:
    def __init__(self, file_path, sheet_name=None):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.df = None
        self.header_row = None
        self.cols_to_drop = []

    def process(self):
        # 读取Excel文件
        self.df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)

        # 自动检索表头所在行
        min_unnamed_count = float('inf')
        for i in range(min(len(self.df), 10)):
            row = self.df.iloc[i]
            if all(type(col) == str or pd.isna(col) for col in row):
                unnamed_count = len([col for col in row if 'Unnamed:' in str(col) or pd.isna(col)])
                if unnamed_count < min_unnamed_count:
                    self.header_row = i + 1
                    min_unnamed_count = unnamed_count

        # 使用表头所在行作为表头
        if self.header_row is not None:
            self.df = pd.read_excel(self.file_path, sheet_name=self.sheet_name, header=self.header_row)

        # 删除列名为空或者包含'Unnamed'的列
        for col in self.df.columns:
            if col == '' or 'Unnamed' in col:
                self.df = self.df.drop(col, axis=1)

        # 自动检索出从0或者1开始自增的序号列去掉
        for col in self.df.columns:
            if self.df[col].dtype == 'int64':
                if self.df[col].is_monotonic_increasing:
                    self.cols_to_drop.append(col)
        self.df = self.df.drop(self.cols_to_drop, axis=1)
        return self.df

        # print(self.df)
    def save_processed_data(self, file_path):
        if self.df is None:
            raise Exception("需要先执行数据处理; you need processor.process() before save to file !")
        self.df.to_excel(file_path, index=False)


# 使用示例
if __name__ == '__main__':
    processor = DataProcessor('给张博涵.xlsx', sheet_name='Sheet3')
    processor.process()
    processor.save_processed_data('processed_data.xlsx')


