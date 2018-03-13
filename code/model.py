import numpy as np
import pandas as pd
import json

from method import KNN, Logistic, PCR_PLS, RF_BAG_BST, SVM


COLUMNS = ['name', 'code', 'time', 'price', 'time_1', 'price_1', \
           'price_dif_1', 'sell_1', 'buy_1', 'volume_1', 'variation_1', \
           'post_num_1', 'unique_id_1', 'click_1', 'like_1', 'dislike_1', \
           'time_2', 'price_2', 'price_dif_2', 'sell_2', 'buy_2', \
           'volume_2', 'variation_2', 'post_num_2', 'unique_id_2', \
           'click_2', 'like_2', 'dislike_2', 'time_3', 'price_3', \
           'price_dif_3', 'sell_3', 'buy_3', 'volume_3', 'variation_3', \
           'post_num_3', 'unique_id_3', 'click_3', 'like_3', 'dislike_3', \
           'mkt_cap', 'kospi', 'kosdaq', 'trash', 'yesterday_closing_price', \
           'is_maximum', 'is_minimum', 'price_volatility', 'price_trend', \
           'average_price_volatility', 'sell_minus_buy_1', \
           'sell_minus_buy_2', 'sell_minus_buy_3', 'is_price_gap_stable', \
           'price_gap_volatility', 'is_like_higher', 'volume_trend', \
           'post_num_trend', 'unique_id_trend', 'click_trend', \
           'price_increase', 'did_price_increase', 'did_price_033', \
           'did_price_100', 'did_price_150', 'kospi_ind', 'kosdaq_ind', \
           'time_slot', 'ko_inter', 'early_mor', 'morning', 'lunch', \
           'afternoon', 'late', 'mkt_change', 'alpha', 'per_now', \
           'kospi_1', 'kospi_2', 'kospi_3', 'kospi_answer', 'kosdaq_1', \
           'kosdaq_2', 'kosdaq_3', 'kosdaq_answer', 'kospi_trend', \
           'kosdaq_trend', 'kospi_increase', 'kosdaq_increase', \
           'market_increase', 'did_opening_price_increase', 'price_1_sq', \
           'price_dif_1_sq', 'sell_1_sq', 'buy_1_sq', 'volume_1_sq', \
           'variation_1_sq', 'post_num_1_sq', 'unique_id_1_sq', \
           'click_1_sq', 'like_1_sq', 'dislike_1_sq', 'price_2_sq', \
           'price_dif_2_sq', 'sell_2_sq', 'buy_2_sq', 'volume_2_sq', \
           'variation_2_sq', 'post_num_2_sq', 'unique_id_2_sq', \
           'click_2_sq', 'like_2_sq', 'dislike_2_sq', 'price_3_sq', \
           'price_dif_3_sq', 'sell_3_sq', 'buy_3_sq', 'volume_3_sq', \
           'variation_3_sq', 'post_num_3_sq', 'unique_id_3_sq', \
           'click_3_sq', 'like_3_sq', 'dislike_3_sq', 'mkt_cap_sq', \
           'yesterday_closing_price_sq', 'price_volatility_sq', \
           'price_trend_sq', 'average_price_volatility_sq', \
           'sell_minus_buy_1_sq', 'sell_minus_buy_2_sq', \
           'sell_minus_buy_3_sq', 'price_gap_volatility_sq', \
           'volume_trend_sq', 'post_num_trend_sq', 'unique_id_trend_sq', \
           'click_trend_sq', 'kospi_ind_sq', 'kosdaq_ind_sq', \
           'time_slot_sq', 'ko_inter_sq', 'mkt_change_sq', 'alpha_sq', \
           'per_now_sq', 'kospi_1_sq', 'kospi_2_sq', 'kospi_3_sq', \
           'kosdaq_1_sq', 'kosdaq_2_sq', 'kosdaq_3_sq', 'kospi_trend_sq', \
           'kosdaq_trend_sq']

TO_DEL = ['name', 'code', 'time', 'price', 'time_1', 'time_2', 'time_3', \
          'price_increase', 'did_price_increase', 'did_price_033', \
          'did_price_100', 'did_price_150', 'kospi_answer', \
          'kosdaq_answer', 'kospi_increase', 'kosdaq_increase', \
          'market_increase']

X_COL = []
for var in COLUMNS:
    if var not in TO_DEL:
        X_COL.append(var)


try:
    with open("../data/dataframe/dataframe_02.json", 'r', encoding='UTF-8') as f:
        FEB = json.load(f)
except FileNotFoundError as e:
    print(e)

try:
    with open("../data/dataframe/dataframe_03.json", 'r', encoding='UTF-8') as f:
        MAR = json.load(f)
except FileNotFoundError as e:
    print(e)

DF_FEB = pd.DataFrame(FEB, columns = COLUMNS)
DF_MAR = pd.DataFrame(MAR, columns = COLUMNS)
DF = pd.concat([DF_FEB, DF_MAR])
DF = DF.dropna(axis=0, how='any')

#define filter for trainig set, validation test and testing set
TIME_FILTER_TRAIN = (DF['time'].str.startswith("2018-02-21")) | \
                    (DF['time'].str.startswith("2018-02-20")) | \
                    (DF['time'].str.startswith("2018-02-14"))
        
TIME_FILTER_VALID = (DF['time'].str.startswith("2018-02-22")) | \
                    (DF['time'].str.startswith("2018-02-23")) | \
                    (DF['time'].str.startswith("2018-02-26")) 

TIME_FILTER_TEST = (DF['time'].str.startswith("2018-02-28")) | \
                   (DF['time'].str.startswith("2018-03-02")) | \
                   (DF['time'].str.startswith("2018-03-05")) | \
                   (DF['time'].str.startswith("2018-02-27")) | \
                   (DF['time'].str.startswith("2018-03-06")) | \
                   (DF['time'].str.startswith("2018-03-07"))

TRAIN_DF = DF[TIME_FILTER_TRAIN].reset_index(drop = True)
VALID_DF = DF[TIME_FILTER_VALID].reset_index(drop = True)
TEST_DF = DF[TIME_FILTER_TEST].reset_index(drop = True)

#split X and y dataframe, hardcoding y variable is 'did_price_033'
X = DF[X_COL]
Y = DF['did_price_033']
X_TRAIN = TRAIN_DF[X_COL]
Y_TRAIN = TRAIN_DF['did_price_033']
X_VALID = VALID_DF[X_COL]
Y_VALID = VALID_DF['did_price_033']
X_TEST = TEST_DF[X_COL]
Y_TEST = TEST_DF['did_price_033']
TEST_IN = TEST_DF['price_increase']