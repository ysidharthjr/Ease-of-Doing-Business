import pandas as pd
from pandas_datareader import wb
import datetime
import numpy as np
from sklearn import linear_model
from scipy import stats
from sklearn.linear_model import LinearRegression 
from collections import Counter
import pycountry
import requests
import re
import math

now = datetime.datetime.now()
strtyear=2005

'''Linear Regression(Returns mean if less than 5 data points)'''
def lnreg(y,p):
    x11= []
    y11=[]
    j=-1
    for i in y:
        j=j+1
        if np.isnan(i)==False:
            y11.append(i)
            x11.append(j)
    x1=np.array(x11)        
    y1=np.array(y11)
    if len(y1)>4:
        m=((x1.mean()*y1.mean())-(x1*y1).mean())/((x1.mean()*x1.mean())-(x1*x1).mean())
        b=y1.mean()-(m*x1.mean())
        return (m*p)+b
    else:
        return y1.mean()
    

clmns=[] #Stores names of all the columns used
'''Initiating Dataset with ease of doing business'''
indic="Ease of Doing Business"
clmns.append(indic)
maindata=wb.download(country=u"all", indicator="IC.BUS.EASE.XQ",start=strtyear, end=now.year) 
maindata.columns=[indic]
maindata['Country']=[i[0] for i in maindata.index]
maindata['Year']=[i[1] for i in maindata.index]
maindata['Year']=maindata['Year'].apply(int)
maindata = maindata.groupby("Country").transform(lambda x: x.iloc[::-1])
maindata['Country']=[i[0] for i in maindata.index]
maindata=maindata[["Country","Year",indic]]
maindata=maindata[658:]
maindata[indic]=maindata[indic].replace(0, np.nan)
maindata[indic] = maindata.groupby("country")[indic].transform(lambda x: x.fillna(x.mean()))

'''Function to append Features'''
def featureappnd(ind,nm,ft):
    clmns.append(nm)
    tmpdt=wb.download(country=u"all", indicator=ind,start=strtyear, end=now.year)
    tmpdt.columns=[nm]
    tmpdt['Country']=[i[0] for i in tmpdt.index]
    tmpdt['Year']=[i[1] for i in tmpdt.index]
    tmpdt['Year']=tmpdt['Year'].apply(int)
    tmpdt =tmpdt.groupby("Country").transform(lambda x: x.iloc[::-1])
    tmpdt['Country']=[i[0] for i in tmpdt.index]
    tmpdt=tmpdt[["Country","Year",nm]]
    tmpdt=tmpdt[658:]
    tmpdt[nm]=tmpdt[nm].replace(0, np.nan)
    if ft=="reg":
        tmpdt[nm] = tmpdt.groupby("country")[nm].transform(lambda x: x.fillna(lnreg(x,tmpdt['Year']-strtyear))) 
    elif ft=="mean":
        tmpdt[nm] = tmpdt.groupby("country")[nm].transform(lambda x: x.fillna(x.mean()))
    elif ft=="sdp":
        tmpdt[nm] = tmpdt.groupby("country")[nm].transform(lambda x: x.fillna(x.mean()+(tmpdt["Year"]-2010)*0.5*np.std(x)))
    elif ft=="sdn":
        tmpdt[nm] = tmpdt.groupby("country")[nm].transform(lambda x: x.fillna(x.mean()-(tmpdt["Year"]-2010)*0.5*np.std(x)))
    global maindata
    maindata=pd.merge(maindata,tmpdt)

