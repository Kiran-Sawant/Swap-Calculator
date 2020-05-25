import MetaTrader5 as mt5
import time

mt5.initialize()

def pair_generator(symbol):
    """Takes the asset name and gives the USD converting forex pair
        ie. for JP225 it will return USDJPY"""

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


def fxAdjust(exposure, pair):
    """Adjusts non-USD exposure into USD"""

    mt5.symbol_select(pair)
    time.sleep(1)
    if pair[0:3] == 'USD':
        adjustedExpo = exposure / mt5.symbol_info_tick(pair).ask
    else:
        adjustedExpo = exposure * mt5.symbol_info_tick(pair).ask

    return adjustedExpo


def swap(symbol):
    """Returns the rollover costs in USD"""

    if symbol[-1: -5: -1] in ['ESYN', 'SAN.']:              #If the asset is US equity or ETF
        swap_long = mt5.symbol_info(symbol).swap_long
        swap_short = mt5.symbol_info(symbol).swap_short
        swapLday = ((exposure * swap_long) / 100) / 365
        swapSday = ((exposure * swap_short) / 100) / 365
        return (swapLday, swapSday)
    else:                                                   #If the asset is forex, commodity, index CFDs
        swap_long = mt5.symbol_info(symbol).swap_long
        swap_short = mt5.symbol_info(symbol).swap_short
        swapLday = swap_long * volume
        swapSday = swap_short * volume
        if symbol in denoDict:                              #If the asset is a Dollar Cross
            dollar_swapLday = fxAdjust(swapLday, denoDict[symbol])
            dollar_swapSday = fxAdjust(swapSday, denoDict[symbol])
            return (dollar_swapLday, dollar_swapSday)
        elif symbol[0:3] == 'USD':                          #If the asset is a USD base FX pair
            dollar_swapLday = swapLday / mt5.symbol_info_tick(symbol).ask
            dollar_swapSday = swapSday / mt5.symbol_info_tick(symbol).bid
            return (dollar_swapLday, dollar_swapSday)
        else:                                               #If the asset is quoted in USD
            return (swapLday, swapSday)


print("Enter x to Quit...")
while True:
    print('\n', '='*50)
    try:
        symbol = input("Enter the symbol as in MT5: ").upper()
        if symbol in ['x', 'X']:
            break
        volume = float(input("Enter volume of trade: "))
    except ValueError:
        print("Wrong input try again! ")
        continue
    mt5.symbol_select(symbol)
    time.sleep(1)
    ask = mt5.symbol_info_tick(symbol).ask
    exposure = ask * volume
    long, short = swap(symbol)
    print(f"{symbol} swap long/day: ${long:.2f}, swap short/day: ${short:.2f}")

mt5.shutdown()