# Reference
# Gantt charts with Python’s Matplotlib
# https://towardsdatascience.com/gantt-charts-with-pythons-matplotlib-395b7af72d72


import toml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Union
import os

class GanttHelper:

    def __init__(self, src: str, dir: Union[str, bool]=False, fname: Union[str, bool]=False, sort_by_start: bool=True, x_ticks_num: int=10, fig_size: tuple=(20, 5)) -> None:
        """_summary_

        Parameters
        ----------
        src : str
            Toml file name, without filename extension
        dir : Union[str, bool], optional
            Ouput file directory, by default False
        fname : Union[str, bool], optional
            Ouput file name, by default False
        sort_by_start : bool, optional
            Sort data by their start date, by default True
        x_ticks_num : int, optional
            How many x ticks you want to display, by default 10
        fig_size : tuple, optional
            Figure size, by default (20, 5)
        
        """
        self.src = src
        self.dir = dir
        self.fname = fname
        self.sort_by_start = sort_by_start
        self.x_ticks_num = x_ticks_num
        self.fig_size = fig_size
    

    def plot(self) -> None:
        """_summary_

        Example:
        -------
        ```python
        from gantt_helper import GanttHelper

        gh = GanttHelper('gantt', dir='Images', fname='Gannt', sort_by_start=True, x_ticks_num=10, fig_size=(20, 5))
        gh.plot()
        ```
        """
        df, x_ticks_num = self.cleaned_dataframe_data, self.x_ticks_num

        plt.style.use('fivethirtyeight')
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']

        fig, ax = plt.subplots(1, figsize=self.fig_size)

        ax.barh(df.task, df.current_num, left=df.start_num, color=df.color)
        ax.barh(df.task, df.start_end, left=df.start_num, color=df.color, alpha=0.5)

        for _, row in df.iterrows():
            ax.text(row.end_num+df.start_end.max()*0.01, row.uid, f"{int(row.complete)}%", va='center')

        step = (df.end_num.max()-df.start_num.min())/x_ticks_num

        ax.set_xticks(np.arange(0, df.end_num.max(), step))
        ax.set_xticklabels(pd.date_range(df.start.min(), df.end.max(), x_ticks_num).strftime("%Y-%m-%d"), fontsize=10)
        
        plt.title(f'{self.fname}')
        
        if self.fname:
            plt.savefig(self.output_path, bbox_inches='tight')

    @property
    def output_path(self):
        if self.dir:
            os.makedirs(self.dir, exist_ok=True)
            output_path = f'{self.dir}/{self.fname}.png'
        else:
            output_path = f'{self.fname}.png'
        
        return output_path

    @property
    def toml_data(self):
        """_summary_
    
        !!! note

            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et euismod
            nulla. Curabitur feugiat, tortor non consequat finibus, justo purus auctor
            massa, nec semper lorem quam in massa.

        Format:
        -------
        ```toml
        [1] 
        task = 'A'
        start = 2018-06-27
        end = 2018-06-22
        complete = 55
        ```
        """
        return toml.load(f'{self.src}.toml')
    

    @property
    def raw_dataframe_data(self):
        df = pd.DataFrame(self.toml_data.values())
        if self.sort_by_start:
            df = df.sort_values(by='start')
            df = df.reset_index(drop=True)
        
        return df
    

    @property
    def cleaned_dataframe_data(self):

        df = self.raw_dataframe_data

        def unique_task_id(x):
            l = df.task.unique().tolist()
            return l.index(x)

        df['start_num'] = df.start - df.start.min()
        df['start_end'] = df.end - df.start

        df['start_num'] = df.start_num.astype('timedelta64[D]').astype(int)
        df['start_end'] = df.start_end.astype('timedelta64[D]').astype(int)

        df['end_num'] = df.start_num + df.start_end

        df['current_num'] = (df.start_end* df.complete/100)
        df['color'] = df.complete.apply(GanttHelper.to_color)
        df['uid'] = df.task.apply(unique_task_id)

        return df


    @staticmethod
    def to_color(x):
        if x == 100:
            return (0.3, 0.3, 0.3, 1)
        
        elif x < 100 and x > 60:
            return (0, 0.5, 0.3, x/100)
        
        else:
            return (0.7, 0, 0, 0.8)



