import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from datetime import datetime
from dash.dependencies import Input, Output, State
import tweepy as tw
import os
from flask import jsonify
import csv
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pprint
import pandas as pd
import numpy as np
from newsapi import NewsApiClient
import json as json


external_stylesheets = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(children=[
    html.H1(
        children='InfoCreeper Dashboard'
    ),

    html.Div(
        children=[
            html.Div(children=[
                html.H1(children='Twitter'),
                html.I("Enter a keyword to search in Twitter"),
                html.Br(),
                html.Div(dcc.Input(id='input', type='text',
                         placeholder='Search keyword')),
                html.Div(dcc.Input(id='date_input', type='text',
                         placeholder='YYYY-MM-DD')),
                html.Button('Submit', id='submit'),
                html.Div(id='output',
                         children='Enter a value and click on submit')
            ], className='container col-md-6')
        ],
        id="mainTweetDiv"
    ),
    html.Div(
        children=[
            html.Div(children=[
                html.H1(children='Yahoo'),
                html.I("Enter stock ticker:"),
                html.Br(),
                html.Div(dcc.Input(id='finance_input', type='text',
                         placeholder='Search ticker')),
                html.Label("Start date:"),
                html.Div(dcc.Input(id='startdate_input',
                         type='text', placeholder='YYYY-MM-DD')),
                html.Label("End date:"),
                html.Div(dcc.Input(id='enddate_input',
                         type='text', placeholder='YYYY-MM-DD')),
                html.Button('Submit', id='finance_submit'),
                html.Div(id='finance_output',
                         children='Enter a value and click on submit')
            ], className='container col-md-6')
        ],
        id="mainYahooDiv"
    ),
    html.Div(
        children=[
            html.Div(children=[
                html.H1(children='News API'),
                html.I("Enter a searchword for Scraping News:"),
                html.Br(),
                html.Div(dcc.Input(id='news_input', type='text',
                         placeholder='Enter keyword')),
                html.Button('Submit', id='news_submit'),
                html.Div(id='news_output',
                         children='Enter a value and click on submit')
            ], className='container col-md-6')
        ],
        id="mainNewsDiv"
    )
])


@app.callback(
    Output('output', 'children'),
    Input('submit', 'n_clicks'),
    State('input', 'value'),
    State('date_input', 'value')
)
def callTwitterApiAndWriteInCSV(counter, value, date_value):
    search_words = "{} -filter:retweets".format(value)
    all_tweets = []
    print(value, search_words)
    if value != None:
        print(value)
        with open('{}.csv'.format(value), 'w',) as csvfile:
            writer = csv.writer(csvfile)
            tweets = tw.Cursor(api.search,
                               q=search_words,
                               lang="en",
                               since=date_value).items(100)
            all_tweets = [tweet.text for tweet in tweets]
            for tweet in all_tweets:
                writer.writerow([tweet])
        return "Saved the tweets with the searchword in {}.csv file".format(value)
    return 'Enter a value and click on submit'


@app.callback(
    Output('finance_output', 'children'),
    Input('finance_submit', 'n_clicks'),
    State('finance_input', 'value'),
    State('startdate_input', 'value'),
    State('enddate_input', 'value')
)
def callYahooApiAndWriteInCSV(counter, value, startdate_value, enddate_value):
    if value != None:
        data_df = yf.download(value, start=startdate_value, end=enddate_value)
        data_df.to_csv("{}.csv".format(value))
        return 'Saved the stock data in the {}.csv file'.format(value)
    return 'Enter search ticker'


@app.callback(
    Output('news_output', 'children'),
    Input('news_submit', 'n_clicks'),
    State('news_input', 'value')
)
def callNewsApiAndWriteInCSV(counter, value):
    if value != None:
        keyword = "{}".format(value)
        all_articles = newsapi.get_everything(keyword,
                                              sources='bbc-news,the-verge',
                                              domains='bbc.co.uk,techcrunch.com',
                                              from_param='2021-04-29',
                                              to='2021-03-29',
                                              language='en',
                                              sort_by='relevancy',
                                              page=2)                            
        artcilesinstring = json.dumps(all_articles.json())
        allarticles = json.loads(artcilesinstring)
        listofarticles = allarticles['articles']
        df = pd.read_json(json.dumps(listofarticles))
        df.to_csv("{}.csv".format(value))

        with open('{}.csv'.format(value), 'w',) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
        return 'Saved the news data in the {}.csv file'.format(value)

    return 'Enter a keyword and click on submit'


consumer_key = 'seuGCMC2q0kTXJounWXmP520F'
consumer_secret = 'RoKzAi9trcPy4nlNYl0v41sSPts8XN2Enrv32h8EVZsMKLimTS'
access_token = '1303511996554338304-eJgorIf0su9WgchY1aWaPdxo4WR3RU'
access_token_secret = 'oysg7I3vbLm9MzNSPeV1cVHzMhAGc8J5tmHH2G8AOMqWb'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)


api_key = 'cecd1c1f508a410bbef01f38a4097483'
newsapi = NewsApiClient(api_key)


if __name__ == '__main__':
    app.run_server(debug=True)