'''Function to test Features with various filling methods'''
def featuretest(ind,nm):   
    tmpdt=wb.download(country=u"all", indicator=ind,start=strtyear, end=now.year)
    tmpdt.columns=[nm]
    tmpdt['Country']=[i[0] for i in tmpdt.index]
    tmpdt['Year']=[i[1] for i in tmpdt.index]
    tmpdt['Year']=tmpdt['Year'].apply(int)
    tmpdt =tmpdt.groupby("Country").transform(lambda x: x.iloc[::-1])
    tmpdt['Country']=[i[0] for i in tmpdt.index]
    tmpdt=tmpdt[["Country","Year",nm]]
    tmpdt=tmpdt[658:]
    tmpdt[nm]=tmpdt[nm].replace(0, np.nan)
    tmpdt["regress"] = tmpdt.groupby("country")[nm].transform(lambda x: x.fillna(lnreg(x,tmpdt['Year']-strtyear))) 
    tmpdt["mean"] = tmpdt.groupby("country")[nm].transform(lambda x: x.fillna(x.mean()))
    tmpdt["SD+"] = tmpdt.groupby("country")[nm].transform(lambda x: x.fillna(x.mean()+(tmpdt["Year"]-2010)*0.5*np.std(x)))
    tmpdt["SD-"] = tmpdt.groupby("country")[nm].transform(lambda x: x.fillna(x.mean()-(tmpdt["Year"]-2010)*0.5*np.std(x)))
    return tmpdt

testy=featuretest("NY.GDP.MKTP.CD","GDP total")

'''Getting HDI'''
clmns.append("HDI")
resp=requests.get("http://ec2-54-174-131-205.compute-1.amazonaws.com/API/HDRO_API.php/indicator_id=137506")

hdi=pd.DataFrame()
hdi['index']=[]
hdi['137506']=[]
hdi["Country"]=[]

for i in resp.json()['indicator_value']:
    for j in resp.json()['indicator_value'][i]:
        jj=pd.DataFrame(resp.json()['indicator_value'][i]).reset_index()
        jj['Country']=i
        hdi=pd.concat([hdi,jj],ignore_index=True)

hdi.columns=["Year","HDI","Alpha3",]


'''Features Appends (Economic)'''
featureappnd("NY.GDP.MKTP.CD","GDP total","reg")
featureappnd("NY.GDP.PCAP.PP.CD","GDP per Capita","reg")
featureappnd("NY.GDP.MKTP.KD.ZG","GDP growth","reg")
featureappnd("NE.GDI.TOTL.ZS","Gross capital formation","reg")
featureappnd("NY.GNP.PCAP.CD","GNI per capita","reg")
featureappnd("SL.TLF.ACTI.ZS","Labor force participation","reg")
featureappnd("NE.TRD.GNFS.ZS","Trade (% of GDP)","reg")
featureappnd("NV.SRV.TOTL.ZS","Services, value added(% of GDP)","reg")
featureappnd("NE.IMP.GNFS.ZS","Imports of goods and services (% of GDP)","reg")
featureappnd("TM.VAL.MRCH.CD.WT","Merchandise imports","reg")
featureappnd("NY.GDP.DEFL.KD.ZG","Inflation (annual %)","reg")
featureappnd("NV.IND.TOTL.ZS","Industry value added (% of GDP)","reg")
featureappnd("PA.NUS.FCRF","Official exchange rate","reg")
featureappnd("CM.MKT.LDOM.NO","Listed domestic companies","reg")
featureappnd("IC.CRD.INFO.XQ","Depth of credit information index","reg")
featureappnd("IC.BUS.DISC.XQ","Business extent of disclosure index","reg")
featureappnd("IC.REG.PROC","Start-up procedures to register a business","reg")
featureappnd("IC.REG.DURS","Time required to start a business (days)","reg")
featureappnd("IC.TAX.TOTL.CP.ZS","Total tax rate (% of commercial profits)","reg")

'''Features Appends (Social)'''
featureappnd("SP.POP.TOTL","Population total","reg")
featureappnd("EG.USE.ELEC.KH.PC","Electric power consumption","reg")
featureappnd("SE.XPD.TOTL.GB.ZS","Government expenditure on education","reg")
featureappnd("SE.PRM.ENRR","School enrollment, primary (% gross)","reg")
featureappnd("EN.POP.DNST","Population density","reg")
featureappnd("SP.DYN.LE00.IN","Life expectancy","reg")
featureappnd("SP.URB.TOTL.IN.ZS","Urban population (% of total)","reg")
featureappnd("IT.NET.USER.ZS","Individuals using the Internet","reg")
featureappnd("SL.UEM.TOTL.ZS","Unemployment %","reg")
featureappnd("EG.ELC.ACCS.ZS","Access to electricity (% of population)","reg")
featureappnd("IC.LGL.CRED.XQ","Strength of legal rights index","reg")
featureappnd("IQ.CPA.TRAN.XQ","CPIA transparency","reg") #Corruption

