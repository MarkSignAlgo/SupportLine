import pandas as pd
import requests


def api_iex(stock):
    """
    function calls the IEX API and returns a pandas df of it.
    Make sure it starts with oldest date
    """
    link='https://cloud.iexapis.com/stable/stock/{}/chart/max?token={YOUR_TOKEN_HERE}'.format(stock.lower())
    data=requests.get(link)
    try:
        dataj=data.json()
    except:
        return 'Error in get_data_api for {}.'.format(stock)
    data_list=list()
    for i in dataj:
        data_list.append([i['date'], i['open'], i['close'], i['low'], i['high'], i['volume']])
    df=pd.DataFrame(data_list, columns=['date', 'open', 'close', 'low', 'high', 'volume'])
    return df


def sline(df, min_per, holding, loss_cut):
    #checking is done over 6mo+
    positions=list()
    recent=list()
    i=0
    while i<(len(df)-min_per-holding-2):
        try:
            local=df[i:i+min_per]
            local=local.reset_index(drop=True)
            min=local['close'].min()
            #getting the index of the min value
            min_index=local.index[local['close']==min].values.tolist()
            #IDENTIFYING the support points
            support=0
            if len(min_index)==1:
                mins=list()
                for k in range(len(local)):
                    if k<min_index[0]-10 or k>min_index[0]+10:
                        if local['close'].iloc[k]>0.99*min and local['close'].iloc[k]<1.01*min:
                            support=support+1
            else:
                #already having at least 2 values, min is the value to compare to and add to a position
                support=support+1
            #identifying the BUY point
            if support>2:
                if local['close'].iloc[-1]<min*1.03 and local['close'].iloc[-1]>min:
                    #initiate the BUY position and hold for HOLDING period
                    perf=df['close'].iloc[i+min_per+holding]/df['close'].iloc[i+min_per]-1
                    if perf<(-1*loss_cut) or perf==(-1*loss_cut):
                        #identify the selling point
                        for kk in range(holding):
                            pperf=df['close'].iloc[i+min_per+kk]/df['close'].iloc[i+min_per]-1
                            if pperf<(-1*loss_cut) or pperf==(-1*loss_cut):
                                positions.append([i, i+min_per, perf])
                                i=i+min_per+kk
                                break
                            if kk==holding-1:
                                i=i+1
                    else:
                        positions.append([i, i+min_per, perf])
                        i=i+min_per
                else:
                    i=i+1
            else:
                i=i+1
        except:
            full_rez={'positions':positions, 'recent':recent, 'message':'Error at step {}'.format(i)}
            return full_rez
    full_rez={'positions':positions, 'recent':recent, 'message':''}
    return full_rez
  
  
  def sline_opt(df):
    wrap_rez={'opportunity':'', 'optimum_values':[], 'errors':[]}
    errors=list()
    all_rez=list()
    for k in range(20, 120, 1):
        for j in range(7, 50, 1):
            print(k, j);
            p=sline(df, k, j, 0.05)
            if p['message']=='':
                pp=p['positions']
                all_rez.append([calc(pp), k, j, 0.05])
            else:
                errors.append(p['message'])
    all_rez.sort(key=lambda kk: kk[0], reverse=True)
    #buiding the optimum values string
    wrap_rez['optimum_values']=','.join([str(all_rez[0][1]), str(all_rez[0][2]), str(all_rez[0][3])])
    opt_run=sline(df, all_rez[0][1], all_rez[0][2], all_rez[0][3])
    wrap_rez['opportunity']=opt_run
    wrap_rez['errors']=errors
    return wrap_rez

#UTILITIES
def calc(pp):
    r=1
    for i in pp:
        r=r*(1+i[2])
    r=r-1
    return r
  
 
