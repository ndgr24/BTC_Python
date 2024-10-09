import ccxt, talib, numpy, pygame, time, os, sys, pprint, subprocess
from datetime import datetime

RSI_PERIOD = 14
closes = []  # Array of closed candle
price_values = []
rsi_values = []

# pygame init code
pygame.init()
win = pygame.display.set_mode((350, 360))

# colors
white = (255, 255, 255)
grey = (191, 191, 196) #(220, 220, 220)
dark_grey = (70, 70, 72)
dark_dark_grey = (50, 50, 50)
black = (0, 0, 0)
green = (103, 211, 78)
yellow = (245, 179, 0)
red = (211, 77, 78)

# font setup
font = pygame.font.Font('C:\Windows\Fonts\Arial.ttf', 11)
price_font = pygame.font.Font(None, 12)
user_text = ''
term_text = font.render('type [help] for a command list', True, white)

# pygame caption, icon, and time setup
pygame.display.set_caption('epic gains! 1.0')
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)
now = datetime.now()

# exchange variables
exchange = ccxt.binanceus()
symbol = 'BTC/USD'
currency = 'USD'
crypto_type = 'BTC'

# index and bool variables
holding = False
run = True
rsi_indicator = 2
ma_indicator = 2

# calculates the current rsi (relative strength indicator) for the given symbol
def Rsi():
    # global variables
    global rsi_indicator
    global rsi_text
    global rsi_status_text

    # checks if the current symbol value is in the array of closes (this keeps the list from getting repeat values).
    # If the value is not in the close list it is added to the list (closes)
    if not (ticker['last'] in closes):
        closes.append(ticker['last'])

    # rsi calculation using the talib library.
    # this code also formats the output a bit by rounding to the nearest 100th.
    np_closes = numpy.array(closes)
    rsi = talib.RSI(np_closes, RSI_PERIOD)
    last_rsi = rsi[-1]
    formatted_rsi = str(round(last_rsi, 2))

    # this is all gui stuff like changing the color of the square that is next to the rsi value
    if formatted_rsi != 'nan':
        if float(formatted_rsi) >= 70:  # 70 is a typical rsi value used as a sell indicator
            rsi_indicator = 0  # sell indicator
            rsi_text = font.render('RSI: ' + formatted_rsi, True, white)  # sets the text for the 'gui' function
            pygame.draw.rect(win, green, (10, 35, 5, 12))  # changes color of rect
        elif float(formatted_rsi) <= 30:  # 30 is a typical rsi value used as a buy indicator
            rsi_indicator = 1  # buy indicator
            rsi_text = font.render('RSI: ' + formatted_rsi, True, white)  # sets the text for the 'gui' function
            pygame.draw.rect(win, red, (10, 35, 5, 12))  # changes color of rect
        else:
            rsi_indicator = 2  # don't buy or sell

            rsi_text = font.render('RSI: ' + formatted_rsi, True, white)  # sets the text for the 'gui' function
            pygame.draw.rect(win, yellow, (10, 35, 5, 12))  # changes color of rect
    else:
        rsi_text = font.render('RSI: ' + formatted_rsi, True, white)  # sets the text for the 'gui' function
        pygame.draw.rect(win, yellow, (10, 35, 5, 12))  # changes color of rect


# calculates the mv (moving average) this indicator is used to denote market integrity.
def MovingAverage():
    # global variables
    global ma_indicator
    global moving_average_text

    # Number of closes before a moving average is calculated.
    # A smaller closing value will be less significant crossing period but will be triggered more often.
    # A larger closing value will have a more significant crossing period but will be trigger less often.
    # Feel free to play with these values to find a proper balance. Just remember your money is a steak here.
    closing_number = 50

    # starts calculation once enough close data is collected
    if len(closes) >= closing_number:
        # Grabbing past 50 closes and finding average of those closes.
        last_50_closes = closes[-50:]
        moving_average = sum(last_50_closes) / 50
        # Here we are adding a 1% buffer to the MA to mitigate faulty signals.
        mv_plus_three_percent = moving_average + moving_average * 0.01
        mv_minus_three_percent = moving_average - moving_average * 0.01

        # Formats text to display moving average.
        moving_average_text = font.render('50 MA: ' + str(round(moving_average, 2)), True, white)

        # Flagged as a sell if the current crypto value is greater than the moving average
        if moving_average < ticker['last']:
            ma_indicator = 0  # sell indicator
            pygame.draw.rect(win, green, (10, 52, 5, 12))  # changes color of rect
        # Flagged as a buy if the current crypto value is less than the moving average
        elif moving_average > ticker['last']:
            ma_indicator = 1  # buy indicator
            pygame.draw.rect(win, red, (10, 52, 5, 12))  # changes color of rect
        else:
            ma_indicator = 2  # don't buy or sell
            pygame.draw.rect(win, yellow, (10, 52, 5, 12))  # changes color of rect
    else:
        # Formats text to display moving average if no data is available yet.
        moving_average_text = font.render('50 MA: nan', True, white)
        pygame.draw.rect(win, yellow, (10, 52, 5, 12))  # changes color of rect