'''Research'''
featureappnd("IP.PAT.RESD","Patent applications, residents","reg")
featureappnd("IP.PAT.NRES","Patent applications, nonresidents","reg")
featureappnd("GB.XPD.RSDV.GD.ZS","Research and development expenditure (% of GDP)","reg")
featureappnd("SP.POP.SCIE.RD.P6","Researchers in R&D (per million people)","reg")

'''Logistic Peformance Features'''
featureappnd("LP.LPI.CUST.XQ","Efficiency of customs clearance","reg")
featureappnd("LP.LPI.LOGS.XQ","Competence and quality of logistics","reg")
featureappnd("LP.LPI.TIME.XQ","Punctuality logistics","reg") #Logistics performance index: Frequency with which shipments reach consignee within scheduled or expected time
featureappnd("LP.LPI.ITRN.XQ","Price Arrangement logistics","reg") #Logistics performance index: Ease of arranging competitively priced shipments 
featureappnd("LP.LPI.TRAC.XQ","Track and trace","reg") #Logistics performance index: Ability to track and trace consignments 
featureappnd("LP.LPI.INFR.XQ","Transportation","reg")

'''Medical Features'''
featureappnd("SH.MED.PHYS.ZS","Physician (per 1000 people)","reg")
featureappnd("SH.XPD.CHEX.GD.ZS","Health expenditure per capita","reg")
featureappnd("SH.XPD.CHEX.PC.CD","Current health expenditure (% of GDP)","reg")
featureappnd("SH.STA.OWGH.ZS","Prevalence of overweight","reg")
featureappnd("SH.TBS.INCD","Tuberculosis (per 100,000 people)","reg")
featureappnd("SH.MLR.INCD.P3","Incidence of malaria (per 1,000 population at risk)","reg")
featureappnd("SH.ANM.CHLD.ZS","Prevalence of anemia among children","reg")
featureappnd("SH.STA.DIAB.ZS","Diabetes prevalence","mean")
featureappnd("EN.ATM.PM25.MC.ZS","PM2.5 excess exposure (% of population)","reg")
featureappnd("SH.DTH.COMM.ZS","Cause of death, by communicable diseases","reg")
featureappnd("SH.IMM.IDPT","Immunization, DPT","reg")
featureappnd("SH.SGR.IRSK.ZS","Risk surgical care","reg")
featureappnd("SH.PRV.SMOK","Smoking prevalence","reg")
featureappnd("SH.ALC.PCAP.LI","alcohol consumption per capita","reg")
featureappnd("SH.UHC.SRVS.CV.XD","UHC service coverage index","reg")

'''Geographical Features'''
featureappnd("AG.LND.PRCP.MM","Average precipitation","reg")

