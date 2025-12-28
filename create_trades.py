import logging
import json
from dotenv import load_dotenv
import os
import requests
from openai import OpenAI
from fireworks import LLM

load_dotenv()


llm = LLM(model="gpt-oss-20b", deployment_type="serverless", api_key=os.getenv('FIREWORKS_API_KEY'))


fj_trade = "⚡️**FJFund** Trading Summary (Updated every 12 hours)\n\n**1. ETHUSDT Cross 3X**\nDirection: Long\nEntry Price: $4577.47\nCurrent Price: $3866.88\nROI: -46.57%\nFound in Channel List\nChannel Id: 1379787390155096105 Channel Name: 🐧┃fj-signals\nMessage Content: **CHR/USDT (long)** 12h chart\n\nEntry: 0,0697 - (market)\n\nTP1: 0,0734\nTP2: 0,0773\nTP3: 0,0837\nTP4: 0,0945\nTP5: 0,1080\nTP6: 0,1290\n\nSL: 0,0634\n\nR:R: 9,44\n<@&1354945711879491767>"
fj_trade_id = 541656519516950




def isSignal(message):

    #question = " **FIL/USDT (long)** 12h chart\n\nEntry:  1,749 - I'm waiting for the resistance breakout (use stop-limit/stop-market order)\n\nTP1: 1,821\nTP2: 1,930\nTP3: 2,083\nTP4: 2,322\nTP5: 2,680\n\nSL: 1,597\n\nR:R: 6,25\n<@&1354945711879491767>"
    question = "TP 2 was reached <@&1354945711879491767>"
    
    question = question.replace(',', '.')

    tp_num = "10"
    trade_amount = '200'

    #tradeFormatOld = '{"symbol":"BTCUSDT","orderList":[{"side":"BUY","price":"60000","qty":"0.5","orderType":"LIMIT","reduceOnly":false,"effect":"GTC","clientId":"c12345","tpPrice":"61000","tpStopType":"MARK","tpOrderType":"LIMIT","tpOrderPrice":"61000.1","slPrice":"59000","slStopType":"LAST","slOrderType":"MARKET"},{"side":"SELL","price":"61000","qty":"0.5","orderType":"LIMIT","reduceOnly":false,"effect":"IOC","clientId":"c12346"}]}'
    #tradeFormat = '{"symbol":"BTCUSDT","orderList":[{"side":"BUY","price":"60000","qty":"0.5","orderType":"LIMIT","reduceOnly":false,"effect":"GTC","clientId":"c12345","slPrice":"59000","slStopType":"LAST","slOrderType":"MARKET"},{"side":"SELL","price":"61000","qty":"0.5","orderType":"MARKET","reduceOnly":false,"effect":"IOC","clientId":"c12346"}]}'
    #contentMessage = f'given that a trade signal message typically looks like the following: \n**FIL/USDT (LONG)** \nLeverage: 10X \nBalance: 5% of capital\nEntry: 2.1289 - (limit order)\nTP1: 2.4175\nTP2: 2.8483\nTP3: 3.4193\nTP4: 4.3273\nSL: 1.8550\nR:R: 8 please look at the following message: {message} and determine if it is a trade signal. If so, please format the signal into the following format: {tradeFormat} be sure to include the take profit (tp) sells and export this in json format but if it is not a trade signal message just repond with the word "false"'
    #contentMessage = f'given that a trade signal message typically looks like the following: \n**FIL/USDT (LONG)** \nLeverage: 10X \nBalance: 5% of capital\nEntry: 2.1289 - (limit order)\nTP1: 2.4175\nTP2: 2.8483\nTP3: 3.4193\nTP4: 4.3273\nSL: 1.8550\nR:R: 8 please look at the following message: {message} and determine if it is a trade signal. If so, please format the signal into the following format: {tradeFormat} take care to note that a long is a buy signal and a short is a sell signal. For the take profit trades treat those as seperate trades and remove the take profit option on the intial trade. however take note that if the first trade is a buy then the take profit trades are sells and if the first trade is a sell then the take profit trades are buys. if {tpNUM} is less than the number of take profit trades only include {tpNUM} take profit trades with the quantities adjusted accordingly. adjust the buy quantities to use {trade_amount} USDT total. adjust the sell quantities of the take profit trades so all of the initial purchase is sold. put all of the trades in an array and export this in python dictionary format but if it is not a trade signal message just repond with the word "false". please do not provide any context and export the dictionary only'
    #content_message = f'given that a trade signal message typically looks like the following: \n**FIL/USDT (LONG)** \nLeverage: 10X \nBalance: 5% of capital\nEntry: 2.1289 - (limit order)\nTP1: 2.4175\nTP2: 2.8483\nTP3: 3.4193\nTP4: 4.3273\nSL: 1.8550\nR:R: 8 please look at the following message: {message} and determine if it is a trade signal. If so, format the signal into the following format: {tradeFormat}. Please note that a long is a buy trade and a short is a sell trade. Treat the take profit trades as seperate trades. the take profit trades should be a "MARKET" order. if the first trade was a buy trade then take profit trades are sell trades and vice versa. if {tpNUM} is less than the number of take profit trades in the message then only include {tpNUM} take profit trades. Adjust the quantity value of the initial trade to use {trade_amount} USDT total. all of the take profit trades qty in the array should equal the qty of the first buy or sell trade in the array. Put all of the trades in an array and export this in python dictionary format. If this is not a trade signal then just respond with the word "false". Do not provide any context and output either "false" or the dictionary format only.'
    
    signal = " \n**FIL/USDT (LONG)** \nLeverage: 10X \nBalance: 5% of capital\nEntry: 2.1289 - (limit order)\nTP1: 2.4175\nTP2: 2.8483\nTP3: 3.4193\nTP4: 4.3273\nSL: 1.8550\nR:R: 8"
    trade_format = '{"symbol":"BTCUSDT","orderList":[{"side":"BUY","price":"60000","qty":"0.5","orderType":"LIMIT","reduceOnly":false,"effect":"GTC","clientId":"c12345","slPrice":"59000","slStopType":"LAST","slOrderType":"MARKET"},{"side":"SELL","price":"61000","qty":"0.25","orderType":"MARKET","reduceOnly":true,"effect":"IOC","clientId":"c12346"},{"side":"SELL","price":"61000","qty":"0.25","orderType":"MARKET","reduceOnly":true,"effect":"IOC","clientId":"c12346"}]}'
    
    content_message = f'hey, answer the users question based on the following context: the users question is this: {question} given that a trade signal message typically looks like the following: {signal}. please look at the input and determine if it is a trade signal. If so, format the signal into the following format: {trade_format}. sometimes instead of a "." the auther may use a "," make sure to correct this. take note that a long is a buy trade and a short is a sell trade. Treat the take profit trades as separate trades. the take profit trades should be a "LIMIT" order. if the first trade was a buy trade then take profit trades are sell trades and vice versa. Adjust the quantity value of the initial trade to use {trade_amount} USDT total. adjust the sell trades so the summed total qty of the sell trades equals the qty of the buy trade if {tp_num} is less than the number of sell trades then reduce the sell trades to equal the first {tp_num} trades and adjust the quantities and prices accordingly. Put all of the trades in an array and export this in python dictionary format. If this is not a trade signal then just respond with the word "false". Do not provide any other output except "false" or the formatted result.'

    
    response = llm.chat.completions.create(
    messages=[{"role": "user", "content": content_message}]
)

    #logger.info(response.choices[0].message.content)
    print(response.choices[0].message.content)
    
    
    '''
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv('OPENROUTER_KEY'),
    )
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=[
            {
            "role": "user",
            "content": content_message
            }
        ]
    )

    print(completion.choices[0].message.content)
    '''
    
    
    '''
    api_key = os.getenv('OPENROUTER_KEY')
    print(api_key)
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        data=json.dumps({
            "model": "deepseek/deepseek-chat-v3.1:free", # Optional
            "messages": [
            {
                "role": "user",
                "content": contentMessage
            }
            ]
        })
    )
    jsonn = json.loads(response.text)
    print(response)
    print(response.text)
    '''
    return response.choices[0].message.content

isSignal(fj_trade)

