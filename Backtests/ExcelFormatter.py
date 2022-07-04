#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[9]:


class ExcelFormatter:
    def __init__(self,excel_file):
        self.file = excel_file
        df = pd.read_excel(excel_file,sheet_name=None,engine="openpyxl")
        self.sheets = df.keys()
        self.writer = pd.ExcelWriter(excel_file,engine="xlsxwriter")
        
        #Populates writer with sheet data
        self.load_writer()
        
        self.workbook = self.writer.book
        
        self.init_formats()
        
        #Center align all text
        for sheet in df.keys():
            #Center align everything
            worksheet = self.writer.sheets[sheet]
            worksheet.set_column("A:Z",5,self.formats["align-center"])
            
            #Freeze top row
            worksheet.freeze_panes(1,0)
            
            #Autofit column width
            tmp_df = pd.read_excel(excel_file,sheet_name=sheet,engine="openpyxl")
            for column in tmp_df:
                column_length = max(tmp_df[column].astype(str).map(len).max(), len(column))
                col_idx = tmp_df.columns.get_loc(column)
                self.writer.sheets[sheet].set_column(col_idx, col_idx, column_length)
            
    def highlight_pnl(self,column,sheet):
        formatting = {
            "type":"cell",
            "criteria":"greater than",
            "value": 19.5,
            "format":self.formats["green_bg"]
        }
        
        worksheet = self.writer.sheets[sheet]
        worksheet.conditional_format(column,formatting)
        
        formatting = {
            "type":"cell",
            "criteria":"less than",
            "value": -10,
            "format":self.formats["red_bg"]
        }
        
        worksheet.conditional_format(column,formatting)
    
    def init_formats(self):
        self.formats = {}
        self.formats["red_bg"] = self.workbook.add_format({'bg_color':   '#FFC7CE',
                               'font_color': '#9C0006'})
        
        format_align = self.workbook.add_format()
        format_align.set_align('center')
        format_align.set_align('vcenter')
        self.formats["align-center"] = format_align
        
        self.formats["green_bg"] = self.workbook.add_format({'bg_color':   '#C6EFCE',
                               'font_color': '#006100'})
        
    def load_writer(self):
        for sheet in self.sheets:
            df = pd.read_excel(self.file,sheet_name=sheet,engine="openpyxl")
            df.replace(np.inf,0,inplace=True)
            df.fillna(0,inplace=True)
#             df = df.loc[~(df==0).all(axis=1)]
#             df = df[df["Ratio"] != 0]
            df.to_excel(self.writer,sheet_name=sheet)
            
    
    def save(self):
        self.writer.save()
        
        


# In[13]:


# fmt = ExcelFormatter("tmp-new.xlsx")


# In[14]:


# fmt.highlight_pnl("AB1:AB255","data")


# In[15]:


# fmt.save()


# In[ ]:




