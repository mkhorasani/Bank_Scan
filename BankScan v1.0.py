from tabula import read_pdf
import re
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()
import PyPDF2
from dateutil import parser
from fpdf import FPDF
import locale
locale.setlocale(locale.LC_ALL,'')
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import timeit


### Data Frame ###

df = read_pdf("C:/Users/Mohammad Khorasani/Desktop/BS.pdf", pages='all')


### Finding Column Names ###

columns = []

for col in df.columns:
    columns.append(col)


### Finding Date Column ###

date_column = ''
date_key_words = ['date']

for i in range(0,len(columns)):
	if any(x in columns[i].lower() for x in date_key_words):
		date_column = i
		break


### Finding Balance Column ###

balance_column = ''
balance_key_words = ['balance']

for i in range(0,len(columns)):
	if any(x in columns[i].lower() for x in balance_key_words):
		balance_column = i
		break


### Finding Description Column ###

description_column = ''
description_key_words = ['description','narrat','particular','service','remark']

for i in range(0,len(columns)):
	if any(x in columns[i].lower() for x in description_key_words):
		description_column = i
		break
	    
	    
### Finding Debit Column ###

debit_column = ''
debit_key_words = ['debit','withdraw']

for i in range(0,len(columns)):
	if any(x in columns[i].lower() for x in debit_key_words):
		debit_column = i
		break
	    

### Finding Credit Column ###

credit_column = ''
credit_key_words = ['credit','deposit']

for i in range(0,len(columns)):
	if any(x in columns[i].lower() for x in credit_key_words):
		credit_column = i
		break


### Extracting Text from PDF ###

pdf_file = open("C:/Users/Mohammad Khorasani/Desktop/BS.pdf", 'rb')
read_pdf = PyPDF2.PdfFileReader(pdf_file)
no_pages = read_pdf.getNumPages()
page = read_pdf.getPage(0)
page_content = page.extractText()
pdf_file.close()


### Appending Multiple Description Rows ###

dropped_rows = []

for i in range(0,len(df)):
    if(str(df.iloc[i][date_column]) == 'nan'):
        k = i
        while(str(df.iloc[k][date_column]) == 'nan'):
            k += 1
        for j in range(i,k):
            df.iloc[i-1][description_column] += (' ' + df.iloc[j][description_column])
        for z in range(i,k):
            dropped_rows.append(z)

dropped_rows2 = []

[dropped_rows2.append(x) for x in dropped_rows if x not in dropped_rows2]

for i in range(1,len(dropped_rows2)+1):
    df = df.drop(df.index[dropped_rows2[-i]])


### Date ###

date_array = []

for i in range(0,len(df)):

    try:
        if str(df.iloc[i][date_column]) != 'nan':
            df.iloc[i][date_column] = parser.parse(df.iloc[i][date_column])
            df.iloc[i][date_column] = df.iloc[i][date_column].strftime("%d %b %Y")
    except ValueError:
        continue
    except TypeError:
        continue

    date_array.append(df.iloc[i][date_column])
    

### Start Date ###

sdate = df.iloc[0][date_column]

try:
    sdate = parser.parse(sdate)
    sdays = sdate
    sdate = sdate.strftime("%d %b %Y")
except ValueError:
    sdate = sdate
except TypeError:
    sdate = sdate


### End Date ###

edate = df.iloc[len(df)-1][date_column]

try:
    edate = parser.parse(edate)
    edays = edate
    edate = edate.strftime("%d %b %Y")
except ValueError:
    edate = edate
except TypeError:
    edate = edate


### Time Delta ###

try:
    time_delta = edays - sdays
    time_delta = time_delta.days
except TypeError:
    time_delta = 'Unknown'
except ValueError:
    time_delta = 'Unknown'    


### Debit ###

debit_array = [] 

for i in range(0,len(df)):
    if (',' in str(df.iloc[i][debit_column])) == True:
        df.iloc[i][debit_column] = re.sub(',','',df.iloc[i][debit_column])

    if str(df.iloc[i][debit_column]) == 'nan':
        df.iloc[i][debit_column] = 0

    try:
        debit_array.append(float(df.iloc[i][debit_column]))
    except ValueError:
        continue
    except TypeError:
        continue
                        
debit = round(sum([x for x in debit_array if str(x) != 'nan']),2)


### Credit ###

credit_array = []

for i in range(0,len(df)):
    if (',' in str(df.iloc[i][credit_column])) == True:
        df.iloc[i][credit_column] = re.sub(',','',df.iloc[i][credit_column])

    if str(df.iloc[i][credit_column]) == 'nan':
        df.iloc[i][credit_column] = 0

    try:
        credit_array.append(float(df.iloc[i][credit_column]))
    except ValueError:
        continue
    except TypeError:
        continue

credit = round(sum([y for y in credit_array if str(y) != 'nan']),2)


### Balance ###

balance_array = []

for i in range(0,len(df)):
    if (',' in str(df.iloc[i][balance_column])) == True:
        df.iloc[i][balance_column] = re.sub(',','',df.iloc[i][balance_column])

    try:
        balance_array.append(float(df.iloc[i][balance_column]))
    except ValueError:
        continue
    except TypeError:
        continue   

### Start Balance ###

sbalance = round(float(re.sub(',','',df.iloc[0][balance_column])),2)


### End Balance ###

ebalance = round(float(re.sub(',','',df.iloc[len(df)-1][balance_column])),2)


### Removing Title Rows ###

title_rows = []

for i in range(0,len(df)):

    try:
        tx = float(df.iloc[i][balance_column])
    except:
        title_rows.append(i)
        
for i in range(0,len(title_rows)):
    df = df.drop(df.index[title_rows[i]])


### Date vs. Balance ###





### Clearing Credit Rows ###

#for i in range(0,len(df)):
#    if(str(df.iloc[i][credit_column]) != 'nan'):
#        df.iloc[i][description_column] = '----C-R-C----'


### Spending Categories ###

## Housing ##

housing = 0

housing_words = ['housing','property',' hoa ','maintenance','maintain','rent',
                 'mortgage','home loan','house loan','appartm','complex','condomin',
                 'service charge','tenant','tenancy','landlord',' land','lease',
                 'plumb','electrician','septic','cleaning',' maid '
              ]

housing_array = []
              
for i in range(0,len(df)):

    housing_array.append(0)

    for housing_word in housing_words:
        
        if ((housing_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):

            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                housing += float(df.iloc[i][debit_column])
                housing_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue

              
## Transportation ##

transportation = 0

transportation_words = ['transport','limo','taxi',' car ',' dmv ','gas','petrol',
                        'parking',' toll','transit',' bus','uber','lyft','careem',
                        'vehicle','metro','subway','tram','underground','carriage',
                        'train','brt','tire','tyre','oil change','car wash',
                        'carwash','rail','mover'
                        ]

transportation_array = []
              
for i in range(0,len(df)):

    transportation_array.append(0)

    for transportation_word in transportation_words:
        
        if ((transportation_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):

            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                transportation += float(df.iloc[i][debit_column])
                transportation_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue
            

## Food ##

food = 0

food_words = ['restau','burger','food','sandwich','steak','grocer','meal',
              'mcdonald','lunch','dinner','breakfast','gourmet','wine',
              'bar','drink','f&b','beverage','nutri','meat','eat','mexic',
              'india','chine','china','thai','korea','vietnam','persia',
              'kebab','doner','shawarma','skewer','asia','mediterran',
              'ethiop','greek','french','ital','pizza','chicken','dairy',
              'claim j','salad','diet','sweet','cake','pastr','cream','ice',
              'tea','fish','vegan','vegeta','turke','turki','bukhar',
              'noodle','spaghet','macaron','barbe',
              'grill','boil','charbroil','broil','cook','chef','fry',
              'toast','roast','bak','scorch','dip','choc','sauce','dine',
              'cafe','chez','chip','starbuc','wendy','plate','beer',
              'liqo','alcohol','kitchen','crust','spic','tandoor','salt',
              'soup','egg','balls','taste','caviar','pan','cuisine','chop',
              'jar','goat','bagel','bread','biscuit','grape','cherry',
              'juice','shake','bbq','pig','crab','frie','lettuce','sheep',
              'ocean','hot','green','leaf','kabob','spina','pot','water',
              'tavern','grove','flavo','hungry','hunger','serve','caf',
              'coffee','dining',' pub ','taco','beef','brisket','smoke','cora',
              'shrimp','lobster','avocado','honey','bacon','banana','orange',
              'tangerine','pepper','butter','cheese','bloat','pie','bowl',
              'brew','bite','candy','cow','pudding','picnic','chop',
              'corn','fed ','prawn','culin','cup ','cut ','drip','donut','dough',
              'nut','crisp','jam','drop','waffl','espress','capac','feast',
              'feed','fig','orchard','fat','horse','potato','dump','fork',
              'spoon','knife','fruit','shack','gelat','vodka','tequil',
              'onion','organic','farm','free range','chill','salami',
              'sausage','healthy','herb','sour','chedder','rice','koffee',
              'stalk','frog','liquid','sizzl','chub','lotus','curry','mint',
              'koshe','iran','afghan','zilla','nectar','nibbl','garden',
              'octopus','olive','shater','tart','pork','pasta','poultr',
              'pretzel','latt','burrito','rabbit','fresh','bean','coco','plum',
              'rib','yard','royal','palace','sea','snack','mouth','stomach',
              'span','slice','splice','sponge','puff','squish','stuff','sugar',
              'swallow','pickl','snail','barn','smoothi','milk','tender',
              'bery','loaf','jasm','lemon','ingred','menu','mocha','cannib',
              'dragon','nose','tease','pigeon','bird','spirit','slaw','thirst',
              'velve','tongue','baba','tropic','tuna','biscot','veg','seed',
              'ranch','brunch','wasabi','yogurt','froze','freez','appleb',
              'arby','buffalo','beavertail','auntie anne','wing','chick',
              'crepe','denny','dunkin','five guy','gloria jean','hardee',
              'harvey','hooter','jimmy john','the keg','kfc','krisp','ceasar',
              'hut','nando','panda','baguet','pollo camp','ponderos','popeye',
              'quizno','red robin','ruby tues','recipe','swensen','t.g.i',
              'tim horton','tony rom','white cast','yoshino','carl','tast',
              'din tai','domino','fast ed','patiss','porche','roost','schnit',
              'shingle inn','zambr','zarraf','a&w','florent','time','dunn',
              'earls','mario','eleph','joey','keg','king','queen','mary brow',
              'panago','tree','salisbur','famil','white spot','the work',
              'mostaz','rostip','jensen','roll','bel cant','flunch','hippo',
              'kochl','nords','wiene','vapian','goody','café','aydar','annapo',
              'bikan','goli','haldira','moshe','murugan','namma','saravan',
              'hoka','the count','rcoket','ramsden','leo burdock','mao',
              'milano','wagam','sushi','zizzi','bewley','caff','esquire',
              'abrake','supermac','spizz','anna mill','gyoza','ippud','kura',
              'saizer','sukiy','lotteria','tous les','klg','marrybrown','pelita',
              'roti','sate','scr','el poll','sirloin','egon','wimpy','steers',
              'cervecer','rodilla','foster','chow','dencio','bacolod','chook',
              'jollibee','est.33','chester','gaggan','sirocco','mado','arab',
              'falafel','chiquito','frankie','harvester','hotcha','itsu',
              'loch fyne','pret a','prezzo','spudulike','strada','table tab',
              'veeno','walkabout','yate','manchu','pick up','au bon','cinnab',
              'le mad','le pain','chili','heine','robeks','guthri','finger',
              'zaxby','baskin','ben &','braum','carvel','friend','graeter',
              'dazs','mango','tcby','yogen','big boy','checkers','culver',
              'fuddruck','halal','jack in','krystal','mooyah','original tom',
              'penguin point','sonic drive','spangle','swenson','drive-in',
              'james coney','sneaky pete','la sals','qdoba','tijuana','cicis',
              'fazoli','pizzer','capriotti','cousins sub','dibella','eegee',
              'erbert &','wrap','jimmy john','mcalister','pita pit',
              'primo hoag','schlot','togo','tubby','which wich','arthur trea',
              'captain d','long john','bennigan','furr','ground rou','houlihan',
              'huddle hou','seasons 52','twin peak','village inn',
              'yard hou','benihan','p.f. chang','hopcat','ale hou','first wat',
              'ihop','bahama','margarit','max &','chuy','cantin','buca di',
              'valentino','bertucci','happy joe','mushroom','maid-rite',
              'mccormick &','bar-b-q','barrel','copeland','famous dave',
              'fogo de','montana mike','texas de','tony roma','dave &'
              ]

food_array = []

for i in range(0,len(df)):

    food_array.append(0)
    
    for food_word in food_words:
        
        if ((food_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):
            
            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                food += float(df.iloc[i][debit_column])
                food_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue
            
        
## Utilities ##

utilities = 0

utilities_words = ['utilit','electri','kahra','duke en','engie','national gr',
                   'nextera','edf','enel','dominion res','iberdrol','southern com',
                   'exelon','kepco','tepco','grid','e.on',' gas',' coal',
                   'southern cali','power','light','consolidated edi','energ',
                   'tennessee vall','authority','arizona publ','salt riv',
                   'municip','public ser','irrig','river','hvac','ventil',
                   ' air','conditioni','heating','sewag',' cable','internet',
                   'phone',' cell ','public work','pepco',' jea','palm beach',
                   ' emc ',' remc ','avista','idacorp','pacificorp','ameren',
                   ' comed ','nisource','vectren','cleco','entergy','swepco',
                   'emera','wmeco','nstar','unitil corp','freeborn-mow',
                   'entergy','ameren','aquila','wapda','orange and r','blue rid',
                   'district',' peco ',' ecoel','santee coop','city of','luminant',
                   'synergy','fuel','hydro','enmax','transalta','atco','epcor',
                   'altalink','churchill falls','lower churchill dev','renewabl',
                   'rio tinto','Comgás','gaz','poweo','gds','petro','cpc corp',
                   'ptt','cuadrilla','niccolo','bulb','agl','atmos','conoco',
                   'eqt','sec vic','alinta','actewagl','summit gro','eletro',
                   'celesc','cemig','cesp','copel','ceee','cez gr','fortum',
                   'alterna','nerg','wateur','enercoop','gdf','lampiris','te oui',
                   ' rwe ','enbw','ppc','ntpc','kptcl','mseb','bses','nhpc',
                   'neyveli lig','damodar val','nuclear','transmission','dakshin g',
                   'dakshin h','board','gujarat urja','madhya g','paschim g',
                   'uttar har','rajasthan raj','uttar pradesh','tneb l','nadu gen',
                   'perusahaan lis','a2a',' acea ',' hera ','sorgenia','tenaga nasio',
                   'meralco','eskon','endesa','vattenfall','transco','al ain dis',
                   'bin moosa &','aadc',' pipe','tabreed al','utico','sesco',
                   'telstra','optus','vodafone','telecom','aapt','primus','network',
                   'transact',' oi ','ooredoo','vivo','irancell','rightel','taliya',
                   'hamra','telefô','astraqom','babytel','bell can','bce inc','bell ali',
                   'northerntel','ontera','mt&t','at&t','newtel','nbtel','islandtel',
                   'northwestel','télébec','communicat','citywest','cogeco','comwave',
                   'distributel','dmts','eastlink','fido','mobile','iristel','wireless',
                   'wifi','novus','sasktel','sene ip','signal','sogotel','tbaytel',
                   'teksavvy','telus','vidéotron','vonage','pccw','orange s.a','sfr',
                   'telesur','digicel','opt pol','tikiphone','o2','dsl','t-home',
                   'broadband','3 hk','csl1010','smartone','budgetalk','gts h',
                   'media ex','invitel','telekom','ups magy','telenor','airtel','bsnl',
                   ' jio ','mtnl','indosat','sateli','telkom','smartfen',' axis ',
                   'xl axi','hiweb','mtce','media','bezeq','cellcom',
                   'voicenter','cellular','phone','fastweb','iliad','wind tre',
                   'tiscali','kddi','ntt','lg u','zain kuw','maxis','dotcom','celcom',
                   'red one',' tune','y-max','axtel','telmex','movistar','telcel',
                   'totalplay','spark new','chorus lim','2degree','etisalat','ufone',
                   'wateen','worldcall','wi-tri','warid','vimpelcom','megafon','mts',
                   'tele2',' motiv ','zain saudi','vodacom','meotel','cell c','glocalnet',
                   ' telia ','nordisk mob','halebop','swedfone','spring mob','bredband',
                   'howsip','swisscom','upc swit',' vibo ','turkcell',' du ','bt group',
                   'kcom gr',' ee ',' hutchison ','talktalk','centurylink','comcast',
                   ' sprint ','verizon','altice','cincinnati bell','crown cast','idt corp',
                   'vonage','zayo group','acn inc',' gci ','singtel','teleserv','arcor ag',
                   'freenet','aircel','mobilink',' zong ',' tot ','true corp','dtac',' ais',
                   'tel ',' steam ','stream ','américa','claro pue','acantho','aexis',
                   'albacom','alcotek','alltre','amtel','asco','atlanet','bergamocom',
                   ' blu ','brennercom','cdc 1085','clicktel','easytel','ecsnet',
                   'elitel','eutelia','fastweb','h3g','infostrada','intred','leadercom',
                   'messagenet','momax','omnitel','c spire','birch','fairpoint','cytranet',
                   'comtech21','alaskatel',' gci ','crexendo','comtech21','smith bagley',
                   'sonic.net','blue casa','telepacific','tcast','voice','ztelco',
                   'closecall',' rcn ','cavalier','on drive tech','nettalk','fractel',
                   'xpedeus','c spire','deltacom','hargray','ellijay','servpac',
                   'rangatel','smithville fib','nitco','dsci corp','12net','metrocom',
                   'telnet','buckeyetel','wow!','trustid','comporium','epb','icbs',
                   'ubta-ubet','sabesp','sanepar','copasa',' water ','environ',' hera ',
                   ' seabo ','waste','waterwork','unitywater','hydra'
                   ]

utilities_array = []

for i in range(0,len(df)):

    utilities_array.append(0)

    for utilities_word in utilities_words:
        
        if ((utilities_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):

            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                utilities += float(df.iloc[i][debit_column])
                utilities_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue


## Insurance ##

insurance = 0

insurance_words = ['insur','warranti','protection',' aflac',' allstate',' aaa ',
                   ' allianz',' aig ',' asi ','ameriprise fin',' amtrust','applied und',
                   'assur',' risk ','bankers life','black bear','blue adv','caresource',
                   'champ va','chubb corp','cigna health','civil service emp','cna fin',
                   'cno fin','country fin','delta den','esurance','evergreen usa',
                   'first coast serv','fm global','gainsco','geico','general re',
                   'genworth fin','gracy tit','grange mut','the hartford','horace mann',
                   'casualty','ironshore','jackson nat','kemper corp','kentucky farm b',
                   'knights of col','liberty mut','lincoln nat','markel corp','massmut',
                   ' mbbs ','metlife','metromite','modern wood','mutual of om',
                   'national life','the norfolk &','northwestern mut','ohio national fin',
                   ' omega','onebeacon','oxford health','pacific life','pacific prime',
                   'pemco','penn mutual','physicians mut','plymouth rock','primerica',
                   'principal fin',' progressive','protective life','prudential fin',
                   ' qbe ','the regence g','reliance part','rli corp',' safeco',
                   'securian fin','squaretrade','sun life fin','symetra','the gen',
                   'the travelers comp','tiaa-cerf','transamerica corp','tricare',
                   'triwest','trupanion','universal prop',' unum ',' usaa ','us health g',
                   'vantage health','veteran affair','west coast life','southern fin',
                   'xl catlin','colonial penn','conseco','garden state life','ing grou',
                   'mature life','old mutual','unifi comp','united of om','amerisafe',
                   ' memic ','employers mut','united heart',' aia ','assicur',' axa ',
                   'british marine lux',' bupa ','canada life',' cigna ',
                   'clerical medical','claridge-ware','euler herm','friends prov',
                   'generali int','gerling-kon','globalhealth asia','grouparma tran',
                   'hang seng life','hannover r','hong kong mor','hsbc life','kolnische r',
                   'underwrit','guarant','manulife','massmutual','munchener r',
                   'phoenix life','schweizerische r','scottish mut','standard life',
                   'sun life hong','taylor brun',' icici ','coface s',' ecics ',
                   'fwd sing','lion city run','s of lon','shc capital','sompo jap',
                   'standard steam','singapore life','transamerica life',
                   'zurich international l','aviva lim','asia sunrise','creare priv',
                   'reliance nat','r&v ver','scor global life','tokio marine n',
                   'muenchener r','xi re lim','uib asia priv','medicare',' aarp ',' aetna',
                   'amerigroup',' anthem ','aspen dent','cambia health','blue cross and',
                   'coventry health','emblemhealth',' fortis ','geisinger','group health',
                   'health net','healthmarket','healthpartner','healthspring','highmark',
                   'humana','independence blue','kaiser perman','kaleida health',
                   'liberty medic','lifewise health','med4home','oscar health','premera blue',
                   'state farm','thrivent fin','unitedhealth','unitrin','universal american c',
                   'wellcare','fidelis care'
                   ]

insurance_array = []

for i in range(0,len(df)):

    insurance_array.append(0)

    for insurance_word in insurance_words:
        
        if ((insurance_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):

            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                insurance += float(df.iloc[i][debit_column])
                insurance_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue

                
## Healthcare ##

healthcare = 0

healthcare_words = ['medic','health','care ','well-being','hospit','prescrip','dental',
                    'dentis','pharma','drug','doctor','nurs','specialist','ologist',
                    'trauma','triage','emergency','burn cent','psych',' rehab','cancer',
                    ' acute','infirm','pediat','treatment','illness','injur','diseas',
                    'surgic','surger','surgeo','obstet','postnat','ambula','clinic',
                    'long-term c','chronic','cardi','osteo','physio','therap','counselo',
                    'patient','geriat','oncolog','transplant',' organ ','physici','wound',
                    'recovery','recoveri','mental','lunat','asylum','communicab',
                    'santorium','clínic','hôpital','özel','hastanesi','holzspit','cliniq',
                    'kantonss','ospedal','parapleg','spital','klinik'
                    ]
                    

healthcare_array = []

for i in range(0,len(df)):

    healthcare_array.append(0)

    for healthcare_word in healthcare_words:
        
        if ((healthcare_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):

            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                healthcare += float(df.iloc[i][debit_column])
                healthcare_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue
                   

## Investment ##

investment = 0

investment_words = ['saving','invest','debt','retire','superan','401(k)',' ira ',' loan',
                    'jpmorgan','goldman s','bofa sec','morgan stan','credit suisse',
                    'barclays invest','deutsche bank',' ubs ','rbc cap','wells fargo',
                    'jefferies group','bnp paribas','mizuho fin','lazard','nomura',
                    'evercore part','bmo capital','mitsubishi ufj','almeida cap',
                    'atlantic-pac','campbell part','helix assoc','morgan caz','park hill',
                    'probitas part','abn amro','barclays cap','lloyds banki','merrill lyn',
                    'cibc world','national westm','nomura group','william blair &',
                    'markets','etoro','trading','bank of amer','allahabad bank','allen & co',
                    'bb&t','berkery, noy','bg capital','blackstone','cantor flitz',
                    'capstone part','centerview part','china international cap','citic secu',
                    ' clsa ','commerzbank','corporate fin','cowen','credit agricole',
                    'csg part','daewoo sec','duff & phel','europa part','financo',
                    'gleacher & comp','greenhill & co','guggenheim part','guosen part',
                    'houlihan lok','hsbc holding','imperial capital','icbc ','icici bank',
                    'indian bank','j.p. morg','keefe, bruy','keycorp','ladenburg',
                    'lancaster poll','lincoln int','macquarie gr','maple capital',
                    'marathon cap','mccoll part','mediobanca','miller buck','moelis & c',
                    'montgomery & co','morgan keegan','needham & co',' nbf ','nomura hold',
                    'oppenheimer & co','panmure gord','perella wein','piper jaff','pnc fin',
                    'punjab national bank','raymond james',' rbs ','robert w. b',
                    'roth capital part','rothschild','sagent advis','sandler o','sbi capital',
                    'scotiabank','société générale','sonenshine part','stephens, inc',
                    'stifel fin','sucsy, fischer','sumitomo mitsui fin','suntrust',
                    'syndicate bank','td secur','united bank of india','vermillion part',
                    'wr hambrecht','yes bank',' capital ','partners','finance',
                    'fidelity invest','e*trade','td ameri','robinhood',' stash ',
                    ' acorns ',' coinbase ','fanduel','predictlt','charles schwab',
                    'betterment','broker','wealth','asset','merrill edge',' stock','fund',
                    ' equit','finans','financial','transfer','telex'
                    ]

investment_array = []

for i in range(0,len(df)):

    investment_array.append(0)

    for investment_word in investment_words:
        
        if ((investment_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):

            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                investment += float(df.iloc[i][debit_column])
                investment_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue
                    

## Recreation & Enterntainment ##

recreation = 0

recreation_words = ['recreat','entertain',' fun','leisure','concert','sport','game','bowling',
                    'vacation','tour ','airline','airway','ticket','cinema','theatr',
                    'subscript','netflix','hulu','hobb','streami','itune','android','hotel',
                    'inn','emirates','etihad','lufthan','delta air','klm','air fr','ryanair',
                    ' iag ','air china','skywest','easyjet','wizz air','trip','ferry','cruise',
                    'train','coach','movie','music','film','kid','activit','boat','sailing',
                    'flying','diving','dune','safari','expedit','theme park','disney','youtube',
                    'broadway','studios','amuse','cable tele','broadcast','20th century',
                    ' fair','disco',' bar','club','comcast','crunchyroll','discover',
                    'fox corp','the jim henson','klasky csupo','premier park','rdf media',
                    'six flag','perform',' art','21st century','4licens','productions',
                    'aerodrome inc','a.d. vision','access ind','wrestl','aniplex','antigrav',
                    'aqualillies','alpha video','talent','pictures','brooklyn bould','burnloung',
                    'cbs corp','chippendales','cinedigm','circus','cloverway','cmd dist',
                    'stadium',' show','auditori','cosmote tv','crush manag','dave & bust',
                    'deaton-flan','dover motor','ecast, inc','eapybird','elvis presley enter',
                    'firework','foxnext','gaia, inc','genius brands','ghost hunt week',
                    'giftwrap','the goldklang','great eastern con','grindhouse','harmony gold',
                    'hunk-o',' ibahn ','imengine','international speed','jillian','juniornet',
                    'publications',' leg ','lionsgate','the madison square','martinka',
                    'motion pic',' moxi ','national geo','nbcunivers','nu image','pangea corp',
                    'paniq escape','pb&j tele','premier parks','radical axis','realnetwork',
                    'right stuf','ryman hosp','seagram','the shuman','society award',
                    'splash universe','springtime','station.com','sundance group','swarmcast',
                    'timetrax','tivo inc','toei animation','truly indie','gala','contest',
                    'festiv','fayre','celebra'
                    ]

recreation_array = []

for i in range(0,len(df)):

    recreation_array.append(0)

    for recreation_word in recreation_words:
        
        if ((recreation_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):
            
            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                recreation += float(df.iloc[i][debit_column])
                recreation_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue
                    

## Personal ##

personal = 0

personal_words = ['shop','walmart','amazon','megamart','carrefour','lifestyle',
                  'gym','cloth','shoe','mart','decor','furni','gift','magazine',
                  'hygien','dry clean','laundry','store','ikea','monoprix','spinney',
                  'barneys','century21','j. c. pen','kohl','lord & tay','macy',
                  'bloomingdale','neiman marc','bergdof good','nordstrom','saks fifth',
                  'sears','bealls',' belk ','boscov','dillard','goody','gordmans',
                  'palais royal','peebles','von maur','boyds','charleston dep',
                  'david m. brian','dunham','flemington dep','fords fed','getz',
                  'gus mayer','halls','jos. kuhn','la epoca','lavogue','dar al sal',
                  'leader depart','loeb','mack & dave','mccaulou',"murphy's",'groom',
                  "neilson's",'nichols',"norby's","ossell's","reed's","ruben's",
                  'rubenstein',"schroeder's",'shirokiya','the sm',"stahlke's",
                  'stanley korshak','tomah cash',"wakefield's","weaver's",'fitness',
                  "wilson's","scott seale's","young's dep",'bargain','ben franklin',
                  'big lots','wholesale',' sale','burlington','costco','discount',
                  'dirt cheap','dollar general','dollar tree','family dollar',
                  'five below',"fred's",'fred meyer',"gabe's",'gordmans',
                  'harbor freight','homegoods','homesense','marshalls','meijer',
                  'ocean state job','renys','roses','t.j. maxx','treasure hunt',
                  'tuesday morning',"sam's club",'lulu','market','hyper',
                  'supertarget','kroger','kaufland',' coles','the warehouse',
                  'loblaw','jumbo',' asda ','sainsbury','harrod','tesco',
                  'marks and spenc',' BHS','géant','albertsons','carrs','jewel-osco',
                  'pavilions','randalls','tom thumb','safeway inc',' vons','food lion',
                  'hannaford','giant food','king kullen','fred meyer','harris teeter',
                  'jay c','king soopers',"mariano's","owen's",' qfc ','ralphs',
                  "roundy's","scott's",'spartannash','supervalu','hornbacher',
                  "shop 'n save","bashas'",'brookshire','buehler','big y','butera'
                  'super saver','buy for less','calandros','caraluzzi','cash saver',
                  'coborns','de cicco','dierberg','fareway','giant eagle','giant value',
                  'giantway','gristede','h-e-b','hen house','homeland',"hugo's",
                  'hy-vee','la canasta','lunardi','lunds &','macey','matherne',
                  'mccaffrey','meijer','morton william','mollie stone','piggly wig',
                  'preston-safe','price chop','pricerite','publix','pueblo',"raley's",
                  'roche bro','rosauer','schnuck','smart & fin','stater bro',
                  'stew leo','supermercad','supersol',"trig's","turco's","wade's",
                  'wegmans',"wesselman's",'wise way',"zup's",' aldi ','cash & carry',
                  'outlet','plaza','hannam','marukai','mitsuwa','bazar','bazzar',
                  'patel bro',' bravo ','mi tienda','la placita','presidente',
                  'rancho',"saver's cost",'el super',"terry's","motty's",
                  'new day','kosher','evergreen','breadberry','grand & ess'
                  
                  ]

personal_array = []
              
for i in range(0,len(df)):

    personal_array.append(0)

    for personal_word in personal_words:
        
        if ((personal_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):
            
            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                personal += float(df.iloc[i][debit_column])
                personal_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue


## Education ##

education = 0

education_words = ['educat','tuition','colleg','universit','school','kindergar',
                   'elementary','edx','mooc','udacity','course','udemy','of tech',
                   'tutor','edexcel','aqa','ocr',' sat ',' act ',' gre ','toefl',
                   'ietls','pearson','exam','assessm','quiz'
                  ]

education_array = []
              
for i in range(0,len(df)):

    education_array.append(0)

    for education_word in education_words:
        
        if ((education_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][credit_column] == 0):

            df.iloc[i][description_column] = '----D-R-C----'
        
            try:
                education += float(df.iloc[i][debit_column])
                education_array[i] = float(df.iloc[i][debit_column])
            except ValueError:
                continue
            

## Miscellaneous Debit ##

misc_debit = debit - food - utilities - insurance - healthcare - investment - recreation - personal - education           


## Salary ##

salary = 0

salary_words = ['salar','compens','renumer','wage','stipend','allowance','income',
                'emolume','honorarium','hire','pay ','bonus'
                  ]

salary_array = []
              
for i in range(0,len(df)):

    salary_array.append(0)

    for salary_word in salary_words:
        
        if ((salary_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][debit_column] == 0):

            df.iloc[i][description_column] = '----C-R-C----'
        
            try:
                salary += float(df.iloc[i][credit_column])
                salary_array[i] = float(df.iloc[i][credit_column])
            except ValueError:
                continue


## Earnings ##

earnings = 0

earnings_words = ['invest','earning','dividend','stock','share','bond','profit',
                  'earned','return','payback','premium','benefit','gain','surplus',
                  'capital','portion','advantag','commision','rent','lease',
                  'hire','charter','fund','market','forex','tenan','interest',
                  'charge'
                  ]

earnings_array = []
              
for i in range(0,len(df)):
    
    earnings_array.append(0)

    for earnings_word in earnings_words:
        
        if ((earnings_word in ((str(df.iloc[i][description_column])).lower())) == True) and (df.iloc[i][debit_column] == 0):

            df.iloc[i][description_column] = '----C-R-C----'
        
            try:
                earnings += float(df.iloc[i][credit_column])
                earnings_array[i] = float(df.iloc[i][credit_column])
            except ValueError:
                continue


## Miscellaneous Credit ##

misc_credit = credit - salary - earnings


### Debit Categories Array ###

debit_cat_array = [['Housing',housing],['Food',food],['Insurance',insurance],
                   ['Utilities',utilities],['Transportation',transportation],
                   ['Healthcare',healthcare],['Recreation',recreation],
                   ['Personal',personal],['Education',education],['Investment',investment],
                   ['Other Debit',misc_debit]]


### Credit Categories Array ###

credit_cat_array = [['Salary',salary],['Earnings',earnings],['Other Credit',misc_credit]]

            
### Finding Currency ###

lpage_content = page_content.lower()
currency = ''

if ('australian' in lpage_content) == True:
    currency = 'AUD'
if ('australian dollar' in lpage_content) == True:
    currency = 'AUD'
if ('a$' in lpage_content) == True:
    currency = 'AUD'
if ('AUD' in page_content) == True:
    currency = 'AUD'

#if ('brazilian' in lpage_content) == True:
#    currency = 'BRL'
#if ('brazilian real' in lpage_content) == True:
#    currency = 'BRL'
#if ('r$' in lpage_content) == True:
#    currency = 'BRL'
#if ('BRL' in page_content) == True:
#    currency = 'BRL'
    
if ('british' in lpage_content) == True:
    currency = 'GBP'
if ('british pound' in lpage_content) == True:
    currency = 'GBP'
if ('£' in lpage_content) == True:
    currency = 'GBP'
if ('GBP' in page_content) == True:
    currency = 'GBP'

if ('canadian' in lpage_content) == True:
    currency = 'CAD'
if ('canadian dollar' in lpage_content) == True:
    currency = 'CAD'
if ('c$' in lpage_content) == True:
    currency = 'CAD'
if ('CAD' in page_content) == True:
    currency = 'CAD'

#if ('chilean' in lpage_content) == True:
#    currency = 'CLP'
#if ('chilean peso' in lpage_content) == True:
#    currency = 'CLP'
#if ('CLP' in page_content) == True:
#    currency = 'CLP'

#if ('chinese' in lpage_content) == True:
#    currency = 'CNY'
#if ('yuan' in lpage_content) == True:
#    currency = 'CNY'
#if ('CNY' in page_content) == True:
#    currency = 'CNY'

#if ('czech' in lpage_content) == True:
#    currency = 'CZK'
#if ('koruna' in lpage_content) == True:
#    currency = 'CZK'
#if ('kč' in lpage_content) == True:
#    currency = 'CZK'
#if ('CZK' in page_content) == True:
#    currency = 'CZK'

#if ('danish' in lpage_content) == True:
#    currency = 'DKK'
#if ('danish krone' in lpage_content) == True:
#    currency = 'DKK'
#if ('DKK' in page_content) == True:
#    currency = 'DKK'

if ('euro' in lpage_content) == True:
    currency = 'EUR'
if ('€' in lpage_content) == True:
    currency = 'EUR'
if ('EUR' in page_content) == True:
    currency = 'EUR'

#if ('hong kong' in lpage_content) == True:
#    currency = 'HKD'
#if ('hong kong dollar' in lpage_content) == True:
#    currency = 'HKD'
#if ('hk$' in lpage_content) == True:
#    currency = 'HKD'
#if ('HKD' in page_content) == True:
#    currency = 'HKD'

#if ('hungarian' in lpage_content) == True:
#    currency = 'HUF'
#if ('forint' in lpage_content) == True:
#    currency = 'HUF'
#if ('HUF' in page_content) == True:
#    currency = 'HUF'

#if ('indian' in lpage_content) == True:
#    currency = 'INR'
#if ('₹' in lpage_content) == True:
#    currency = 'INR'
#if ('INR' in page_content) == True:
#    currency = 'INR'

#if ('indonesian' in lpage_content) == True:
#    currency = 'IDR'
#if ('rupiah' in lpage_content) == True:
#    currency = 'IDR'
#if ('IDR' in page_content) == True:
#    currency = 'IDR'

#if ('japanese' in lpage_content) == True:
#    currency = 'JPY'
#if ('yen' in lpage_content) == True:
#    currency = 'JPY'
#if ('JPY' in page_content) == True:
#    currency = 'JPY'

#if ('korean' in lpage_content) == True:
#    currency = 'KRW'
#if ('korean won' in lpage_content) == True:
#    currency = 'KRW'
#if ('₩' in lpage_content) == True:
#    currency = 'KRW'
#if ('KRW' in page_content) == True:
#    currency = 'KRW'

#if ('malaysian' in lpage_content) == True:
#    currency = 'MYR'
#if ('ringgit' in lpage_content) == True:
#    currency = 'MYR'
#if ('MYR' in page_content) == True:
#    currency = 'MYR'

#if ('mexican' in lpage_content) == True:
#    currency = 'MXN'
#if ('mexican peso' in lpage_content) == True:
#    currency = 'MXN'
#if ('mex$' in lpage_content) == True:
#    currency = 'MXN'
#if ('MXN' in page_content) == True:
#    currency = 'MXN'

if ('new zealand' in lpage_content) == True:
    currency = 'NZD'
if ('new zealand dollar' in lpage_content) == True:
    currency = 'NZD'
if ('nzd' in lpage_content) == True:
    currency = 'NZD'

#if ('norwegian' in lpage_content) == True:
#    currency = 'NOK'
#if ('norwegian krone' in lpage_content) == True:
#    currency = 'NOK'
#if ('NOK' in page_content) == True:
#    currency = 'NOK'

#if ('pakistani' in lpage_content) == True:
#    currency = 'PKR'
#if ('pakistani rupee' in lpage_content) == True:
#    currency = 'PKR'
#if ('PKR' in page_content) == True:
#    currency = 'PKR'

#if ('philippine' in lpage_content) == True:
#    currency = 'PHP'
#if ('philippine peso' in lpage_content) == True:
#    currency = 'PHP'
#if ('₱' in lpage_content) == True:
#    currency = 'PHP'
#if ('PHP' in page_content) == True:
#    currency = 'PHP'

#if ('polish' in lpage_content) == True:
#    currency = 'PLN'
#if ('zloty' in lpage_content) == True:
#    currency = 'PLN'
#if ('zł' in lpage_content) == True:
#    currency = 'PLN'
#if ('PLN' in page_content) == True:
#    currency = 'PLN'

#if ('russian' in lpage_content) == True:
#    currency = 'RUB'
#if ('ruble' in lpage_content) == True:
#    currency = 'RUB'
#if ('RUB' in page_content) == True:
#    currency = 'RUB'

#if ('singapore' in lpage_content) == True:
#    currency = 'SGD'
#if ('singapore dollar' in lpage_content) == True:
#    currency = 'SGD'
#if ('s$' in lpage_content) == True:
#    currency = 'SGD'
#if ('SGD' in page_content) == True:
#    currency = 'SGD'

#if ('south african' in lpage_content) == True:
#    currency = 'ZAR'
#if ('rand' in lpage_content) == True:
#    currency = 'ZAR'
#if ('ZAR' in page_content) == True:
#    currency = 'ZAR'

#if ('swedish' in lpage_content) == True:
#    currency = 'SEK'
#if ('krona' in lpage_content) == True:
#    currency = 'SEK'
#if ('SEK' in page_content) == True:
#    currency = 'SEK'

#if ('swiss' in lpage_content) == True:
#    currency = 'CHF'
#if ('franc' in lpage_content) == True:
#    currency = 'CHF'
#if ('CHF' in page_content) == True:
#    currency = 'CHF'

#if ('taiwan' in lpage_content) == True:
#    currency = 'TWD'
#if ('taiwan dollar' in lpage_content) == True:
#    currency = 'TWD'
#if ('nt$' in lpage_content) == True:
#    currency = 'TWD'
#if ('TWD' in page_content) == True:
#    currency = 'TWD'

#if ('thai' in lpage_content) == True:
#    currency = 'THB'
#if ('baht' in lpage_content) == True:
#    currency = 'THB'
#if ('฿' in lpage_content) == True:
#    currency = 'THB'
#if ('THB' in page_content) == True:
#    currency = 'THB'

#if ('turkish' in lpage_content) == True:
#    currency = 'TRY'
#if ('lira' in lpage_content) == True:
#    currency = 'TRY'
#if ('₺' in lpage_content) == True:
#    currency = 'TRY'
#if ('TRY' in page_content) == True:
#    currency = 'TRY'

if ('us dollar' in lpage_content) == True:
    currency = 'USD'
if ('united states dollar' in lpage_content) == True:
    currency = 'USD'
if ('USD' in page_content) == True:
    currency = 'USD'

#if ('iranian' in lpage_content) == True:
#    currency = 'IRR'
#if ('iranian rial' in lpage_content) == True:
#    currency = 'IRR'
#if ('IRR' in page_content) == True:
#    currency = 'IRR'

if ('saudi' in lpage_content) == True:
    currency = 'SAR'
if ('saudi riyal' in lpage_content) == True:
    currency = 'SAR'
if ('SAR' in page_content) == True:
    currency = 'SAR'

if ('kuwaiti' in lpage_content) == True:
    currency = 'KWD'
if ('dinar' in lpage_content) == True:
    currency = 'KWD'
if ('KWD' in page_content) == True:
    currency = 'KWD'

if ('emirati' in lpage_content) == True:
    currency = 'AED'
if ('dirham' in lpage_content) == True:
    currency = 'AED'
if ('AED' in page_content) == True:
    currency = 'AED'

if ('qatari' in lpage_content) == True:
    currency = 'QAR'
if ('qatari riyal' in lpage_content) == True:
    currency = 'QAR'
if ('QAR' in page_content) == True:
    currency = 'QAR'


### Cost of Living Ratio CUR vs. USD ###

c_aud = 0.69
c_brl = 0.38
c_gbp = 0.92
c_cad = 0.62
c_clp = 0.36
c_cny = 0.48
c_czk = 0.46
c_dkk = 0.80
c_eur = 0.80
c_hkd = 0.93
c_huf = 0.37
c_inr = 0.22
c_idr = 0.38
c_jpy = 0.78
c_krw = 0.70
c_myr = 0.35
c_mxn = 0.35
c_nzd = 0.67
c_nok = 0.87
c_pkr = 0.18
c_php = 0.37
c_pln = 0.40
c_rub = 0.46
c_sgd = 0.87
c_zar = 0.43
c_sek = 0.69
c_chf = 1.14
c_twd = 0.51
c_thb = 0.51
c_try = 0.26
c_usd = 1.00
c_irr = 0.37
c_sar = 0.39
c_kwd = 0.51
c_aed = 0.66
c_qar = 0.68


### Extracting Name ###

doc = nlp(page_content)
people = ['']
people = [name for name in doc.ents if name.label_ == 'PERSON']
name = people[0]
name = str(name)
name = name.lower()
name = name.title()
name = name[0:20]


### Creating Report ###

pdf = FPDF(orientation = 'P', unit = 'mm', format = 'A4')
pdf.add_page()
pdf.image('C:/Users/Mohammad Khorasani/Desktop/page.png', x = 0, y = 0, w = 210, h = 297)
pdf.set_font('helvetica','',10)
pdf.set_text_color(255,255,255)
pdf.text(25.0,49.0,name)
pdf.text(25.0,57.2,currency)
pdf.text(25.0,65.5,sdate)
pdf.text(25.0,73.7,edate)

## Generating Pie Charts ##

credit_color = [[0.0000,0.4392,0.7529],[0.8627,0.0784,0.8431],[0.6157,0.7647,0.9020]]

debit_color = [[0.4980,0.4980,0.4980],[0.7490,0.7490,0.7490],[0.5176,0.2353,0.04706],
               [1.0000,0.0000,0.0000],[1.0000,1.0000,0.0000],[0.3294,0.5098,0.2078],
               [1.0000,0.8509,0.4000],[0.7490,0.5647,0.0000],[0.0000,0.0000,0.0000],
               [0.6627,0.8196,0.5569],[0.9569,0.6941,0.5137]]

def donut(name, value, category, total_value, currency, color, color_b):

    values = [value, total_value - value]
    
    my_circle=plt.Circle( (0,0), 0.8, color=[0.9490,0.9490,0.9490])

    plt.pie(values,
            wedgeprops = { 'linewidth' : 0, 'edgecolor' : 'white' }, colors=[color,color_b],labeldistance=1.1)

    p=plt.gcf()
    p.gca().add_artist(my_circle)
    plt.savefig(('%s.png' % (name)),orientation='portrait',transparent=True, bbox_inches=None, pad_inches=0)
    plt.close()

for i in range(0,len(credit_cat_array)):
    donut(credit_cat_array[i][0],int(credit_cat_array[i][1]),'Other Credit',credit,currency,credit_color[i],[0.8549,0.8902,0.9529])

for i in range(0,len(debit_cat_array)):
    donut(debit_cat_array[i][0],int(debit_cat_array[i][1]),'Other Debit',debit,currency,debit_color[i],[0.9569,0.8627,0.8549])


## Health Score ##

housing_score = [25,0,25,35,60]
food_score = [10,0,10,15,25]
insurance_score = [10,0,10,25,35]
utilities_score = [5,0,5,10,15]
transportation_score = [10,0,10,15,25]
healthcare_score = [5,0,5,10,15]
recreation_score = [5,0,5,10,15]
personal_score = [5,0,5,10,15]
education_score = [10,0,10,20,30]
investment_score = [10,0,10,20,30]
other_debit_score = [5,0,5,10,15]

if (housing/debit*100) <= housing_score[2]:
    housing_score_val = ((housing_score[2] - (housing/debit*100))/housing_score[2])*100
if ((housing/debit*100) > housing_score[2]) and ((housing/debit*100) <= housing_score[3]):
    housing_score_val = 0
if ((housing/debit*100) > housing_score[3]) and ((housing/debit*100) <= housing_score[4]):
    housing_score_val = ((housing_score[3] - (housing/debit*100))/housing_score[2])*100
if ((housing/debit*100) > housing_score[4]):
    housing_score_val = -100

if (food/debit*100) <= food_score[2]:
    food_score_val = ((food_score[2] - (food/debit*100))/food_score[2])*100
if ((food/debit*100) > food_score[2]) and ((food/debit*100) <= food_score[3]):
    food_score_val = 0
if ((food/debit*100) > food_score[3]) and ((food/debit*100) <= food_score[4]):
    food_score_val = ((food_score[3] - (food/debit*100))/food_score[2])*100
if ((food/debit*100) > food_score[4]):
    food_score_val = -100

if (insurance/debit*100) <= insurance_score[2]:
    insurance_score_val = ((insurance_score[2] - (insurance/debit*100))/insurance_score[2])*100
if ((insurance/debit*100) > insurance_score[2]) and ((insurance/debit*100) <= insurance_score[3]):
    insurance_score_val = 0
if ((insurance/debit*100) > insurance_score[3]) and ((insurance/debit*100) <= insurance_score[4]):
    insurance_score_val = ((insurance_score[3] - (insurance/debit*100))/insurance_score[2])*100
if ((insurance/debit*100) > insurance_score[4]):
    insurance_score_val = -100

if (utilities/debit*100) <= utilities_score[2]:
    utilities_score_val = ((utilities_score[2] - (utilities/debit*100))/utilities_score[2])*100
if ((utilities/debit*100) > utilities_score[2]) and ((utilities/debit*100) <= utilities_score[3]):
    utilities_score_val = 0
if ((utilities/debit*100) > utilities_score[3]) and ((utilities/debit*100) <= utilities_score[4]):
    utilities_score_val = ((utilities_score[3] - (utilities/debit*100))/utilities_score[2])*100
if ((utilities/debit*100) > utilities_score[4]):
    utilities_score_val = -100

if (transportation/debit*100) <= transportation_score[2]:
    transportation_score_val = ((transportation_score[2] - (transportation/debit*100))/transportation_score[2])*100
if ((transportation/debit*100) > transportation_score[2]) and ((transportation/debit*100) <= transportation_score[3]):
    transportation_score_val = 0
if ((transportation/debit*100) > transportation_score[3]) and ((transportation/debit*100) <= transportation_score[4]):
    transportation_score_val = ((transportation_score[3] - (transportation/debit*100))/transportation_score[2])*100
if ((transportation/debit*100) > transportation_score[4]):
    transportation_score_val = -100

if (healthcare/debit*100) <= healthcare_score[2]:
    healthcare_score_val = ((healthcare_score[2] - (healthcare/debit*100))/healthcare_score[2])*100
if ((healthcare/debit*100) > healthcare_score[2]) and ((healthcare/debit*100) <= healthcare_score[3]):
    healthcare_score_val = 0
if ((healthcare/debit*100) > healthcare_score[3]) and ((healthcare/debit*100) <= healthcare_score[4]):
    healthcare_score_val = ((healthcare_score[3] - (healthcare/debit*100))/healthcare_score[2])*100
if ((healthcare/debit*100) > healthcare_score[4]):
    healthcare_score_val = -100

if (recreation/debit*100) <= recreation_score[2]:
    recreation_score_val = ((recreation_score[2] - (recreation/debit*100))/recreation_score[2])*100
if ((recreation/debit*100) > recreation_score[2]) and ((recreation/debit*100) <= recreation_score[3]):
    recreation_score_val = 0
if ((recreation/debit*100) > recreation_score[3]) and ((recreation/debit*100) <= recreation_score[4]):
    recreation_score_val = ((recreation_score[3] - (recreation/debit*100))/recreation_score[2])*100
if ((recreation/debit*100) > recreation_score[4]):
    recreation_score_val = -100

if (personal/debit*100) <= personal_score[2]:
    personal_score_val = ((personal_score[2] - (personal/debit*100))/personal_score[2])*100
if ((personal/debit*100) > personal_score[2]) and ((personal/debit*100) <= personal_score[3]):
    personal_score_val = 0
if ((personal/debit*100) > personal_score[3]) and ((personal/debit*100) <= personal_score[4]):
    personal_score_val = ((personal_score[3] - (personal/debit*100))/personal_score[2])*100
if ((personal/debit*100) > personal_score[4]):
    personal_score_val = -100

if (education/debit*100) <= education_score[2]:
    education_score_val = ((education_score[2] - (education/debit*100))/education_score[2])*100
if ((education/debit*100) > education_score[2]) and ((education/debit*100) <= education_score[3]):
    education_score_val = 0
if ((education/debit*100) > education_score[3]) and ((education/debit*100) <= education_score[4]):
    education_score_val = ((education_score[3] - (education/debit*100))/heducation_score[2])*100
if ((education/debit*100) > education_score[4]):
    education_score_val = -100

if (investment/debit*100) <= investment_score[2]:
    investment_score_val = ((investment_score[2] - (investment/debit*100))/investment_score[2])*100
if ((investment/debit*100) > investment_score[2]) and ((investment/debit*100) <= investment_score[3]):
    investment_score_val = 0
if ((investment/debit*100) > investment_score[3]) and ((investment/debit*100) <= investment_score[4]):
    investment_score_val = ((investment_score[3] - (investment/debit*100))/investment_score[2])*100
if ((investment/debit*100) > investment_score[4]):
    investment_score_val = -100

if (misc_debit/debit*100) <= other_debit_score[2]:
    other_debit_score_val = ((other_debit_score[2] - (misc_debit/debit*100))/other_debit_score[2])*100
if ((misc_debit/debit*100) > other_debit_score[2]) and ((misc_debit/debit*100) <= other_debit_score[3]):
    other_debit_score_val = 0
if ((misc_debit/debit*100) > other_debit_score[3]) and ((misc_debit/debit*100) <= other_debit_score[4]):
    other_debit_score_val = ((other_debit_score[3] - (misc_debit/debit*100))/other_debit_score[2])*100
if ((misc_debit/debit*100) > other_debit_score[4]):
    other_debit_score_val = -100

spending_score = ((housing_score_val/100)*housing_score[0]
                  + (food_score_val/100)*food_score[0]
                  + (insurance_score_val/100)*insurance_score[0]
                  + (utilities_score_val/100)*utilities_score[0]
                  + (transportation_score_val/100)*transportation_score[0]
                  + (healthcare_score_val/100)*healthcare_score[0]
                  + (recreation_score_val/100)*recreation_score[0]
                  + (personal_score_val/100)*personal_score[0]
                  + (education_score_val/100)*education_score[0]
                  + (investment_score_val/100)*investment_score[0]
                  + (other_debit_score_val/100)*other_debit_score[0]
                  )

balance_score = (int(credit - debit)/sbalance)*100

if int(credit - debit) > sbalance:
    balance_score = 100
if int(credit - debit) < -sbalance:
    balance_score = -100

health_score = int(((spending_score/100)*50) + ((balance_score/100)*50))

def donut_2(name, value, color_b):

    if value >= 80:
        color = [0.4392,0.6784,0.2784]
    if (value < 80) and (value >= 60):
        color = [0.9569,0.6941,0.5137]
    if value < 60:
        color = [1.0000,0.4118,0.4118]
    
    my_circle=plt.Circle( (0,0), 0.8, color=[0.4902,0.8000,1.0000])

    if value > 0:
        values = [value, 100 - value]
        plt.pie(values,
                wedgeprops = { 'linewidth' : 0, 'edgecolor' : 'white' }, colors=[color,color_b],labeldistance=1.1)

    if value < 0:
        values = [-value, 100 + value]
        plt.pie(values,
                wedgeprops = { 'linewidth' : 0, 'edgecolor' : 'white' }, colors=[color,color_b],labeldistance=1.1, counterclock=False)

    p=plt.gcf()
    p.gca().add_artist(my_circle)
    plt.savefig(('%s.png' % (name)),orientation='portrait',transparent=True, bbox_inches=None, pad_inches=0)
    plt.close()

donut_2('Debit_score',spending_score,[0.9569,0.8627,0.8549])
donut_2('Balance_score',balance_score,[0.8549,0.8902,0.9529])
donut_2('Health_score',health_score,[0.8549,0.8902,0.9529])

## Bar Charts ##

def bar_chart(date,balance,credit,debit,salary,earnings,housing,food,transportation,utilities,insurance,healthcare,investment,recreation,personal,education):

    balance_a = []

    for i in range(0,len(date)):

        if i < len(date) - 1:
            if date[i] != date[i+1]:
                balance_a.append((date[i],balance[i]))
        if i == len(date) - 1:
            balance_a.append((date[i],balance[i]))
        

    credit_d = []

    for i in range(0,len(date)):
        credit_d.append((date[i],credit[i]))

    dictionary = dict()

    for (date_v,value) in credit_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    credit_a = [(key, val) for (key, val) in dictionary.items()]

    debit_d = []

    for i in range(0,len(date)):
        debit_d.append((date[i],debit[i]))

    dictionary = dict()

    for (date_v,value) in debit_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    debit_a = [(key, val) for (key, val) in dictionary.items()]

    x = [x[0:6] for (x,y) in balance_a]


    ### Credit Categories ###

    ## Salary Category ##

    salary_d = []

    for i in range(0,len(date)):
        salary_d.append((date[i],salary[i]))

    dictionary = dict()

    for (date_v,value) in salary_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    salary_a = [(key, val) for (key, val) in dictionary.items()]


    ## Earnings Category ##

    earnings_d = []

    for i in range(0,len(date)):
        earnings_d.append((date[i],earnings[i]))

    dictionary = dict()

    for (date_v,value) in earnings_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    earnings_a = [(key, val) for (key, val) in dictionary.items()]

    ## Miscellanous Category ##

    miscellanousc_a = []

    for i in range(0,len(x)):
        miscellanousc_a.append((x[i],credit_a[i][1]
                              - salary_a[i][1]
                              - earnings_a[i][1]
                              ))


    ### Debit Categories ###

    ## Personal Category ##

    personal_d = []

    for i in range(0,len(date)):
        personal_d.append((date[i],personal[i]))

    dictionary = dict()

    for (date_v,value) in personal_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    personal_a = [(key, val) for (key, val) in dictionary.items()]


    ## Housing Category ##

    housing_d = []

    for i in range(0,len(date)):
        housing_d.append((date[i],housing[i]))

    dictionary = dict()

    for (date_v,value) in housing_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    housing_a = [(key, val) for (key, val) in dictionary.items()]


    ## Food Category ##

    food_d = []

    for i in range(0,len(date)):
        food_d.append((date[i],food[i]))

    dictionary = dict()

    for (date_v,value) in food_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    food_a = [(key, val) for (key, val) in dictionary.items()]


    ## Transportation Category ##

    transportation_d = []

    for i in range(0,len(date)):
        transportation_d.append((date[i],transportation[i]))

    dictionary = dict()

    for (date_v,value) in transportation_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    transportation_a = [(key, val) for (key, val) in dictionary.items()]


    ## Utilities Category ##

    utilities_d = []

    for i in range(0,len(date)):
        utilities_d.append((date[i],utilities[i]))

    dictionary = dict()

    for (date_v,value) in utilities_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    utilities_a = [(key, val) for (key, val) in dictionary.items()]


    ## Insurance Category ##

    insurance_d = []

    for i in range(0,len(date)):
        insurance_d.append((date[i],insurance[i]))

    dictionary = dict()

    for (date_v,value) in insurance_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    insurance_a = [(key, val) for (key, val) in dictionary.items()]


    ## Healthcare Category ##

    healthcare_d = []

    for i in range(0,len(date)):
        healthcare_d.append((date[i],healthcare[i]))

    dictionary = dict()

    for (date_v,value) in healthcare_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    healthcare_a = [(key, val) for (key, val) in dictionary.items()]


    ## Investment Category ##

    investment_d = []

    for i in range(0,len(date)):
        investment_d.append((date[i],investment[i]))

    dictionary = dict()

    for (date_v,value) in investment_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    investment_a = [(key, val) for (key, val) in dictionary.items()]


    ## Recreation Category ##

    recreation_d = []

    for i in range(0,len(date)):
        recreation_d.append((date[i],recreation[i]))

    dictionary = dict()

    for (date_v,value) in recreation_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    recreation_a = [(key, val) for (key, val) in dictionary.items()]


    ## Education Category ##

    education_d = []

    for i in range(0,len(date)):
        education_d.append((date[i],education[i]))

    dictionary = dict()

    for (date_v,value) in education_d:
        dictionary[date_v] = dictionary.get(date_v,0) + value

    education_a = [(key, val) for (key, val) in dictionary.items()]

    ## Miscellanous Category ##

    miscellanous_a = []

    for i in range(0,len(x)):
        miscellanous_a.append((x[i],debit_a[i][1]
                              - housing_a[i][1]
                              - food_a[i][1]
                              - transportation_a[i][1]
                              - utilities_a[i][1]
                              - insurance_a[i][1]
                              - healthcare_a[i][1]
                              - investment_a[i][1]
                              - recreation_a[i][1]
                              - personal_a[i][1]
                              - education_a[i][1]
                              ))



    ## Plotting Graph ##

    z1 = [y for (x,y) in housing_a]
    z2 = [y for (x,y) in food_a]
    z3 = [y for (x,y) in transportation_a]
    z4 = [y for (x,y) in utilities_a]
    z5 = [y for (x,y) in insurance_a]
    z6 = [y for (x,y) in healthcare_a]
    z7 = [y for (x,y) in investment_a]
    z8 = [y for (x,y) in recreation_a]
    z9 = [y for (x,y) in personal_a]
    z10 = [y for (x,y) in education_a]
    z11 = [y for (x,y) in miscellanous_a]

    u1 = [y for (x,y) in salary_a]
    u2 = [y for (x,y) in earnings_a]
    u3 = [y for (x,y) in miscellanousc_a]


    fig2, ax2 = plt.subplots(1, 1, figsize=(16,7), dpi= 96)

    n = len(x)
    index = np.arange(n)

    width = 0.125       

    p1 = plt.bar(index+0.0625, np.add(np.add(np.add(np.add(np.add(np.add(np.add(np.add(np.add(np.add(z11,z10),z9),z8),z7),z6),z5),z4),z3),z2),z1), width, label='Housing',color=[(0.4980,0.4980,0.4980)])
    p2 = plt.bar(index+0.0625, np.add(np.add(np.add(np.add(np.add(np.add(np.add(np.add(np.add(z11,z10),z9),z8),z7),z6),z5),z4),z3),z2), width, label='Food',color=[(0.7490,0.7490,0.7490)])
    p3 = plt.bar(index+0.0625, np.add(np.add(np.add(np.add(np.add(np.add(np.add(np.add(z11,z10),z9),z8),z7),z6),z5),z4),z3), width, label='Transportation',color=[(0.5176,0.2353,0.04706)])
    p4 = plt.bar(index+0.0625, np.add(np.add(np.add(np.add(np.add(np.add(np.add(z11,z10),z9),z8),z7),z6),z5),z4), width, label='Utilities',color=[(1.0000,0.0000,0.0000)])
    p5 = plt.bar(index+0.0625, np.add(np.add(np.add(np.add(np.add(np.add(z11,z10),z9),z8),z7),z6),z5), width, label='Insurance',color=[(1.0000,1.0000,0.0000)])
    p6 = plt.bar(index+0.0625, np.add(np.add(np.add(np.add(np.add(z11,z10),z9),z8),z7),z6), width, label='Healthcare',color=[(0.3294,0.5098,0.2078)])
    p7 = plt.bar(index+0.0625, np.add(np.add(np.add(np.add(z11,z10),z9),z8),z7), width, label='Investment',color=[(0.6627,0.8196,0.5569)])
    p8 = plt.bar(index+0.0625, np.add(np.add(np.add(z11,z10),z9),z8), width, label='Recreation',color=[(1.0000,0.8509,0.4000)])
    p9 = plt.bar(index+0.0625, np.add(np.add(z11,z10),z9), width, label='Personal',color=[(0.7490,0.5647,0.0000)])
    p10 = plt.bar(index+0.0625, np.add(z11,z10), width, label='Education',color=[(0.0000,0.0000,0.0000)])
    p11 = plt.bar(index+0.0625, z11, width, label='Other Debit',color=[(0.9569,0.6941,0.5137)])

    p12 = plt.bar(index-0.0625, np.add(np.add(u3,u2),u1), width, label='Salary',color=[(0.0000,0.4392,0.7529)])
    p13 = plt.bar(index-0.0625, np.add(u3,u2), width, label='Earnings',color=[(0.8627,0.0784,0.8431)])
    p14 = plt.bar(index-0.0625, u3, width, label='Other Credit',color=[(0.6157,0.7647,0.9020)])

    angle = 45
    if len(x) > 19:
        angle = round(len(x)/0.44,0)
    if angle > 90:
        angle = 90

    my_xticks = x
    plt.xticks(index,x,fontsize=14, rotation = angle, horizontalalignment='center',color='darkgrey')
    plt.yticks(fontsize=14,color='darkgrey')
    plt.xlim(-1.0)
    ax2.yaxis.grid(alpha=0.5)

    plt.yscale('log', basey=1.00001)

    from matplotlib.ticker import ScalarFormatter
    for axis in [ax2.yaxis]:
        axis.set_major_formatter(ScalarFormatter())

    plt.gca().spines["top"].set_alpha(0)
    plt.gca().spines["bottom"].set_alpha(0.5)
    plt.gca().spines["right"].set_alpha(0)
    plt.gca().spines["left"].set_alpha(0)

    plt.savefig('fig2.png',orientation='portrait',transparent=True, bbox_inches=None, pad_inches=0)


    ### Balance Graph ###

    from pandas.plotting import andrews_curves

    y1 = [y for (x,y) in credit_a]
    y2 = [y for (x,y) in debit_a]
    y3 = [y for (x,y) in balance_a]


    fig, ax = plt.subplots(1, 1, figsize=(16,7), dpi= 96)

    plt.plot(x,y3,label='Balance',color='black',linewidth=2.0)
    b1=plt.bar(index-0.0625,y1,label='Credit',color=[(0.06667,0.5647,0.7961)],width=0.125)
    b2=plt.bar(index+0.0625,y2,label='Debit',color=[(1,0.4118,0.4118)],width=0.125)


    plt.xticks(fontsize=14, rotation = angle, horizontalalignment='center',color='darkgrey')
    plt.yticks(fontsize=14,color='darkgrey')
    plt.xlim(-1.0)
    ax.yaxis.grid(alpha=0.5)
    plt.yscale('log', basey=1.00001)

    plt.text(x[0],y3[0] + 0.1*y3[0],'Start Balance\n' + str(locale.format_string('%d',int(y3[0]),1)),color='darkgrey',horizontalalignment='center',fontsize=14)
    plt.text(x[-1],y3[-1] + 0.1*y3[-1],'End Balance\n' + str(locale.format_string('%d',int(y3[-1]),1)),color='darkgrey',horizontalalignment='center',fontsize=14)


    from matplotlib.ticker import ScalarFormatter
    for axis in [ax.yaxis]:
        axis.set_major_formatter(ScalarFormatter())

    plt.gca().spines["top"].set_alpha(0)
    plt.gca().spines["bottom"].set_alpha(0.5)
    plt.gca().spines["right"].set_alpha(0)
    plt.gca().spines["left"].set_alpha(0)
    plt.savefig('fig1.png',orientation='portrait',transparent=True, bbox_inches=None, pad_inches=0)


bar_chart(date_array,balance_array,credit_array,debit_array,salary_array,
           earnings_array,housing_array,food_array,transportation_array,
           utilities_array,insurance_array,healthcare_array,investment_array,
           recreation_array,personal_array,education_array)

pdf.image('fig1.png',65,10,150,65)
pdf.image('fig2.png',65,80,150,65)


## Pie Charts ##

pdf.image('Salary.png',78,157.5,44,33)
pdf.image('Earnings.png',118,157.5,44,33)
pdf.image('Other Credit.png',158,157.5,44,33)

pdf.image('Housing.png',68,189.5,44,33)
pdf.image('Food.png',101,189.5,44,33)
pdf.image('Insurance.png',135,189.5,44,33)
pdf.image('Utilities.png',168,189.5,44,33)

pdf.image('Transportation.png',68,221.5,44,33)
pdf.image('Healthcare.png',101,221.5,44,33)
pdf.image('Recreation.png',135,221.5,44,33)
pdf.image('Personal.png',168,221.5,44,33)

pdf.image('Education.png',78,253.5,44,33)
pdf.image('Investment.png',118,253.5,44,33)
pdf.image('Other Debit.png',158,253.5,44,33)

## Pie Chart Values ##

# Credit Pie Chart Function #

def credit_pie(credit_category,x1,x2,x3,x4,y1,y2,y3):
               
    credit_category_val_p = int(round((credit_category/credit)*100,0))
    pdf.set_text_color(10,100,140)

    if credit_category_val_p == 100:
        pdf.set_xy(x1,y1)
        pdf.set_font('helvetica','',20)
        pdf.cell(10,10,str(credit_category_val_p),0,0,'C')
        pdf.set_xy(x2,y2)
        pdf.set_font('helvetica','',8)
        pdf.cell(10,10,'%',0,0,'C')
    if (credit_category_val_p < 100) and (credit_category_val_p >= 1):
        pdf.set_xy(x3,y1)
        pdf.set_font('helvetica','',20)
        pdf.cell(10,10,str(credit_category_val_p),0,0,'C')
        pdf.set_xy(x4,y2)
        pdf.set_font('helvetica','',8)
        pdf.cell(10,10,'%',0,0,'C')
    if credit_category_val_p < 1:
        pdf.set_xy(x3,y1)
        pdf.set_font('helvetica','',20)
        pdf.cell(10,10,'<1',0,0,'C')
        pdf.set_xy(x4,y2)
        pdf.set_font('helvetica','',8)
        pdf.cell(10,10,'%',0,0,'C')

    pdf.set_xy(x3,y3)
    pdf.set_font('helvetica','',9)
    credit_category_val = locale.format_string('%d',int(credit_category),1)
    pdf.cell(10,10,(currency + str(credit_category_val)),0,0,'C')

# Salary #
credit_pie(salary,94,101,95.5,100.7,167.5,168.7,172.5)

# Earnings #
credit_pie(earnings,134,141,135.5,140.7,167.5,168.7,172.5)

# Other Credit #
credit_pie(misc_credit,174,181,175.5,180.7,167.5,168.7,172.5)


# Debit Pie Chart Function #

def debit_pie(debit_category,x1,x2,x3,x4,y1,y2,y3,threshold):
    
    debit_category_val_p = int(round((debit_category/debit)*100,0))

    if debit_category_val_p <= threshold:
        pdf.set_text_color(112,173,71)
    else:
        pdf.set_text_color(210,0,0)

    if debit_category_val_p == 100:
        pdf.set_xy(x1,y1)
        pdf.set_font('helvetica','',20)
        pdf.cell(10,10,str(debit_category_val_p),0,0,'C')
        pdf.set_xy(x2,y2)
        pdf.set_font('helvetica','',8)
        pdf.cell(10,10,'%',0,0,'C')
    if (debit_category_val_p < 100) and (debit_category_val_p >= 1):
        pdf.set_xy(x3,y1)
        pdf.set_font('helvetica','',20)
        pdf.cell(10,10,str(debit_category_val_p),0,0,'C')
        pdf.set_xy(x4,y2)
        pdf.set_font('helvetica','',8)
        pdf.cell(10,10,'%',0,0,'C')
    if debit_category_val_p < 1:
        pdf.set_xy(x3,y1)
        pdf.set_font('helvetica','',20)
        pdf.cell(10,10,'<1',0,0,'C')
        pdf.set_xy(x4,y2)
        pdf.set_font('helvetica','',8)
        pdf.cell(10,10,'%',0,0,'C')

    pdf.set_xy(x3,y3)
    pdf.set_font('helvetica','',9)
    debit_category_val = locale.format_string('%d',int(debit_category),1)
    pdf.cell(10,2,(currency + str(debit_category_val)),0,0,'C')


def score_pie(value,x1,x2,x3,x4,y1,y2,s1,s2):

    if value >= 80:
        pdf.set_text_color(112,173,71)
    if (value < 80) and (value >= 60):
        pdf.set_text_color(244,177,131)
    if value < 60:
        pdf.set_text_color(255,105,105)

    if (value == 100) or (value < -9):
        pdf.set_xy(x1,y1)
        pdf.set_font('helvetica','',s1)
        pdf.cell(10,10,str(int(value)),0,0,'C')
        pdf.set_xy(x2,y2)
        pdf.set_font('helvetica','',s2)
        pdf.cell(10,10,'%',0,0,'C')
    else:
        pdf.set_xy(x3,y1)
        pdf.set_font('helvetica','',s1)
        pdf.cell(10,10,str(int(value)),0,0,'C')
        pdf.set_xy(x4,y2)
        pdf.set_font('helvetica','',s2)
        pdf.cell(10,10,'%',0,0,'C')


# Housing #
debit_pie(housing,84,91,85.5,90.7,199.5,200.7,208.5,35)

# Food #
debit_pie(food,117,124,118.5,123.7,199.5,200.7,208.5,15)

# Insurance #
debit_pie(insurance,151,158,152.5,157.7,199.5,200.7,208.5,25)

# Utilities #
debit_pie(utilities,184,191,185.5,190.7,199.5,200.7,208.5,10)

# Transportation #
debit_pie(transportation,84,91,85.5,90.7,231.5,232.7,240.5,15)

# Healthcare #
debit_pie(healthcare,117,124,118.5,123.7,231.5,232.7,240.5,10)

# Recreation #
debit_pie(recreation,151,158,152.5,157.7,231.5,232.7,240.5,10)

# Personal #
debit_pie(personal,184,191,185.5,190.7,231.5,232.7,240.5,10)

# Education #
debit_pie(education,94,101,95.5,100.7,263.5,264.7,272.5,20)

# Investment #
debit_pie(investment,134,141,135.5,140.7,263.5,264.7,272.5,20)

# Other Debit #
debit_pie(misc_debit,174,181,175.5,180.7,263.5,264.7,272.5,10)

# Debit Score #
pdf.image('Debit_score.png',-3,185.5,44,33)
score_pie(spending_score,13,20.7,14.5,20.6,197.6,198.8,25,8)

# Balance Score #
pdf.image('Balance_score.png',28,185.5,44,33)
score_pie(balance_score,44,51.7,45.5,51.6,197.6,198.8,25,8)

# Health Score #
pdf.image('Health_score.png',-10,218,88,66)
score_pie(health_score,28.7,42.1,30.2,42.0,246.9,249.1,44,17)

## Credit/Debit Values ##

debit_val = int(debit)
debit_val = locale.format_string('%d',int(debit_val),1)
if currency != '':
    debit_val = currency + debit_val

credit_val = int(credit)
credit_val = locale.format_string('%d',int(credit_val),1)
if currency != '':
    credit_val = currency + credit_val

credit_debit_balance_val = int(credit - debit)
credit_debit_balance_int = credit_debit_balance_val
credit_debit_balance_val = locale.format_string('%d',int(credit_debit_balance_val),1)
if currency != '':
    credit_debit_balance_val = currency + credit_debit_balance_val

pdf.set_font('helvetica','',22)
pdf.set_text_color(10,100,140)
pdf.set_xy(25,95)
pdf.cell(20,10,credit_val,0,0,'C')
pdf.set_text_color(210,0,0)
pdf.set_xy(25,131)
pdf.cell(20,10,debit_val,0,0,'C')

if credit_debit_balance_int < 0:
    pdf.set_text_color(210,0,0)
    pdf.set_xy(25,167)
    pdf.cell(20,10,credit_debit_balance_val,0,0,'C')
if credit_debit_balance_int > 0:
    pdf.set_text_color(112,173,71)
    pdf.set_xy(25,167)
    pdf.cell(20,10,credit_debit_balance_val,0,0,'C')

## Final Output ##
    
pdf.output('BankScan Report.pdf')