# Should you buy or sell? That is what this function must decide.
def BuyOrSell():
    # global var
    global holding

    # if RSI and MA both indicate a sell
    if rsi_indicator == 0 and ma_indicator == 0 and holding == True:
        # saves price data to log.txt with a timestamp
        print('sell')
        dateAndTime = now.strftime("%d/%m/%Y %H:%M")
        dataLog = open("log.txt", "a")
        dataLog.write("SELL " + str(ticker['last']) + " " + dateAndTime + "\n")
        dataLog.close()
        holding = False
    # if RSI and MA both indicate a buy
    elif rsi_indicator == 1 and ma_indicator == 1 and holding == False:
        # saves price data to log.txt with a timestamp
        print('buy')
        dateAndTime = now.strftime("%d/%m/%Y %H:%M")
        dataLog = open("log.txt", "a")
        dataLog.write("BUY " + str(ticker['last']) + " " + dateAndTime + "\n")
        dataLog.close()
        holding = True

def DispValue():
    # global values
    global price_text
    global volume_text
    global formatted_price

    # simply displays the current pricing data on the screen and the current trading volume
    price_text = font.render(crypto_type + ': $' + str(ticker['last']) + ' ' + currency, True, white)
    volume_text = font.render('Volume: ' + str(ticker['baseVolume'])[0:9], True, white)

def DispValueLineChart():
    screen_min_y = 160
    screen_max_y = 290
    chart_min_y = 40000
    chart_max_y = 60000

    screen_min_x = 10
    screen_max_x = 340
    chart_min_x = 0
    chart_max_x = 500

    pygame.draw.rect(win, dark_grey, (10, 160, 330, 130), 0)
    pygame.draw.line(win, dark_dark_grey, (10, 176.25), (340, 176.25))
    pygame.draw.line(win, dark_dark_grey, (10, 192.5), (340, 192.5))
    pygame.draw.line(win, dark_dark_grey, (10, 208.75), (340, 208.75))
    pygame.draw.line(win, dark_dark_grey, (10, 225), (340, 225))
    pygame.draw.line(win, dark_dark_grey, (10, 241.25), (340, 241.25))
    pygame.draw.line(win, dark_dark_grey, (10, 257.5), (340, 257.5))
    pygame.draw.line(win, dark_dark_grey, (10, 273.75), (340, 273.75))

    value_text1 = price_font.render(' 60,000 ', True, white)
    value_text2 = price_font.render(' 57,500 ', True, white, dark_grey)
    value_text3 = price_font.render(' 55,000 ', True, white, dark_grey)
    value_text4 = price_font.render(' 52,500 ', True, white, dark_grey)
    value_text5 = price_font.render(' 50,000 ', True, white, dark_grey)
    value_text6 = price_font.render(' 47,500 ', True, white, dark_grey)
    value_text7 = price_font.render(' 45,000 ', True, white, dark_grey)
    value_text8 = price_font.render(' 42,500 ', True, white, dark_grey)
    value_text9 = price_font.render(' 40,000 ', True, white)

    price_history = exchange.fetch_ohlcv(symbol, '1h')

    for i in price_history:
        i1 = str(i[4:-1])
        screen_value_y = ((float(i1[1:-1]) - chart_min_y) / (chart_max_y - chart_min_y)) * (screen_max_y - screen_min_y) + screen_min_y
        if not price_values or len(price_values) < chart_max_x and screen_value_y != price_values[len(price_values) - 1]:
            price_values.append(screen_value_y)
        elif len(price_values) > chart_max_x:
            price_values.append(screen_value_y)
            price_values.pop(0)

    for i in range(0, chart_max_x):
        screen_value_x = ((i - chart_min_x) / (chart_max_x - chart_min_x)) * (
                    screen_max_x - screen_min_x) + screen_min_x
        new_value_y = price_values[i]
        old_value_y = price_values[i - 1]

        pygame.draw.line(win, green, (screen_value_x, new_value_y), (screen_value_x, old_value_y))

    win.blit(value_text1, (13, 156))
    win.blit(value_text2, (13, 172.25))
    win.blit(value_text3, (13, 188.5))
    win.blit(value_text4, (13, 204.75))
    win.blit(value_text5, (13, 221))
    win.blit(value_text6, (13, 237.25))
    win.blit(value_text7, (13, 253.5))
    win.blit(value_text8, (13, 269.75))
    win.blit(value_text9, (13, 286))