'''Main Window GUI'''
feat=pd.DataFrame()
pos=0
ren=0
catval=0
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
def addxvalues():
    def posset(k):
        global pos
        pos=k
    def bpress():
        global feat
        global pos
        text=e.get()
        feat=feat.append(wb.search(text,field='name',case=False))
        feat=feat[:10]
        tk.Button(StartWindowx,text=feat["name"].iloc[0],command=lambda:posset(0)).grid(row=2,column=0,columnspan=3)
        tk.Button(StartWindowx,text=feat["name"].iloc[1],command=lambda:posset(1)).grid(row=3,column=0,columnspan=3)
        tk.Button(StartWindowx,text=feat["name"].iloc[2],command=lambda:posset(2)).grid(row=4,column=0,columnspan=3)
        tk.Button(StartWindowx,text=feat["name"].iloc[3],command=lambda:posset(3)).grid(row=5,column=0,columnspan=3)
        tk.Button(StartWindowx,text=feat["name"].iloc[4],command=lambda:posset(4)).grid(row=6,column=0,columnspan=3)
        tk.Button(StartWindowx,text=feat["name"].iloc[5],command=lambda:posset(5)).grid(row=7,column=0,columnspan=3)
        tk.Button(StartWindowx,text=feat["name"].iloc[6],command=lambda:posset(6)).grid(row=8,column=0,columnspan=3)
        tk.Button(StartWindowx,text=feat["name"].iloc[7],command=lambda:posset(7)).grid(row=9,column=0,columnspan=3)
        tk.Button(StartWindowx,text=feat["name"].iloc[8],command=lambda:posset(8)).grid(row=10,column=0,columnspan=3)
        tk.Button(StartWindowx,text=feat["name"].iloc[9],command=lambda:posset(9)).grid(row=11,column=0,columnspan=3)
    global ren
    global catval
    StartWindowx=tk.Toplevel()
    StartWindowx.title("Add Feature") # Change Window TItle
    StartWindowx.geometry('450x400')
    e = tk.Entry(StartWindowx, bd =5) #text
    e.grid(row=0,column=0)

    b=tk.Button(StartWindowx,text='Search',command=bpress)
    b.grid(row=1,column=0)

    f=("+ve Relation","-ve Relation")
    f2=("Economic","Social","Medical","Geographic")
    s=tk.StringVar()
    s.set(f[0]) #set default
    d=tk.OptionMenu(StartWindowx,s,*f) #dropdown
    d.grid(row=0,column=1)
    s1=tk.StringVar()
    s1.set(f2[0])
    d2=tk.OptionMenu(StartWindowx,s1,*f2)
    d2.grid(row=0,column=2)
    rel=s.get()
    catog=s1.get()
    
    if (rel=="+ve Relation"):
        ren=0
    else:
        ren=1
    if (catog=="Economic"):
        catval=14
    elif (catog=="Social"):
        catval=12
    elif (catog=="Medical"):
        catval=18
    else:
        catval=2
    
def uplodbox():
    
    BrowseWindow=tk.Toplevel()
    BrowseWindow.title("Browse")
    l1=tk.Label(BrowseWindow,text="Choose a file")
    l1.grid(row=0)
    t1=tk.Entry(BrowseWindow,bd=5)
    t1.grid(row=1)
    path=''
    def uploadCSV():
        global path
        path=fd.askopenfilename(parent=BrowseWindow,filetypes=[("CSV Files",".csv")])
    b1=tk.Button(BrowseWindow,text="Upload a File",command=uploadCSV)
    b1.grid(row=2)

StartWindow=tk.Tk()
StartWindow.title("SIH(main_page)") # Change Window TItle
StartWindow.geometry('900x600')
StartWindow.configure(background='light blue')
main_frame = tk.Frame(StartWindow)
main_frame.pack(side = tk.LEFT, fill = 'y')
s = ttk.Style()

scrollbar = tk.Scrollbar(main_frame)
scrollbar.pack(side = tk.RIGHT, fill = "y")
features = tk.Label(main_frame,text = "Already added Features(x-axis)", font=("Helvetica", 12), fg = "red")
features.pack()
f_exist=['Ease of Doing Business','GDP total','GDP per Capita','GDP growth','Gross capital formation','GNI per capita','Labor force participation','Trade (% of GDP)','Services, value added(% of GDP)','Imports of goods and services (% of GDP)','Merchandise imports','Inflation (annual %)','Industry value added (% of GDP)','Official exchange rate','Listed domestic companies','Depth of credit information index','Business extent of disclosure index','Start-up procedures to register a business','Time required to start a business (days)','Total tax rate (% of commercial profits)','Population total','Electric power consumption','Government expenditure on education','School enrollment, primary (% gross)','Population density','Life expectancy','Urban population (% of total)','Individuals using the Internet','Unemployment %','Access to electricity (% of population)','Strength of legal rights index CPIA transparency','Patent applications, residents','Patent applications, nonresidents','Research and development expenditure (% of GDP)','Researchers in R&D (per million people)','Efficiency of customs clearance','Competence and quality of logistics','Punctuality logistics','Price Arrangement logistics','Trackntrace','Transportation','Physician (per 1000 people)','Health expenditure per capita','Current health expenditure (% of GDP)','Prevalence of overweight','Tuberculosis (per 100,000 people)','Incidence of malaria (per 1,000 population at risk)','Prevalence of anemia among children','Diabetes prevalence','PM2.5 excess exposure (% of population)','Cause of death, by communicable diseases','Immunization, DPT','Risk surgical care','Smoking prevalence','alcohol consumption per capita','UHC service coverage index','Average precipitation','HDI'
]
list1=tk.Listbox(main_frame,yscrollcommand = scrollbar.set, width=40, height=40, font=("Helvetica", 12), background = 'light blue',fg = 'black')
for x in f_exist:
    list1.insert(tk.END,x)
