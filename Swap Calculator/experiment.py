import MetaTrader5 as mt5

mt5.initialize()

# for i in mt5.account_info():
    # print(i)

#________Creating denomination dictionary_________#
def pair_generator(symbol):
    """Takes the asset name and gives the USD converting forex pair
        ie. for GBPAUD it will return AUDUSD"""

    if symbol in ['EUR', 'GBP', 'AUD', 'NZD']:
        return f'{symbol}USD'
    else:
        return f'USD{symbol}'

allinfo = mt5.symbols_get()

templist = list()
for info in allinfo:
    if info.currency_profit == 'USD' or info.currency_margin == 'USD':
        continue
    else:
        templist.append((info.name, info.currency_profit))

denoDict = dict()
for i in templist:
    denoDict[i[0]] = pair_generator(i[1])

# print(denoDict)

asset_names = [info.name for info in mt5.symbols_get()]

for i in asset_names:
    print(i)