def DisplayRSI():
    screen_min_y = 300
    screen_max_y = 350
    chart_min_y = 10
    chart_max_y = 90

    screen_min_x = 10 + 9.52
    screen_max_x = 340
    chart_min_x = 0
    chart_max_x = 500 - 14

    pygame.draw.rect(win, dark_grey, (10, 300, 330, 50), 0)
    pygame.draw.line(win, dark_dark_grey, (10, 312.5), (339, 312.5))
    pygame.draw.line(win, dark_dark_grey, (10, 338.5), (339, 338.5))

    np_closes = numpy.array(price_values)
    rsi = talib.RSI(np_closes, RSI_PERIOD)
    rsi_list = rsi.tolist()
    #print(rsi)

    for i in rsi_list[14:]:
        screen_value_y = ((i - chart_min_y) / (chart_max_y - chart_min_y)) * (screen_max_y - screen_min_y) + screen_min_y
        if not rsi_values or len(rsi_values) < chart_max_x and screen_value_y != rsi_values[len(rsi_values) - 1]:
            rsi_values.append(screen_value_y)
        elif len(price_values) > chart_max_x:
            rsi_values.append(screen_value_y)
            rsi_values.pop(0)

    for i in range(0, chart_max_x):
        screen_value_x = ((i - chart_min_x) / (chart_max_x - chart_min_x)) * (screen_max_x - screen_min_x) + screen_min_x
        new_value_y = rsi_values[i]
        old_value_y = rsi_values[i - 1]

        pygame.draw.line(win, yellow, (screen_value_x, new_value_y), (screen_value_x, old_value_y))

        rsi_value_text1 = price_font.render(' 70 ', True, white, dark_grey)
        rsi_value_text2 = price_font.render(' 30 ', True, white, dark_grey)
        win.blit(rsi_value_text1, (10, 309.5))
        win.blit(rsi_value_text2, (10, 335.5))

def Gui():
    # set screen background to white
    win.fill(dark_dark_grey)

    # draw a bunch of rectangles
    pygame.draw.rect(win, dark_grey, (137, 10, 203, 140), 0)
    pygame.draw.rect(win, dark_grey, (10, 10, 117, 140), 0)

    # Data functions called here so we can display it on the screen.
    DispValue()
    Rsi()
    MovingAverage()

    term_input_text = font.render('TERMINAL: ' + user_text, True, white)

    # display text from data functions
    win.blit(price_text, (18, 18))
    win.blit(rsi_text, (18, 35))
    win.blit(moving_average_text, (18, 52))
    win.blit(volume_text, (18, 69))
    win.blit(term_input_text, (145, 18))
    win.blit(term_text, (145, 35))

    DispValueLineChart()
    DisplayRSI()

    pygame.display.flip()
    pygame.display.update()

# Main function. Ties everything together.
def Main():
    # global variables
    global run
    global user_text
    global term_text
    global ticker

    # event loop for pygame
    for event in pygame.event.get():
        # allows for user to exit program
        if event.type == pygame.QUIT:
            quit()
        # user terminal logic code
        elif event.type == pygame.KEYDOWN and len(user_text) < 22:
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[0:-1]
            elif event.key == pygame.K_RETURN:
                if user_text == 'set_up':
                    user_text = ''
                    os.startfile('setup.txt')
                    term_text = font.render('done', True, white)
                    Gui()
                elif user_text == 'open_log':
                    user_text = ''
                    os.startfile('log.txt')
                    term_text = font.render('done', True, white)
                    Gui()
                elif user_text == 'quit':
                    quit()
                elif user_text == 'help' or user_text == '[help]':
                    user_text = ''
                    term_text = font.render('set_up, open_log, quit, help', True, white)
                    Gui()
                else:
                    user_text = ''
                    term_text = font.render('error', True, white)
                    Gui()
            else:
                user_text += event.unicode

    # get symbol data
    ticker = exchange.fetch_ticker(symbol.upper())
    #pprint.pprint('\n\n' + str(ticker))

    Gui()
    BuyOrSell()

# restarts program on error. Need this for when connection issues occur.
def queryRepeatedly():
    while True:
        while True:
            try:
                Main()
            except Exception:
                pass

#Main()
queryRepeatedly()
