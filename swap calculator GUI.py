import tkinter as tk
import MetaTrader5 as mt5
import time

#___Initialize MT5___#
mt5.initialize()

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

#_________Swap calculating functions__________#
def fxAdjust(exposure, pair):
    """Adjusts non-USD exposure into USD"""

    mt5.symbol_select(pair)
    time.sleep(1)
    if pair[0:3] == 'USD':
        adjustedExpo = exposure / mt5.symbol_info_tick(pair).ask
    else:
        adjustedExpo = exposure * mt5.symbol_info_tick(pair).ask

    return adjustedExpo


def swap(symbol, volume, exposure):
    """Returns the rollover costs in USD"""

    if symbol[-1: -5: -1] in ['ESYN', 'SAN.']:              #If the asset is US equity or ETF
        swap_long = mt5.symbol_info(symbol).swap_long
        swap_short = mt5.symbol_info(symbol).swap_short
        swapLday = ((exposure * swap_long) / 100) / 365
        swapSday = ((exposure * swap_short) / 100) / 365
        return (swapLday.__round__(3), swapSday.__round__(3))
    else:                                                   #If the asset is forex, commodity, index CFDs
        swap_long = mt5.symbol_info(symbol).swap_long
        swap_short = mt5.symbol_info(symbol).swap_short
        swapLday = swap_long * volume
        swapSday = swap_short * volume
        if symbol in denoDict:                              #If the asset is a Dollar Cross
            dollar_swapLday = fxAdjust(swapLday, denoDict[symbol])
            dollar_swapSday = fxAdjust(swapSday, denoDict[symbol])
            return (dollar_swapLday.__round__(3), dollar_swapSday.__round__(3))
        elif symbol[0:3] == 'USD':                          #If the asset is a USD base FX pair
            dollar_swapLday = swapLday / mt5.symbol_info_tick(symbol).ask
            dollar_swapSday = swapSday / mt5.symbol_info_tick(symbol).bid
            return (dollar_swapLday.__round__(3), dollar_swapSday.__round__(3))
        else:                                               #If the asset is quoted in USD
            return (swapLday.__round__(3), swapSday.__round__(3))


def test():
    selection = assetList.curselection()[0]
    symbol = assetList.get(selection)
    mt5.symbol_select(symbol)
    volume = float(volEntryVar.get())
    try:
        entryPrice = float(priceEntryVar.get())
    except ValueError:
        entryPrice = float(mt5.symbol_info_tick(symbol).ask)
    
    exposure = volume * entryPrice

    long, short = swap(symbol, volume, exposure)
    sLongVar.set(long)
    sShortVar.set(short)
    

#_____Retriving Asset names____#
asset_names = [info.name for info in mt5.symbols_get()]

#___Initialize Window____#
mainWindow = tk.Tk()
mainWindow.geometry('440x480')
mainWindow.title('Carry Calculator')

#___________variables___________#
# listbox variables
listBoxVar = tk.Variable(mainWindow)
listBoxVar.set(asset_names)

# Entrybox Variables
volEntryVar = tk.StringVar()
priceEntryVar = tk.StringVar()

# Answer Variables
sLongVar = tk.IntVar()
sShortVar = tk.IntVar()

#_____________________Creating Widgets_________________________#
assetLabel = tk.Label(mainWindow, text='Assets')
assetList = tk.Listbox(mainWindow, width=30, height=28, listvariable=listBoxVar)
scroll = tk.Scrollbar(mainWindow, orient=tk.VERTICAL, command=assetList.yview)
assetList['yscrollcommand'] = scroll.set
volLabel = tk.Label(mainWindow, text='Volume: ')
priceLabel = tk.Label(mainWindow, text='Price: ')
LSwaplabel = tk.Label(mainWindow, text='Swap Long: ')
LSwapValue = tk.Label(mainWindow, textvariable=sLongVar)
SSwaplabel = tk.Label(mainWindow, text='Swap Short: ')
SSwapValue = tk.Label(mainWindow, textvariable=sShortVar)
volEntry = tk.Entry(mainWindow, textvariable=volEntryVar)
priceEntry = tk.Entry(mainWindow, textvariable=priceEntryVar)
button = tk.Button(mainWindow, text='Calculate', activebackground='red', activeforeground='white', cursor='pirate',command=test)

#_____________________________Placing Widgets__________________________#
assetLabel.grid(row=0, column=0, sticky='w', padx=8)
assetList.grid(row=1, column=0, rowspan=15, padx=8)
scroll.grid(row=1, column=1, rowspan=15, sticky='ns', padx=0)
volLabel.grid(row=1, column=2, sticky='n')
priceLabel.grid(row=2, column=2, sticky='n')
LSwaplabel.grid(row=3, column=2, sticky='n')
SSwaplabel.grid(row=4, column=2, sticky='n')
volEntry.grid(row=1, column=3, sticky='n')
priceEntry.grid(row=2, column=3, sticky='n')
button.grid(row=5, column=3)
LSwapValue.grid(row=3, column=3, sticky='nw')
SSwapValue.grid(row=4, column=3, sticky='nw')


mainWindow.mainloop()
mt5.shutdown()