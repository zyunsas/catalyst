"""
The goal of this is to be able to load json and stuff
"""
import yfinance as yf
import collections
import matplotlib.pyplot as plt
import numpy as np

msft = yf.Ticker("XOM")

#print(msft.dividends)
#print(msft.info)
hist = msft.history(period="10y")

#print(type(hist))

que = collections.deque()
mva = []
normal = []
dates = []
mva_mash = {}

moving_average_amount = 50
#Get 30 day moving average
for index, row in hist.iterrows():
    que.append(row['Open'])
    if(len(que) > moving_average_amount):
        movingAverage = sum(que) / len(que)
        mva.append(movingAverage)
        dates.append(index)
        normal.append(row['Open'])
        mva_mash[index] = movingAverage
        que.popleft()
    # Add to queue

# Now loop through history and run the strategy

# Bit cheesy, but works
# strat works well with stocks with long term and slow growth
multiplier = 1
def strat(shares, cash, current, mva): # 32.42214511664393%, assuming that the stock goes consistently up
    # get current cash, and get how much stocks you can buy
    #1.26, 0.82
    ratio = float(current)/float(mva) 
    #print("Ratio:", ratio)
    if ratio > 1.26:
        # sell all
        return -shares
    elif ratio < 0.5:
        # if it's too far down, bail lol
        return -shares
    elif ratio < 0.82:
        # then buy everything
        return int(cash/current)
    else: 
        return 0

    #
def easy_strat(current, mva): # 3.42663077126717%
    return int(current - mva)

costhistory = []
mvadiffhistory = []
totalWealth = []
sharesAmount = []
buyingActivity = []

# Train model
# Determine profit
currentCash = startingCash = 10000

profitmap = {}
    
def doModel():
    isstart = True
    shares = 0

    for index, row in hist.iterrows():
        # Get the thing
        if(index in mva_mash):
            price = (row['Open'])

            if isstart:
                startDate = index
                startingPrice = price
                isstart = False

            enddate = index
            endingPrice = price

            sharesToGet = strat(shares, price, mva_mash[index])

            mvadiffhistory.append(price - mva_mash[index])

            buyingActivity.append(sharesToGet)

            if shares + sharesToGet >= 0 and currentCash - (sharesToGet * price) >= 0:
                shares += sharesToGet
                currentCash -= (sharesToGet * price)
            # Get more shares...
            elif sharesToGet <= 0 and -sharesToGet >= shares:
                # Selling all available shares
                shares = 0
                currentCash -= sharesToGet*price
            elif sharesToGet == 0:
                # Get no shares
                pass

            costhistory.append(currentCash)

            totalWealth.append(currentCash + shares*price)

            sharesAmount.append(shares)
            #Will buy X amount of shares and sell them if it's positive and negative
            #print ("${} and {} shares".format(currentCash, shares))
            '''if thing > 0:
                print("Buy at {}".format(index))
                ax.annotate('buy', xy=(index, row['High']),  xycoords='data',
                    xytext=(0.8, 0.95), textcoords='axes fraction',
                    arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='right', verticalalignment='top',
                )
            elif thing < 0:
                print("Sell at {}".format(index))'''
    print(shares)
    wealth = currentCash + shares*price
    growthRate = (wealth - startingCash)/startingCash
    profitmap[i] = wealth

isstart = True

shares = 0

for index, row in hist.iterrows():
    # Get the thing
    if(index in mva_mash):
        price = (row['Open'])

        if isstart:
            startDate = index
            startingPrice = price
            isstart = False

        enddate = index
        endingPrice = price

        #print(mva_mash[index], " ", price)
        sharesToGet = strat(shares, currentCash, price, mva_mash[index])
        #print(sharesToGet)

        mvadiffhistory.append(price - mva_mash[index])

        buyingActivity.append(sharesToGet)

        if sharesToGet > 0:
            # buying
            if shares <= sharesToGet and sharesToGet*price <= currentCash:
                # buy all of that
                shares += sharesToGet
                currentCash -= (sharesToGet * price)
        elif sharesToGet < 0 and sharesToGet <= shares:
            # selling
            shares += sharesToGet
            currentCash -= sharesToGet*price

        costhistory.append(currentCash)

        totalWealth.append(currentCash + shares*price)

        sharesAmount.append(shares)
        #Will buy X amount of shares and sell them if it's positive and negative
        #print ("${} and {} shares".format(currentCash, shares))
        '''if thing > 0:
            print("Buy at {}".format(index))
            ax.annotate('buy', xy=(index, row['High']),  xycoords='data',
                xytext=(0.8, 0.95), textcoords='axes fraction',
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='right', verticalalignment='top',
            )
        elif thing < 0:
            print("Sell at {}".format(index))'''

print(shares)
wealth = currentCash + shares*price
growthRate = (wealth - startingCash)/startingCash
#profitmap[i] = wealth

# Find interval which it makes the most money, and test with finer resolution

print(profitmap)
fig, ax = plt.subplots(4)  # Create a figure containing a single axes.
#ax.plot(dates, mva)  # Plot some data on the axes.
#ax.plot(dates, normal)  # Plot some data on the axes.
fig.subplots_adjust(right=0.75)

ax[0].plot(dates, costhistory, color='tab:blue', label='Cash held')  
ax[0].legend()

ax2 = ax[0].twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:red'
ax2.set_ylabel('shares', color=color)  # we already handled the x-label with ax1
ax2.plot(dates, sharesAmount, color=color, label='shares')
ax2.tick_params(axis='y', labelcolor=color)
ax2.plot(dates, buyingActivity, color="tab:orange", label='Buying activity')
ax2.legend(loc="upper right")

ax3 = ax[1]
ax3.set_ylabel('share price', color='tab:purple')  
ax3.plot(dates, mva_mash.values(), color='tab:purple', label='{} Moving Average'.format(moving_average_amount)) 
ax3.plot(dates, normal, color='tab:pink', label="Price") 
ax3.legend()

ax4 = ax[2]
ax4.plot(dates, mvadiffhistory, label="Moving average subtracted by stock price") 
ax4.legend()

ax5 = ax[3]
ax5.plot(dates, totalWealth, label="Total Wealth") 
ax5.legend()

wealth = currentCash + shares*price
growthRate = (wealth - startingCash)/startingCash
print("Wealth: {}, Cash: {}, Total gain: {}%".format(wealth, currentCash, growthRate*100))
years_invested = (enddate-startDate).to_pytimedelta().days/365

hodl = (endingPrice - startingPrice) / startingPrice
print("Or {}% every year for {} years, compared to {}% if you just held (ideal is about 10% each year if you just hold the dow)".format(growthRate/years_invested * 100, years_invested, hodl/years_invested))

plt.show()
