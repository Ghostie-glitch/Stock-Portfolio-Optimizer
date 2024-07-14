# Stock-Portfolio-Optimizer

For those who are looking to optimise their stock portfolios. The program created will analyze whatever stocks you have and tell you what percentage of your portfolio should be allocated to that stock. 
the code will return your expected annual return, volatility ( as decimals and you convert it to a percentage) as well as the Sharpe ratio for the portfolio the stock suggests you create. the program also takes it one step further. it will ask you how much you want to invest you type in the value. It will then tell you how many shares of each stock you can buy given the protfilo it suggested, and the amount of money you want to invest.

How to use the code: 

1) First and foremost this code uses YahooFianance as the database. Therefore if you are looking for Canadian stocks they MUST all end in.TO otherwise the program will not understand what you are looking for.
   for example, if you are looking for the Canadian version of Suncor. You would type in SU.TO **NOT** SU.

2) if you are looking for US stocks then just the ticker will do. For example, Nivida is just NVDA

3) the code is interactive so it will ask you questions and provide  instructions if you have half a brain follow it and the code will work just fine.

4) You will need an API Key to access the US treasury. Use this link. https://fred.stlouisfed.org/docs/api/api_key.html