scrollbar.config(command = list1.yview)
def exitall():
    StartWindow.destroy()
list1.pack()
b1=tk.Button(StartWindow,text="Add more data in feature",width=20,font=("Helvetica", 12), height = 5, fg = "red",command=addxvalues)
b1.pack()
b1.place(bordermode=tk.OUTSIDE,x = 500, y = 30)
b2=tk.Button(StartWindow,text="Add Company Features", width = 20,font=("Helvetica", 12), height = 5, fg = "blue",command=uplodbox)
b2.pack()
b2.place(bordermode=tk.OUTSIDE,x = 700 , y = 30)
b3=tk.Button(StartWindow,text="Compute",width = 20,font=("Helvetica", 12), height = 5,command=exitall)
b3.pack(side = tk.BOTTOM)
b3.place(bordermode=tk.OUTSIDE, x =600, y = 230)
s.theme_use('clam')
StartWindow.mainloop()
featureappnd(feat["id"].iloc[pos],feat["name"].iloc[pos],"reg")


'''Alph 3 Extraction'''
def alpha_3(x):
    try:
        a=pycountry.countries.get(name=x).alpha_3
        return a
    except:
        a=None
    try:
        a=pycountry.countries.get(official_name=x).alpha_3
        return a
    except:
        a=None
    x=re.findall(r"[\w']+", x)[0]
    try:
        a=pycountry.countries.get(name=x).alpha_3
        return a
    except:
        a=None
    if (x=="Iran"):
        return "IRN"
    if (x=="Bolivia"):
        return "BOL"
    if (x=="Hong"):
        return "HKG"
    if (x=="Venezuela"):
        return "VEN"
    if (x=="Korea"):
        return "ROK"
    if (x=="Vietnam"):
        return "VNM"
    return a




'''HDI Merge'''
maindata["Alpha3"]=maindata["Country"].apply(lambda x:alpha_3(x))
maindata["Year"]=maindata["Year"].apply(int)
hdi["Year"]=hdi["Year"].apply(int)
FinalData=pd.merge(maindata,hdi,how='left',on=["Alpha3","Year"])    
FinalData["HDI"] = FinalData.groupby("Country")["HDI"].transform(lambda x: x.fillna(lnreg(x,FinalData['Year']-strtyear)))
FinalData.drop(["Alpha3"],axis=1,inplace=True)

FinalData =FinalData[pd.notna(FinalData['HDI'])]
FinalData =FinalData[pd.notna(FinalData['Gross capital formation'])]
FinalData =FinalData[pd.notna(FinalData['Ease of Doing Business'])]
FinalData =FinalData[pd.notna(FinalData['GNI per capita'])]
FinalData =FinalData[pd.notna(FinalData['Labor force participation'])]
FinalData =FinalData[pd.notna(FinalData['Services, value added(% of GDP)'])]
FinalData =FinalData[pd.notna(FinalData['Efficiency of customs clearance'])]
FinalData =FinalData[pd.notna(FinalData['Physician (per 1000 people)'])]
FinalData=FinalData.reset_index()
FinalData.drop(["index"],axis=1,inplace=True)
FinalData.to_csv("FinalDataFrame.csv")
FinalData=FinalData.fillna(0)

FinalDataNorm=FinalData[["Country","Year"]]

def normscaling(col,wtg,trd):
    FinalDataNorm[col]=FinalData.groupby("Year")[col].apply(lambda x:abs((((x-x.min())/(x.max()-x.min()))*wtg)-trd))
    
def lnscaling(col,wtg,trd):
    FinalDataNorm[col]=FinalData.groupby("Year")[col].apply(lambda x:abs((((np.log(x)-np.log(max(x.min(),1)))/(np.log(x.max())-np.log(max(x.min(),1))))*wtg)-trd))
    
    
'''Weihts scaling'''
ew=14
sw=12
rw=4
lw=10
mw=18
gw=2

normscaling("Ease of Doing Business",ew,1)
lnscaling("GDP total",ew,0)
lnscaling("GDP per Capita",ew,0)
normscaling("GDP growth",ew,0)
normscaling("Gross capital formation",ew,0)
lnscaling("GNI per capita",ew,0)
normscaling("Labor force participation",ew,0)
normscaling("Trade (% of GDP)",ew,0)
normscaling("Services, value added(% of GDP)",ew,0)
normscaling("Imports of goods and services (% of GDP)",ew,0)
lnscaling("Merchandise imports",ew,0)
normscaling("Inflation (annual %)",ew,0)
normscaling("Industry value added (% of GDP)",ew,0)
lnscaling("Official exchange rate",ew,1)
normscaling("Listed domestic companies",ew,0) #revisit
normscaling("Depth of credit information index",ew,0)
normscaling("Business extent of disclosure index",ew,0)
normscaling("Start-up procedures to register a business",ew,1)
normscaling("Time required to start a business (days)",ew,1)
normscaling("Total tax rate (% of commercial profits)",ew,1)

lnscaling("Population total",sw,0)
lnscaling("Electric power consumption",sw,0)
normscaling("Government expenditure on education",sw,0)
normscaling("School enrollment, primary (% gross)",sw,0)
lnscaling("Population density",sw,0)
normscaling("Life expectancy",sw,0)
normscaling("Urban population (% of total)",sw,0)
normscaling("Individuals using the Internet",sw,0)
normscaling("Unemployment %",sw,0)
normscaling("Access to electricity (% of population)",sw,0)
normscaling("Strength of legal rights index",sw,0)
normscaling("CPIA transparency",sw,0)
lnscaling("Patent applications, residents",rw,0)
lnscaling("Patent applications, nonresidents",rw,0)
normscaling("Research and development expenditure (% of GDP)",rw,0)
lnscaling("Researchers in R&D (per million people)",rw,0)
normscaling("Efficiency of customs clearance",lw,0)
normscaling("Competence and quality of logistics",lw,0)
normscaling("Punctuality logistics",lw,0)

normscaling("Price Arrangement logistics",lw,0)
normscaling("Track and trace",lw,0)
normscaling("Transportation",lw,0)
normscaling("Physician (per 1000 people)",mw,0)
normscaling("Health expenditure per capita",mw,0)
lnscaling("Current health expenditure (% of GDP)",mw,0)
normscaling("Prevalence of overweight",mw,0)
normscaling("Tuberculosis (per 100,000 people)",mw,0) #Just over 1000 
normscaling("Incidence of malaria (per 1,000 population at risk)",mw,0)
normscaling("Prevalence of anemia among children",mw,0)
normscaling("Diabetes prevalence",mw,0)
normscaling("PM2.5 excess exposure (% of population)",mw,0)
normscaling("Cause of death, by communicable diseases",mw,0)
normscaling("Immunization, DPT",mw,1) # check again
normscaling("Risk surgical care",mw,0)
normscaling("Smoking prevalence",1,0)
normscaling("alcohol consumption per capita",1,0)
normscaling("UHC service coverage index",mw,0)
normscaling("Average precipitation",gw,0) # just above 3000
normscaling("HDI",sw,0)
normscaling(feat["name"].iloc[pos],catval,int(ren))

FinalDataNorm=FinalDataNorm.replace(np.inf,1)
FinalDataNorm["Official exchange rate"]=FinalDataNorm["Official exchange rate"].mask(FinalDataNorm["Official exchange rate"]>1,1)

FinalDataNorm["Country Market Rating"]=FinalDataNorm.drop(['Country','Year'], axis=1).sum(axis=1)
if "Country Market Rating Final" in clmns: clmns.remove("Country Market Rating Final")
if "Country Market Rank" in clmns: clmns.remove("Country Market Rank")
def regtrnd(y):
    x11= []
    y11=[]
    j=-1
    for i in y:
        j=j+1
        if np.isnan(i)==False:
            y11.append(i)
            x11.append(j)
    x1=np.array(x11)        
    y1=np.array(y11)
    m=((x1.mean()*y1.mean())-(x1*y1).mean())/((x1.mean()*x1.mean())-(x1*x1).mean())
    return m

FinalDataNorm["Index Trend"] = FinalDataNorm.groupby("Country")["Country Market Rating"].transform(lambda x: regtrnd(x)) 
IndexList=FinalDataNorm[FinalDataNorm['Year']==2017] #Select The Year or Cycle
IndexList["Index Trend"]=IndexList["Index Trend"].transform(lambda x:abs((((x-x.min())/(x.max()-x.min()))*20)))
IndexRank=IndexList.filter(["Country","Country Market Rating","Index Trend"])
IndexRank["Country Market Rating Final"]=IndexRank.drop(['Country'], axis=1).sum(axis=1)
IndexRank=IndexRank.filter(["Country","Country Market Rating Final"])
IndexRank["Country Market Rank"]=IndexRank["Country Market Rating Final"].rank(ascending=False)


from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
df=FinalData
df1=df
dfx=df1.fillna(0)
df1std = stats.zscore(dfx[clmns])

kmeans = KMeans(n_clusters=10, random_state=0).fit(df1std)
labels = kmeans.labels_

df1['clusters'] = labels
yeardf=df1[df1["Year"]==2017]
yeardf = yeardf.filter(['Country', 'clusters'])

yeardf=yeardf[["clusters","Country"]]
yeardf.set_index('clusters',inplace=True)
yeard=yeardf.transpose()
yeard=yeard.groupby(yeard.columns.values, axis=1).agg(lambda x: x.values.tolist()).sum().apply(pd.Series).T.sort_values(0)
yeard=yeard.fillna("")
df1 = df1[df1["Year"]==2017]

ClustMerge=pd.merge(IndexRank,df1,how="left",on="Country")
clmns.append("Country Market Rating Final")
clmns.append("Country Market Rank")

'''GUI Axis Choice'''
value=0
def doNothing():
  global value
  value=s.get()

StartWindow=tk.Tk()
StartWindow.title("Smart_India_Hackathon") # Change Window TItle
StartWindow.geometry('250x150')
def destr():
    StartWindow.destroy()
b=tk.Button(StartWindow,text='Click',command=destr)
b.grid(row=2,column=0,columnspan=2)

l1=tk.Label(StartWindow,text="XAxis")
l1.grid(row=0,column=0)
xlist=clmns #input list dropdown xaxis
xselected=tk.StringVar()
xselected.set(xlist[60]) #set default
xOp=tk.OptionMenu(StartWindow,xselected,*xlist) #dropdown
xOp.grid(row=0,column=1)

l2=tk.Label(StartWindow,text="YAxis")
l2.grid(row=1,column=0)
ylist=clmns
yselected=tk.StringVar()
yselected.set(ylist[0])
yOp=tk.OptionMenu(StartWindow,yselected,*ylist)
yOp.grid(row=1,column=1)
StartWindow.mainloop()

ax=sns.lmplot(xselected.get(), yselected.get(), data=ClustMerge, fit_reg=False, hue="clusters",  scatter_kws={"marker": "D", "s": 100},size=12)
#ax.fig.axes[0].invert_yaxis()
plt.title(xselected.get()+ " vs "+ yselected.get())
plt.xlabel(xselected.get())
plt.ylabel(yselected.get())

def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x']+.02, point['y'], str(point['val']))

label_point(ClustMerge[xselected.get()], ClustMerge[yselected.get()], ClustMerge["Country"], plt.gca())  

ax.savefig("output.png",dpi=500)
from PIL import Image                                                                                
img = Image.open("output.png")
img.show() 

IndexRank=IndexRank.sort_values(['Country Market Rank','Country Market Rating Final'], ascending=[True,True])
IndexRank.to_csv("IndexRank.csv")

import tkinter
import csv
root = tkinter.Tk()

root.geometry('380x750')
with open("IndexRank.csv", newline = "") as file:
   reader = csv.reader(file)

   # r and c tell us where to grid the labels
   r = 0
   for col in reader:
      c = 0
      for row in col:
         # i've added some styling
         label = tkinter.Label(root, width = 12, height = 2, \
                               text = row, relief = tkinter.RIDGE)
         label.grid(row = r, column = c)
         c += 1
      r += 1

root.mainloop()








