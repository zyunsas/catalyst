import yfinance as yf
import collections
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean 
import operator
import threading
import time

# get history
information = yf.Ticker("XOM")

# 10 year time period
hist = information.history(period="10y")

historic_price_list = collections.deque()


# Tuple of (opening price, moving average)
data = {}

moving_average_amount = 50
for index, row in hist.iterrows():
    historic_price_list.append(row['Open'])

    if len(historic_price_list) > moving_average_amount:
        moving_average = mean(historic_price_list)
        data[index] = (row['Open'], moving_average)
        historic_price_list.popleft()

class Strategy:

    def __init__(self, _sell, _buy, _stop):
        self.sell_boundary = _sell
        self.buy_boundary = _buy
        self.stop_gap = _stop
        pass

    def strategy(self, shares, cash, current_price, mva):
        ratio = current_price/mva
        if ratio > self.sell_boundary:
            # sell all
            return -shares
        elif ratio < self.stop_gap:
            # if it's too far down, bail lol
            return -shares
        elif ratio < self.buy_boundary:
            # then buy everything
            return int(cash/current_price)
        else: 
            return 0

profit = {}
buy_list = {}

def testModel(sell, buy):
    strat = Strategy(sell, buy, 0.5)
    
    shares = 0
    cash = starting_cash = 10000
    
    wealth_hist = []
    buying_hist = []

    final_price = 0
    t0 = time.time()
    # loop through all values
    #for key, value in hist.iterrows():
    #    if key not in data:
    for key, prices in data.items():
            #continue

        purchase = strat.strategy(shares, cash, prices[0], prices[1])

        #buying_hist.append(purchase)

        # Buy and sell stuff
        if purchase > 0:
            # buying
            if shares <= purchase and purchase*prices[0] <= cash:
                # buy all of that
                shares += purchase
                cash -= (purchase * prices[0])
        elif purchase < 0 and purchase <= shares:
            # selling
            shares += purchase
            cash -= purchase*prices[0]

        final_price = prices[0]

        #history
        #wealth_hist.append(cash + shares*final_price)
    
    #get wealth
    wealth = cash + shares*final_price
    growthRate = (wealth - starting_cash)/starting_cash
    #print("Wealth: {}, Cash: {}, Total gain: {}%".format(wealth, cash, growthRate*100))
    years_invested = (list(data.keys())[-1] - list(data.keys())[0]).to_pytimedelta().days/365

    hodl = (final_price - starting_cash) / starting_cash
    #print("Or {}%% every year for {} years, compared to {}%% if you just held (ideal is about 10%% each year if you just hold the dow or something)".format(growthRate/years_invested * 100, years_invested, hodl/years_invested))

    profit[(sell, buy)] = growthRate/years_invested * 100
    #print(f"Amount gained: {growthRate/years_invested * 100}")
    #t1 = time.time()
    #diff = t1-t0
    #print(diff)
    #buy_list[buy] = growthRate/years_invested * 100
    '''fig, ax = plt.subplots()
    ax.plot(list(data.keys()), wealth_hist)

    plt.show()'''


def func(value):
    for k in range(50, 100):
        sell = (k/100)

        testModel(value, sell)
    print("Done calculating ", value)

threads = []
for k in range(101, 210):
    value = (k/100)
    x = threading.Thread(target=func, args=(value,))
    x.start()
    threads.append(x)

    print("Started thread ", value)
    
for th in threads:
    th.join()

highest = max(profit.items(), key=operator.itemgetter(1))[0]

#fig, ax = plt.subplots()
#ax.plot(list(profit.keys()), profit.values())

#plt.show()

#Then we get buy I guess

#fig, ax = plt.subplots()
#ax.plot(list(buy_list.keys()), buy_list.values())

#plt.show()

print("", highest, profit[highest])
