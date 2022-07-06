#!/usr/bin/env python
# coding: utf-8

# In[11]:


import pandas as pd
from matplotlib.pyplot import *
from statistics import mean
# from AlphaTests import *
import sys
sys.path.insert(1,"../../")
from ExcelFormatter import ExcelFormatter


# In[12]:


class OVBacktest:
    def __init__(self,options,prices):
        # Load dataframes
        self.options = pd.read_csv(options)
        self.prices = pd.read_csv(prices)
        
        # Keep record of all trades
        self.trades = "Date,Expiry,Strike,Returns,OV,OV-Mean,Ratio\n"
        
        #Constructing the required features
        self.construct_features()
        try:
            #Get the batch number from the file name
            self.batch = options.split("-")[3].split(".")[0]
            stk = options.split("-")[0]
            if "PE" in options:
                self.result_name = stk+"-options-CE-"+self.batch+".csv"
            else:
                self.result_name = stk+"-options-PE-"+self.batch+".csv"
            
            self.df = pd.read_csv(self.result_name)
        except:
            pass
        
    def construct_features(self):
        self.options["Delta"] = pd.to_datetime(self.options["Expiry"]) - pd.to_datetime(self.options["Date"])
        self.options["Delta"] = self.options["Delta"].dt.days.astype('int16')
        self.options["OV"] = ((self.prices["Close"] - self.options["Strike Price"]) / self.options["Close"]) * self.options["Delta"]
        self.prices["Change"] = ((self.prices["Close"] - self.prices["Open"]) / self.prices["Open"])*100
        # options["Alpha-Prev"] = options.Alpha.shift(1)
        self.options["OV-Change"] = ((self.options["OV"] - self.options.OV.shift(1)) / self.options["OV"])*100
        self.options["OV-Mean"] = (self.options.OV.shift(1)+self.options.OV.shift(2)+self.options.OV.shift(3)) / 3
        self.options["Change"] = ((self.options["Close"] - self.options["Open"]) / self.options["Open"])*100
        self.options["Ratio"] = self.options["OV"] / self.options["OV-Mean"]
        self.options.fillna(0,inplace=True)
        
    def contruct_csv_data(self,data_list):
        return ",".join(data_list)+"\n"
        
    # Integrate new risk management strategies by chanding here
    def get_results(self,index):
        
        # Return change on the next day, buying the options the next day
        # and holding it for the entire day
        # return self.options["Change"][index+1]
        
        # Returns from buying the opposite option
        # df = pd.read_csv(self.result_name) [Execution time: 40s]
        df = self.df # [Execution time: 10s]
        if df["Open"][index+1] == 0:
            return 0
        df["Change"] = ((df["Close"] - df["Open"]) / df["Open"]) * 100
        return df["Change"][index+1]
    
    def find_net_returns(self,thresh,verbose=False,upper_threshold=-99):
        
        # Keep record of all trades for each run
        self.trades = "Date,Expiry,Strike,Returns,OV,OV-Mean,Ratio\n"
        total_returns = 0
        for index,rows in self.options.iterrows():
            ratio = rows["Ratio"]

            # Ignore options before 3 days of expiry or ratio is not valid
            if rows["Delta"] < 3 or ratio == 0:
                continue

            # Take all trades below the threshold and above upper_threshold
            if ratio <= thresh and ratio > upper_threshold:
                results = self.get_results(index)

                # Create a list with all necessary data field
                data = []
                data.append(str(rows["Date"]))
                data.append(str(rows["Expiry"]))
                data.append(str(rows["Strike Price"]))
                data.append(str(results))
                data.append(str(rows["OV"]))
                data.append(str(rows["OV-Mean"]))
                data.append(str(rows["Ratio"]))

                # Add it to trades
                self.trades += self.contruct_csv_data(data)
                
                # Add to overall returns
                total_returns += results
        if verbose:
            print("Returns: " + str(total_returns))
        return total_returns
        
    def find_optimal_threshold(self,upper_threshold=-99,toPrint=False):
        max_thresh = 3
        thresh = 0.1
        MAX_RETURNS = -9999
        OPT_THRESH = 0
        
        # Looping over all thresholds to find maximum profits
        while(thresh <= max_thresh):
            thresh += 0.01
            returns = self.find_net_returns(thresh,upper_threshold=upper_threshold)
            
            # Check is the returns for the current threshold are better than before
            # Update if true
            if returns > MAX_RETURNS:
                MAX_RETURNS = returns
                OPT_THRESH = thresh
            
        # Print results if needed
        if toPrint:
            print("Maximum Returns: " + str(MAX_RETURNS))
            print("Optimal Threshold: " + str(OPT_THRESH))
        
                    
            
    
    


# In[53]:


class Loader:
    def __init__(self,options,prices):
        # List of all options and prices files mapped to each other
        self.options = options
        
        # Create complimentary option pairs
        self.options_2 = []
        if "PE" in options[0]:
            for x in options:
                self.options_2.append(x.replace("PE","CE"))
        elif "CE" in options[0]:
             for x in options:
                self.options_2.append(x.replace("CE","PE"))
        
        self.prices = prices
        self.backtests = []
        for i in range(0,len(options)):
            self.backtests.append(OVBacktest(options[i],prices[i]))
    
    def find_net_returns(self,thresh,upper_threshold=-99,verbose=False):
        # Loop over all OV models
        total_result = 0
        for ov in self.backtests:
            result = ov.find_net_returns(thresh,upper_threshold=upper_threshold,verbose=verbose)
            total_result += result
        return total_result
    
    # Creates a result file with trades, options chain, prices
    def generate_results(self,thresh,upper_threshold=-99,verbose=False):
        result_dfs = []
        for ov in self.backtests:
            ov.find_net_returns(thresh,upper_threshold=upper_threshold)
            
            # Write trades data for each backtest to a temporary file
            with open("tmp-data.csv","w") as f:
                f.write(ov.trades)
            
            # Read trades from file and add it to dfs
            result_dfs.append(pd.read_csv("tmp-data.csv",index_col=False))
        
        # Concatenate all results from all dataframes
        results_df = pd.concat(result_dfs)
        
        # Create options chain
        dfs = []
        for x in self.options:
            tmp = pd.read_csv(x,index_col=False)
            dfs.append(tmp)
        
#         options_1_df = pd.concat(dfs)
        df2 = pd.concat(dfs)
        
        dfs = []
        for x in self.options_2:
            tmp = pd.read_csv(x,index_col=False)
            dfs.append(tmp)
            
#         options_2_df = pd.concat(dfs)
        df3 = pd.concat(dfs)
#         print(df3.tail())
        
        # Create prices
        dfs = []
        for x in self.prices:
            tmp = pd.read_csv(x,index_col=False)
            dfs.append(tmp)
        
        prices_df = pd.concat(dfs)
        
        # Construct features
#         df2 = options_1_df
#         df3 = options_2_df
        
#         prices_df = prices_df[~prices_df.index.duplicated()]
#         df2 = df2[~df2.index.duplicated()]
#         df3 = df3[~df3.index.duplicated()]
        
        # Change index column to prevent clashes
        prices_df.set_index('Date', inplace=True)
        df2.set_index('Date', inplace=True)
        df3.set_index('Date', inplace=True)
        
        df2["Alpha"] = (prices_df["Close"] - df2["Strike Price"]) / df2["Close"]
        df2["Alpha-Change"] = ((df2["Alpha"] - df2.Alpha.shift(1)) / df2["Alpha"])*100
        df2["Alpha-Mean"] = (df2.Alpha.shift(1)+df2.Alpha.shift(2)+df2.Alpha.shift(3)) / 3
        df2["Change"] = ((df2["Close"] - df2["Open"]) / df2["Open"])*100
        df2["Ratio"] = df2["Alpha"] / df2["Alpha-Mean"]
        
        
        df3["Alpha"] = (prices_df["Close"] - df3["Strike Price"]) / df3["Close"]
        df3["Alpha-Change"] = ((df3["Alpha"] - df3.Alpha.shift(1)) / df3["Alpha"])*100
        df3["Alpha-Mean"] = (df3.Alpha.shift(1)+df3.Alpha.shift(2)+df3.Alpha.shift(3)) / 3
        df3["Change"] = ((df3["Close"] - df3["Open"]) / df3["Open"])*100
        df3["Ratio"] = df3["Alpha"] / df3["Alpha-Mean"]
        
        prices_df["Change"] = ((prices_df["Close"] - prices_df["Open"]) / prices_df["Close"])*100
        
        writer = pd.ExcelWriter("results.xlsx",engine="xlsxwriter")
        
        results_df.to_excel(writer,sheet_name="trades")
        df2.to_excel(writer,sheet_name="puts chain")
        df3.to_excel(writer,sheet_name="calls chain")
        prices_df.to_excel(writer,sheet_name="prices")
        
        writer.save()
        
        # Properly format excel sheet
        clean = ExcelFormatter("results.xlsx")
        clean.save()
        
        
        
    def plot_scatter(self):
        pass
    
    def find_optimal_threshold(self,upper_threshold=-99,verbose=False):
        start_time = time.time()
        OPT_THRESH = 0
        MAX_RETURNS = -999
        
        max_thresh = 2
        thresh = 0.01
        
        while(thresh <= max_thresh):
            thresh += 0.01
            result = self.find_net_returns(thresh,upper_threshold=upper_threshold)
            
            if result > MAX_RETURNS:
                MAX_RETURNS = result
                OPT_THRESH = thresh
        
        if verbose:
            print("Max Returns: " + str(MAX_RETURNS))
            print("Optimal Threshold: " + str(OPT_THRESH))
            print("Time Taken: " + str(time.time() - start_time) + " seconds")
        
        return OPT_THRESH
        


# In[ ]:




