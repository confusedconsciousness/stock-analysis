import streamlit as slt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from markdown import markdown as md
import plotly.express as px

@slt.cache(persist=True)
def load_data():
    """
    load the data from the csv file and returns a dataframe

    Uses a decorator so to prevent loading the dataset multiple
    times when a slight change is made to the app to save
    the computation

    """
    df = pd.read_csv('stocks.csv')
    return df


def load_text(filename):
    """
    Gives the description about the dataset that we are using
    """
    with open(filename, 'r') as f:
        return f.read()

def get_names(df):
    return df.Name.unique()


def plot_graphs(df, mask, options):
    labels = []
    values = []
    dates = []
    metrics = []
    length = len(df[mask])

    if "open" in options:
        value = df[mask]['open'].values
        for v in value:
            values.append(v)
        date = df[mask]['date'].values
        for d in date:
            dates.append(d)
        for _ in range(length):
            metrics.append('Open')
        #slt.write("Open: {}".format(len(df[mask]['open'])))
        labels.append("Open")
    
    
    if "close" in options:
        value = df[mask]['close'].values
        for v in value:
            values.append(v)
        date = df[mask]['date'].values
        for d in date:
            dates.append(d)
        for _ in range(length):
            metrics.append('Close')
        labels.append("Close")
    
    if "high" in options:
        value = df[mask]['high'].values
        for v in value:
            values.append(v)
        date = df[mask]['date'].values
        for d in date:
            dates.append(d)
        for _ in range(length):
            metrics.append('High')
        labels.append("High")

    if "low" in options:
        value = df[mask]['low'].values
        for v in value:
            values.append(v)
        date = df[mask]['date'].values
        for d in date:
            dates.append(d)
        for _ in range(length):
            metrics.append('Low')
        labels.append("Low")
    
    modified_df = {"Date":dates, "Attributes":values, "Metric":metrics}
    fig = px.line(modified_df, x='Date', y='Attributes', color='Metric')
    slt.plotly_chart(fig)
    


def cplot(df_fc, df_sc, mask, option, cname):
    values = []
    dates = []
    names = []

    values_fc = df_fc[mask][option].values
    values_sc = df_sc[mask][option].values

    for v in values_fc:
        values.append(v)
        names.append(cname[0])
    
    for v in values_sc:
        values.append(v)
        names.append(cname[1])

    for d in df_fc[mask]['date'].values:
        dates.append(d)
    
    for d in df_sc[mask]['date'].values:
        dates.append(d)
    
    modified_df = {'Date': dates, 'In Dollars': values, 'Name': names}
    fig = px.line(modified_df, x='Date', y='In Dollars', color='Name', title=option)
    slt.plotly_chart(fig)


def compare_graphs(df_fc, df_sc, mask, options, cname):
    
    if "open" in options:
        cplot(df_fc, df_sc, mask, 'open', cname)
    if "close" in options:
        cplot(df_fc, df_sc, mask, 'close', cname)
    if "high" in options:
        cplot(df_fc, df_sc, mask, 'high', cname)
    if "low" in options:
        cplot(df_fc, df_sc, mask, 'low', cname)
    if "volume" in options:
        cplot(df_fc, df_sc, mask, 'volume', cname)




def main():
    slt.title("Stock Market Analysis")
    df = load_data()
    slt.markdown(load_text("file.txt"))
    slt.write(df.sample(20))
    # we need to find the list of all companies
    names = get_names(df)
    names = tuple(names)
    slt.subheader("Please select your Phase")
    phase = slt.radio("Phase", (("Compare", "Explore")))
    if phase == "Explore":
        slt.subheader("Explore")
        slt.markdown("In this phase we will look at differnt metrics such as 'Low', 'High', 'Open', 'Close' and 'Volume' of the company that you selected")

        slt.subheader("Choose your Company name")
        cname = slt.selectbox("Companies available", names, key='cname')
        # extract the exclusive company data from the data frame using cname as the filter
        df = df[df.Name == cname]
        slt.markdown("Following is the first 10 entries corresponding to {}".format(cname))
        slt.write(df.head(50))
        
        date = df['date']
        
        opt = slt.multiselect("Date vs ?", (("open", "close", "high", "low")))
        if len(opt) == 0:
            slt.warning("Please choose a metric")
        else:
            # ask the user for an interval (maybe the month will be a good option)
            starting_date = str(slt.date_input("Choose the starting period", min_value=pd.to_datetime("2013-01-01"), max_value=pd.to_datetime("2018-03-01")))
            ending_date = str(slt.date_input("Choose the ending period", min_value=pd.to_datetime("2013-01-01"), max_value=pd.to_datetime("2018-03-01")))

            s_time = pd.to_datetime(starting_date)
            e_time = pd.to_datetime(ending_date)
            if e_time <= s_time:
                slt.warning("Ending time needs to be greater than starting time")
            else :
                if (pd.to_datetime(ending_date) - pd.to_datetime(starting_date)).days > 360:
                    slt.warning("Please choose a smaller range")
                else:
                    mask = df.date.between(starting_date, ending_date)
                    plot_graphs(df, mask, opt)
                
    else:
        # compare between two companies
        slt.subheader("Compare")
        slt.markdown("Choose your two companies that you want to compare...")
        fc = slt.selectbox("Company #1", names)
        sc = slt.selectbox("Company #2", names)

        df_fc = df[df.Name == fc]
        df_sc = df[df.Name == sc]

        if fc == sc:
            slt.warning("The companies cannot be same! Please choose a differnt one")
        else:
            slt.subheader("On which Parameters do you want to compare {0} and {1}?".format(fc, sc))
            # give parameters on which to compare
            options = slt.multiselect("Parameters", (("open", "close", "high", "low")))
            if len(options) == 0:
                slt.warning("Please choose a parameter!")
            else:
                slt.markdown("Please provide the interval")
                starting_date = str(slt.date_input("Choose the starting period", min_value=pd.to_datetime("2013-01-01"), max_value=pd.to_datetime("2018-03-01")))
                ending_date = str(slt.date_input("Choose the ending period", min_value=pd.to_datetime("2013-01-01"), max_value=pd.to_datetime("2018-03-01")))

                s_time = pd.to_datetime(starting_date)
                e_time = pd.to_datetime(ending_date)
                if e_time <= s_time:
                    slt.warning("Ending time needs to be greater than starting time")
                else :
                    if (pd.to_datetime(ending_date) - pd.to_datetime(starting_date)).days > 360:
                        slt.warning("Please choose a smaller range")
                    else:
                        mask = df.date.between(starting_date, ending_date)
                        compare_graphs(df_fc, df_sc, mask, options, [fc, sc])
                

if __name__ == '__main__':
    main()