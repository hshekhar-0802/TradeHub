#Created by 2022CS51138 & 2022CS11091


from flask import Flask, render_template, request, redirect, session,jsonify
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date, timedelta
import pandas as pd
from jugaad_data.nse import bhavcopy_save, bhavcopy_fo_save
from jugaad_data.nse import stock_df
from bokehh import graph, multipleplot
from jugaad_data.nse import NSELive
import os
from news import getnews

app=Flask(__name__)
app.secret_key = 'your_secret_key' 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80), nullable=False)
    username=db.Column(db.String(80), unique=True, nullable=False)
    password=db.Column(db.String(80), nullable=False)
    email=db.Column(db.String(80), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    

@app.route("/")
def hello():
    return render_template('home.html')

@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method=='POST':
        email=request.form.get('email')
        name=request.form.get('name')
        username=request.form.get('username')
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            return "Username or email already exists. Please choose another one."
        password=request.form.get('password')
        dob_str=request.form.get('dob')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        user=User(name=name,username=username,password=password,email=email,dob=dob)
        db.session.add(user)
        db.session.commit()
    return render_template('signup.html')

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect(f'/dash/{username}')
        else:
            error = "Invalid username or password. Please try again."
            return render_template('signin.html', error=error)
    return render_template('signin.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/signin")

@app.route("/dash/<username>")
def dashboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect("/signin")
    user = User.query.filter_by(username=username).first()
    if user:
        print("User:", user)
        titles,descriptions, urls, url_to_images=getnews()
        return render_template('dash.html', user=user,titles=titles,descriptions=descriptions,urls=urls,url_to_images=url_to_images, num=len(titles))
    else:
        return "User not found"

@app.route("/allstocks/<sym>/<timeframe>")
def allstocks(sym,timeframe):
    yr=datetime.now().year
    mo=datetime.now().month
    din=datetime.now().day
    gap=0
    if(timeframe=='1Y'):
        gap=1*365
    elif(timeframe=='All'):
        gap=40*365
    elif(timeframe=='20Y'):
        gap=20*365
    elif(timeframe=='10Y'):
        gap=10*365
    elif(timeframe=='5Y'):
        gap=5*365
    elif(timeframe=='6M'):
        gap=6*30
    elif(timeframe=='3M'):
        gap=3*30
    elif(timeframe=='1M'):
        gap=1*30
    elif(timeframe=='1W'):
        gap=7
    elif(timeframe=='1D'):
        gap=1
    current_date = datetime.now()
    delta = timedelta(days=gap)
    past_date = current_date - delta
    fyr=past_date.year
    fmo=past_date.month
    fdin=past_date.day
    nifty=pd.read_csv('nifty50.csv')
    stock_symbols=nifty['Symbol'].to_list()
    df=stock_df(symbol=sym, from_date=date(fyr,fmo,fdin),to_date=date(yr,mo,din), series="EQ")
    first=df.head(1)['CLOSE'].values[0]
    last=df.tail(1)['CLOSE'].values[0]
    color_graph='red'
    if(first>=last):
        color_graph='green'
    dates=df['DATE']
    open=df['OPEN']
    df=df['CLOSE']
    script, div=graph(dates,df,open,sym,color_graph)
    n = NSELive()
    stock_data = n.stock_quote(sym)
    liveprice=stock_data['priceInfo']['lastPrice']
    open_price = stock_data['priceInfo']['open']
    high_price = stock_data['priceInfo']['intraDayHighLow']['max']
    low_price = stock_data['priceInfo']['intraDayHighLow']['min']
    volume = stock_data['preOpenMarket']['totalTradedVolume']
    pe_ratio = stock_data['metadata']['pdSymbolPe']
    market_cap = stock_data['priceInfo']['lastPrice'] * stock_data['securityInfo']['issuedSize']
    week_high = stock_data['priceInfo']['weekHighLow']['max']
    week_low = stock_data['priceInfo']['weekHighLow']['min']
    company_name= nifty.loc[nifty['Symbol']==sym, 'Company Name'].to_list()[0]
    pricechange=((liveprice-open_price)/open_price)*100
    pricechange=((pricechange*100)//1)/100
    color= "#33ff33"
    sign='+'
    if(pricechange<0):
        color='#ff5733'
        sign=''
    return render_template('allstocks.html',stock_symbols=stock_symbols,script=script,div=div, def_symbol=sym, live=liveprice, open=open_price, high=high_price, low=low_price, volume=volume, pe=pe_ratio, mktcap=market_cap, company=company_name, wkhigh=week_high, wklow=week_low, change=pricechange, color=color, sign=sign)

@app.route("/accDetails")
def accDetails():
    return render_template('accDetails.html')

@app.route("/compare/<parameter>", methods=['POST','GET'])
def compare(parameter):
    nifty=pd.read_csv('nifty50.csv')
    stock_symbols=nifty['Symbol'].to_list()
    df=stock_df(symbol='SBIN', from_date=date(2023,1,1),to_date=date(2024,1,1), series="EQ")
    script, div= multipleplot(['SBIN'],[df['DATE']],[df[parameter]], parameter)
    if request.method=='POST':
        selected_stocks = request.form.getlist('stocks')
        dob_str=request.form.get('from_date')
        fromdate= datetime.strptime(dob_str, '%Y-%m-%d').date()
        dob_str=request.form.get('to_date')
        todate = datetime.strptime(dob_str, '%Y-%m-%d').date()
        dates=[]
        data=[]
        for stock in selected_stocks:
            df=stock_df(symbol=stock, from_date=fromdate,to_date=todate, series="EQ")
            dates.append(df['DATE'])
            data.append(df[parameter])
        script, div=multipleplot(selected_stocks,dates,data,parameter)
        return render_template("compare.html",stocks=stock_symbols,script=script, div=div, parameter=parameter)
    return render_template("compare.html",stocks=stock_symbols,script=script, div=div,parameter=parameter)
   
@app.route("/filters",methods=['GET','POST'])
def filters():
    df=pd.read_csv('niftydata.csv')
    df=df.reset_index(drop=True)
    df = df.drop('Unnamed: 0', axis=1)
    html_table = df.to_html( index=False)
    if request.method=='POST':
        openhigh=(request.form.get('openhigh'))
        openlow=(request.form.get('openlow'))
        wkhighhigh=(request.form.get('wkhighhigh'))
        wkhighlow=(request.form.get('wkhighlow'))
        wklowhigh=request.form.get('wklowhigh')
        wklowlow=request.form.get('wklowlow')
        ltphigh=request.form.get('ltphigh')
        ltplow=request.form.get('ltplow')
        mktcaphigh=request.form.get('mktcaphigh')
        mktcaplow=request.form.get('mktcaplow')
        pehigh=request.form.get('pehigh')
        pelow=request.form.get('pelow')
        openhigh = int(openhigh) if openhigh and openhigh != 'None' else 'None'
        openlow = int(openlow) if openlow and openlow != 'None' else 'None'
        wkhighhigh = int(wkhighhigh) if wkhighhigh and wkhighhigh != 'None' else 'None'
        wkhighlow = int(wkhighlow) if wkhighlow and wkhighlow != 'None' else 'None'
        wklowhigh = int(wklowhigh) if wklowhigh and wklowhigh != 'None' else 'None'
        wklowlow = int(wklowlow) if wklowlow and wklowlow != 'None' else 'None'
        ltphigh = int(ltphigh) if ltphigh and ltphigh != 'None' else 'None'
        ltplow = int(ltplow) if ltplow and ltplow != 'None' else 'None'
        mktcaphigh = int(mktcaphigh) if mktcaphigh and mktcaphigh != 'None' else 'None'
        mktcaplow = int(mktcaplow) if mktcaplow and mktcaplow != 'None' else 'None'
        pehigh = int(pehigh) if pehigh and pehigh != 'None' else 'None'
        pelow = int(pelow) if pelow and pelow != 'None' else 'None'
        if not(openhigh=='None'):
            df=df[(df['Open']<=openhigh)]
        if not(openlow=='None'):
            df=df[(df['Open']>=openlow)]
        if not(wkhighhigh=='None'):
            df=df[(df['52 Wk High']<=wkhighhigh)]
        if not(wkhighlow=='None'):
            df=df[(df['52 Wk High']>=wkhighlow)]
        if not(wklowhigh=='None'):
            df=df[(df['52 Wk Low']<=wklowhigh)]
        if not(wklowlow=='None'):
            df=df[(df['52 Wk Low']>=wklowlow)]
        if not(ltphigh=='None'):
            df=df[(df['LTP']<=ltphigh)]
        if not(ltplow=='None'):
            df=df[(df['LTP']>=ltplow)]
        if not(mktcaphigh=='None'):
            df=df[(df['Market Capital']<=mktcaphigh)]
        if not(mktcaplow=='None'):
            df=df[(df['Market Capital']>=mktcaplow)]
        if not(pehigh=='None'):
            df=df[(df['PE Ratio']<=pehigh)]
        if not(pelow=='None'):
            df=df[(df['PE Ratio']>=pelow)]
        df.to_csv("test.csv")
        html_table = df.to_html( index=False)
        return render_template("filters.html", table=html_table, data_len=len(df))
    return render_template("filters.html", table=html_table, data_len=len(df))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    if not(os.path.exists('niftydata.csv')):
        nifty=pd.read_csv('nifty50.csv')
        stock_symbols=nifty['Symbol'].to_list()
        dict={'Symbols':[],'Open':[],'52 Wk High':[],'52 Wk Low':[],'LTP':[],'Market Capital':[],'PE Ratio':[]}
        for symbol in stock_symbols:
            n = NSELive()
            stock_data = n.stock_quote(symbol)
            dict['Symbols'].append(symbol)
            dict['Open'].append(stock_data['priceInfo']['open'])
            dict['52 Wk High'].append( stock_data['priceInfo']['weekHighLow']['max'])
            dict['52 Wk Low'].append( stock_data['priceInfo']['weekHighLow']['min'])
            dict['LTP'].append(stock_data['priceInfo']['lastPrice'])
            dict['Market Capital'].append(stock_data['priceInfo']['lastPrice'] * stock_data['securityInfo']['issuedSize'])
            dict['PE Ratio'].append( stock_data['metadata']['pdSymbolPe'])
            print("Getting "+symbol+" data")
        df=pd.DataFrame(dict)
        df=df.reset_index(drop=True)
        df.to_csv('niftydata.csv')
    app.run(debug=True)
