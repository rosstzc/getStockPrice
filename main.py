# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# from dataProcess import *
# from doubleKlineMethod import *
from checkPolicy import *

from multiprocessing import Process

#在这个页面实现多进程： 1 把code分为100组； 2 用多进程读取每个组数据。


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import baostock as bs
import pandas as pd

#### 登陆系统 ####
lg = bs.login()
# # 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 获取沪深A股历史K线数据 ####
# 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
# 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
# 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
# rs = bs.query_history_k_data_plus("sh.600660",
#                                   # 0    1     2    3   4    5      6       7      8        9      10     11          12    13    14    15      16     17
#                                   # "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg",start_date='2015-01-01', end_date='2030-12-31', #周K线专用
#                                   # "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",                                  start_date='2015-01-01', end_date='2030-12-31',
#                                   "date,code,open,high,low,close",                                  start_date='2020-01-01', end_date='2030-12-31', #仅仅取价格
#     frequency="d", adjustflag="2")
#
#
# print('query_history_k_data_plus respond error_code:'+rs.error_code)
# print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)
#
# #### 打印结果集 ####
# data_list = []
# while (rs.error_code == '0') & rs.next():
#     # 获取一条记录，将记录合并在一起
#     data_list.append(rs.get_row_data())
# result = pd.DataFrame(data_list, columns=rs.fields)


### 结果集输出到csv文件 ####
#result.to_csv("/Users/miketam/Downloads/history_A_stock_k_data.csv",columns=rs.fields, index=False)
#print(result)

# print("333")

######这部分是我写的代码######################
# stockCode = ["300285","300572","000858","600887","600845","300122","000651","600519","002352","601318","300226","002142","002683","300760","300470","600031","601888","002271","600984","603599","603259","002475","600694","002311","000002","600600","002353","603501","000661","600036","300724","600309","603699","300573","601899","002461","603833","601933","000656","603866","603882","600729","002001","002643","002182","300628","600529","300144","300601","000501","600858","000951","300750","002434","600570","002007","002623","000538","603369","600426","300316","688111","600760","601012","600030","002511","002027","600323","600585","000596","600803","300454","300777","600276","300014","002129","300413","600486","300146","600048","300782","002409","603129","601139","000759","002415","603986","000636","300326","600522","300253","688268","300662","002555","600176","002179","688019","000333","601021","600436","002262","688188","601233","002013","600208","601688","000338","603160","600438","600697","600258","603288","300059","300015","002507","688518","688360","688181","688004","688568","688377","603087","688528","688600","300824","300842","600956","300839","300843","300840","300846","300498","002410","300661","600588","688023","002859","300408","300496","603613","002384","688012","002600","002938","688088","688158","688208","603039","688106","600216","300271","300639","688202","688389","603686","603960","688318","688080","603811","600809","000568","000860","000423","002032","002714","600104","600660","002304","600741","688189","688555","688277","688027","688096","300847","300845","600161","600763","600009","600066","600779","603737","002044","688266","600340","688398","300476","603520","000403","603890","300078","603887","300033","603290","002127","600416","002396","300298","300294","002153","600004","603444","000681","600967","600703","603786","002726","300010","002624","300633","300502","000157","002967","600745","002867","603232","002332","603712","300451","002920","300657","300012","002460","000910","688278","600380","300450","688029","300394","002990","688086","002912","688368","000977","600183","002666","002317","300113","688599","688200","688081","603707","300124","600521","002212","000739","002821","300009","000938","601166","603589","002120","002594","600690","603899","002050","002299","603486","603816","600754","600859","601799","000710","002773","300142","688030","300529","600559","002064","002398","688169","688298","688051","605166","300054","000786","603883","600882","600060","600038","002672","601100","002707","600517","002572","603955","300629","603839","300136","300207","600406","000625","300735","300433","300347","300709","002223","002236","000963","600000","601138","600026","600016","601668","002146","600837","600900","300003","603583","600352","002916","002202","600346","601658","601009","002841","002371","601872","300559","002111","300596","002540","002020","002851","600580","601229","601865","002746","002405","603338","600801","601601","002157","600846","600597","601088","002035","300179","000718","300571","600547","002465","300609","002563","601398","600777","002273","300725","002508","601225","002440","300487","601238","300631","000001","300034","601128","603658","002128","002812","600050","000598","600919","603489","300699","603043","601169","603018","600395","002690","002832","300719","601966","601288","688505","601155","300690","300488","002458","688157","300463","000063","603708","002080","002901","600201","603345","603885","002138","300595","300206","300674","300816","000725","600976","002705","603517","688166","600872","300616","601816","601111","688520","688399","688196","688198","600918","300832","603392","601778","601827","002989","300831","300837","002986","605001","300833","300830","603950","300838","002988","300315","000513","300037","300251","002456","000049","002727","603533","002351","603195","300133","002251","300791","603060","300031","001914","002241","002240","300562","002385","688036","300171","002601","600771","002884","688598","688365","600116","300677","300630","300357","300759","603987","300363","603939","603229","688016","603127","603456","300702","300482","300453","300753","603538","603233","002675","688108","300149","688366","300558","300497","688466","688090","688159","688218","600055","300036","603700","300259","002607","688233","688228","002439","603308","300188","002216","000998","002982","300788","002837","603856","002866","603258","688008","603668","688037","688558","600383","002831","002810","603096","000961","002049","300452","000004","603506","000671","002368","300659","603019","601116","688002","600054","688026","000888","603199","600536","300212","600584","600085","300548","300604","300457","300731","300455","688039","688396","601916","688085","601077","688222","688566","688312","688186","688199","688516","000895","600132","002557","002697","002597","002749","600185","600315","300773","002706","300073","603515","300568","002056","300766","600673","300001","603197","603788","300203","300383","603920","300580","603239","603601","002965","688116","002382","688300","002709","688025","600305","603688","600556","002185","002078","600720","002791","600885","601628","002008","600886","603799","603605","002648","000902","002463","002025","600029","600195","300567","601939","600674","603659","603214","600612","300676","300223","603893","002230","600131","002930","000100","002928","002949","600273","603416","300087","600862","603558","603186","300772","300083","300115","002845","600563","603078","300088","300373","300308","603881","002429","002180","603636","600114","603083","002373","300623","603516","600850","002063","300066","000021","300686","603327","002125","002897","300319","000066","000570","688138","300465","601231","002579","600640","002583","300348","000050","600367","603936","601689","300666","000997","000156","000555","603297","300327","002971","000878","300655","600362","002655","002428","000034","000925","000936","300377","300738","300607","600203","002156","300161","002635","002387","000733","600330","600601","603496","603203","300679","002034","603228","603005","603026","300460","603738","300075","300671","600499","300390","300097","002913","300379","603722","603993","300438","002189","002786","688126","603519","603989","002426","300041","300638","002518","002947","002695","688099","002530","688058","002364","300296","300398","000581","002158","603267","688015","603678","600460","300302","300726","002959","002902","002436","300046","300007","600966","300328","002028","601828","603283","300624","300310","601311","300531","300769","000970","601698","000969","002609","300098","300618","000009","600487","300369","601869","688177","002962","603068","300416","300168","002152","600271","000030","601137","002065","300613","300068","603690","600100","002292","600718","002055","002739","002117","688020","002171","002484","688588","688066","688139","600583","603378","688033","688123","000401","300458","300737","002043","688021","002918","002777","688258","600835","002756","002747","688089","002798","000877","002641","600378","000800","002074","603385","603661","688118","002372","002745","603801","688310","600711","000807","002126","603260","603301","002970","300423","002497","300747","603208","002466","002815","300684","300803","603719","300706","300821","300481","002084","603755","002250","300768","603739","002987","300634","002980","603348","603967","300787","603610","300749","603982","300806","002983","300825","300801","002978","300694","002973","002972","600812","002925","600480","601336","000921","002422","601818","002048","600115","300070","600681","603626"]
# stockCode = ["600760","601012","600030","002511","002027","600323","600585","000596","600803","300454","300777","600276","300014","002129","300413","600486","300146","600048","300782","002409","603129","601139","000759","002415","603986","000636","300326","600522","300253","688268","300662","002555","600176","002179","688019","000333","601021","600436","002262","688188","601233","002013","600208","601688","000338","603160","600438","600697","600258","603288","300059","300015","002507","688518","688360","688181","688004","688568","688377","603087","688528","688600","300824","300842","600956","300839","300843","300840","300846","300498","002410","300661","600588","688023","002859","300408","300496","603613","002384","688012","002600","002938","688088","688158","688208","603039","688106","600216","300271","300639","688202","688389","603686","603960","688318","688080","603811","600809","000568","000860","000423","002032","002714","600104","600660","002304","600741","688189","688555","688277","688027","688096","300847","300845","600161","600763","600009","600066","600779","603737","002044","688266","600340","688398","300476","603520","000403","603890","300078","603887","300033","603290","002127","600416","002396","300298","300294","002153","600004","603444","000681","600967","600703","603786","002726","300010","002624","300633","300502","000157","002967","600745","002867","603232","002332","603712","300451","002920","300657","300012","002460","000910","688278","600380","300450","688029","300394","002990","688086","002912","688368","000977","600183","002666","002317","300113","688599","688200","688081","603707","300124","600521","002212","000739","002821","300009","000938","601166","603589","002120","002594","600690","603899","002050","002299","603486","603816","600754","600859","601799","000710","002773","300142","688030","300529","600559","002064","002398","688169","688298","688051","605166","300054","000786","603883","600882","600060","600038","002672","601100","002707","600517","002572","603955","300629","603839","300136","300207","600406","000625","300735","300433","300347","300709","002223","002236","000963","600000","601138","600026","600016","601668","002146","600837","600900","300003","603583","600352","002916","002202","600346","601658","601009","002841","002371","601872","300559","002111","300596","002540","002020","002851","600580","601229","601865","002746","002405","603338","600801","601601","002157","600846","600597","601088","002035","300179","000718","300571","600547","002465","300609","002563","601398","600777","002273","300725","002508","601225","002440","300487","601238","300631","000001","300034","601128","603658","002128","002812","600050","000598","600919","603489","300699","603043","601169","603018","600395","002690","002832","300719","601966","601288","688505","601155","300690","300488","002458","688157","300463","000063","603708","002080","002901","600201","603345","603885","002138","300595","300206","300674","300816","000725","600976","002705","603517","688166","600872","300616","601816","601111","688520","688399","688196","688198","600918","300832","603392","601778","601827","002989","300831","300837","002986","605001","300833","300830","603950","300838","002988","300315","000513","300037","300251","002456","000049","002727","603533","002351","603195","300133","002251","300791","603060","300031","001914","002241","002240","300562","002385","688036","300171","002601","600771","002884","688598","688365","600116","300677","300630","300357","300759","603987","300363","603939","603229","688016","603127","603456","300702","300482","300453","300753","603538","603233","002675","688108","300149","688366","300558","300497","688466","688090","688159","688218","600055","300036","603700","300259","002607","688233","688228","002439","603308","300188","002216","000998","002982","300788","002837","603856","002866","603258","688008","603668","688037","688558","600383","002831","002810","603096","000961","002049","300452","000004","603506","000671","002368","300659","603019","601116","688002","600054","688026","000888","603199","600536","300212","600584","600085","300548","300604","300457","300731","300455","688039","688396","601916","688085","601077","688222","688566","688312","688186","688199","688516","000895","600132","002557","002697","002597","002749","600185","600315","300773","002706","300073","603515","300568","002056","300766","600673","300001","603197","603788","300203","300383","603920","300580","603239","603601","002965","688116","002382","688300","002709","688025","600305","603688","600556","002185","002078","600720","002791","600885","601628","002008","600886","603799","603605","002648","000902","002463","002025","600029","600195","300567","601939","600674","603659","603214","600612","300676","300223","603893","002230","600131","002930","000100","002928","002949","600273","603416","300087","600862","603558","603186","300772","300083","300115","002845","600563","603078","300088","300373","300308","603881","002429","002180","603636","600114","603083","002373","300623","603516","600850","002063","300066","000021","300686","603327","002125","002897","300319","000066","000570","688138","300465","601231","002579","600640","002583","300348","000050","600367","603936","601689","300666","000997","000156","000555","603297","300327","002971","000878","300655","600362","002655","002428","000034","000925","000936","300377","300738","300607","600203","002156","300161","002635","002387","000733","600330","600601","603496","603203","300679","002034","603228","603005","603026","300460","603738","300075","300671","600499","300390","300097","002913","300379","603722","603993","300438","002189","002786","688126","603519","603989","002426","300041","300638","002518","002947","002695","688099","002530","688058","002364","300296","300398","000581","002158","603267","688015","603678","600460","300302","300726","002959","002902","002436","300046","300007","600966","300328","002028","601828","603283","300624","300310","601311","300531","300769","000970","601698","000969","002609","300098","300618","000009","600487","300369","601869","688177","002962","603068","300416","300168","002152","600271","000030","601137","002065","300613","300068","603690","600100","002292","600718","002055","002739","002117","688020","002171","002484","688588","688066","688139","600583","603378","688033","688123","000401","300458","300737","002043","688021","002918","002777","688258","600835","002756","002747","688089","002798","000877","002641","600378","000800","002074","603385","603661","688118","002372","002745","603801","688310","600711","000807","002126","603260","603301","002970","300423","002497","300747","603208","002466","002815","300684","300803","603719","300706","300821","300481","002084","603755","002250","300768","603739","002987","300634","002980","603348","603967","300787","603610","300749","603982","300806","002983","300825","300801","002978","300694","002973","002972","600812","002925","600480","601336","000921","002422","601818","002048","600115","300070","600681","603626"]
# stockCode = ["300285","300572","000858","600887","600845","300122","000651","600519","002352"]
#stockCode = ["600309","300677","600276","300015","002352","300760"]
#stockCode = ["000001","600660","600309","300677","600276","300015","002352","300760"]
            # 平安银行， 福耀玻璃，万华化学，英科医疗，恒瑞医药，   爱尔眼科，顺丰控股， 迈瑞医疗
#沪深300
# stockCode = ["000001",	"000002",	"000063",	"000066",	"000069",	"000100",	"000157",	"000166",	"000333",	"000338",	"000425",	"000538",	"000568",	"000596",	"000625",	"000627",	"000651",	"000656",	"000661",	"000671",	"000703",	"000709",	"000708",	"000723",	"000725",	"000728",	"000768",	"000776",	"000783",	"000786",	"000858",	"000860",	"000876",	"000895",	"000938",	"000961",	"000963",	"000977",	"001979",	"002001",	"002008",	"002007",	"002024",	"002027",	"002032",	"002044",	"002050",	"002120",	"002129",	"002142",	"002146",	"002153",	"002157",	"002179",	"002202",	"002230",	"002236",	"002241",	"002252",	"002271",	"002304",	"002311",	"002352",	"002371",	"002410",	"002415",	"002422",	"002456",	"002460",	"002463",	"002466",	"002468",	"002475",	"002493",	"002508",	"002555",	"002558",	"002594",	"002601",	"002602",	"002607",	"002624",	"002673",	"002714",	"002736",	"002739",	"002773",	"002841",	"002916",	"002939",	"002938",	"002945",	"002958",	"003816",	"300003",	"300014",	"300015",	"300033",	"300059",	"300122",	"300124",	"300136",	"300142",	"300144",	"300347",	"300408",	"300413",	"300433",	"300498",	"300601",	"300628",	"600000",	"600004",	"600009",	"600010",	"600011",	"600015",	"600016",	"600018",	"600019",	"600025",	"600027",	"600028",	"600029",	"600030",	"600031",	"600036",	"600038",	"600048",	"600050",	"600061",	"600066",	"600068",	"600085",	"600089",	"600104",	"600109",	"600111",	"600115",	"600118",	"600170",	"600176",	"600177",	"600183",	"600188",	"600196",	"600208",	"600219",	"600221",	"600233",	"600271",	"600276",	"600297",	"600299",	"600309",	"600332",	"600340",	"600346",	"600352",	"600362",	"600369",	"600372",	"600383",	"600390",	"600398",	"600406",	"600436",	"600438",	"600482",	"600487",	"600489",	"600498",	"600516",	"600519",	"600522",	"600547",	"600570",	"600583",	"600585",	"600588",	"600606",	"600637",	"600655",	"600660",	"600674",	"600690",	"600703",	"600705",	"600741",	"600745",	"600760",	"600795",	"600809",	"600837",	"600848",	"600867",	"600886",	"600887",	"600893",	"600900",	"600919",	"600926",	"600928",	"600958",	"600968",	"600977",	"600989",	"600998",	"600999",	"601006",	"601009",	"601012",	"601018",	"601021",	"601066",	"601077",	"601088",	"601100",	"601108",	"601111",	"601117",	"601138",	"601155",	"601162",	"601166",	"601169",	"601186",	"601198",	"601211",	"601212",	"601216",	"601225",	"601229",	"601231",	"601238",	"601236",	"601288",	"601298",	"601319",	"601318",	"601328",	"601336",	"601360",	"601377",	"601390",	"601398",	"601555",	"601577",	"601600",	"601601",	"601607",	"601618",	"601628",	"601633",	"601658",	"601668",	"601669",	"601688",	"601698",	"601727",	"601766",	"601788",	"601800",	"601808",	"601816",	"601818",	"601828",	"601838",	"601857",	"601877",	"601878",	"601881",	"601888",	"601898",	"601899",	"601901",	"601916",	"601919",	"601933",	"601939",	"601985",	"601988",	"601989",	"601992",	"601997",	"601998",	"603019",	"603156",	"603160",	"603259",	"603260",	"603288",	"603369",	"603501",	"603658",	"603799",	"603833",	"603899",	"603986",	"603993",]
# stockName  = ["平安银行",	"万科A",	  "中兴通讯",	"中国长城",	"华侨城A",	"TCL科技",	"中联重科",	"申万宏源",	"美的集团",	"潍柴动力",	"徐工机械",	"云南白药",	"泸州老窖",	"古井贡酒",	"长安汽车",	"天茂集团",	"格力电器",	"金科股份",	"长春高新",	"阳光城",	"恒逸石化",	"河钢股份",	"中信特钢",	"美锦能源",	"京东方A",	"国元证券",	"中航飞机",	"广发证券",	"长江证券",	"北新建材",	"五粮液",	"顺鑫农业",	"新希望",	"双汇发展",	"紫光股份",	"中南建设",	"华东医药",	"浪潮信息",	"招商蛇口",	"新和成",	"大族激光",	"华兰生物",	"苏宁易购",	"分众传媒",	"苏泊尔",	"美年健康",	"三花智控",	"韵达股份",	"中环股份",	"宁波银行",	"荣盛发展",	"石基信息",	"正邦科技",	"中航光电",	"金风科技",	"科大讯飞",	"大华股份",	"歌尔股份",	"上海莱士",	"东方雨虹",	"洋河股份",	"海大集团",	"顺丰控股",	"北方华创",	"广联达",	"海康威视",	"科伦药业",	"欧菲光",	"赣锋锂业",	"沪电股份",	"天齐锂业",	"申通快递",	"立讯精密",	"荣盛石化",	"老板电器",	"三七互娱",	"巨人网络",	"比亚迪",	"龙蟒佰利",	"世纪华通",	"中公教育",	"完美世界",	"西部证券",	"牧原股份",	"国信证券",	"万达电影",	"康弘药业",	"视源股份",	"深南电路",	"长城证券",	"鹏鼎控股",	"华林证券",	"青农商行",	"中国广核",	"乐普医疗",	"亿纬锂能",	"爱尔眼科",	"同花顺",	"东方财富",	"智飞生物",	"汇川技术",	"信维通信",	"沃森生物",	"宋城演艺",	"泰格医药",	"三环集团",	"芒果超媒",	"蓝思科技",	"温氏股份",	"康泰生物",	"亿联网络",	"浦发银行",	"白云机场",	"上海机场",	"包钢股份",	"华能国际",	"华夏银行",	"民生银行",	"上港集团",	"宝钢股份",	"华能水电",	"华电国际",	"中国石化",	"南方航空",	"中信证券",	"三一重工",	"招商银行",	"中直股份",	"保利地产",	"中国联通",	"国投资本",	"宇通客车",	"葛洲坝",	"同仁堂",	"特变电工",	"上汽集团",	"国金证券",	"北方稀土",	"东方航空",	"中国卫星",	"上海建工",	"中国巨石",	"雅戈尔",	"生益科技",	"兖州煤业",	"复星医药",	"新湖中宝",	"南山铝业",	"海航控股",	"圆通速递",	"航天信息",	"恒瑞医药",	"广汇汽车",	"安迪苏",	"万华化学",	"白云山",	"华夏幸福",	"恒力石化",	"浙江龙盛",	"江西铜业",	"西南证券",	"中航电子",	"金地集团",	"五矿资本",	"海澜之家",	"国电南瑞",	"片仔癀",	"通威股份",	"中国动力",	"亨通光电",	"中金黄金",	"烽火通信",	"方大炭素",	"贵州茅台",	"中天科技",	"山东黄金",	"恒生电子",	"海油工程",	"海螺水泥",	"用友网络",	"绿地控股",	"东方明珠",	"豫园股份",	"福耀玻璃",	"川投能源",	"海尔智家",	"三安光电",	"中航资本",	"华域汽车",	"闻泰科技",	"中航沈飞",	"国电电力",	"山西汾酒",	"海通证券",	"上海临港",	"通化东宝",	"国投电力",	"伊利股份",	"航发动力",	"长江电力",	"江苏银行",	"杭州银行",	"西安银行",	"东方证券",	"海油发展",	"中国电影",	"宝丰能源",	"九州通",	"招商证券",	"大秦铁路",	"南京银行",	"隆基股份",	"宁波港",	"春秋航空",	"中信建投",	"渝农商行",	"中国神华",	"恒立液压",	"财通证券",	"中国国航",	"中国化学",	"工业富联",	"新城控股",	"天风证券",	"兴业银行",	"北京银行",	"中国铁建",	"东兴证券",	"国泰君安",	"白银有色",	"君正集团",	"陕西煤业",	"上海银行",	"环旭电子",	"广汽集团",	"红塔证券",	"农业银行",	"青岛港",	"中国人保",	"中国平安",	"交通银行",	"新华保险",	"三六零",	"兴业证券",	"中国中铁",	"工商银行",	"东吴证券",	"长沙银行",	"中国铝业",	"中国太保",	"上海医药",	"中国中冶",	"中国人寿",	"长城汽车",	"邮储银行",	"中国建筑",	"中国电建",	"华泰证券",	"中国卫通",	"上海电气",	"中国中车",	"光大证券",	"中国交建",	"中海油服",	"京沪高铁",	"光大银行",	"美凯龙",	"成都银行",	"中国石油",	"正泰电器",	"浙商证券",	"中国银河",	"中国中免",	"中煤能源",	"紫金矿业",	"方正证券",	"浙商银行",	"中远海控",	"永辉超市",	"建设银行",	"中国核电",	"中国银行",	"中国重工",	"金隅集团",	"贵阳银行",	"中信银行",	"中科曙光",	"养元饮品",	"汇顶科技",	"药明康德",	"合盛硅业",	"海天味业",	"今世缘",	"韦尔股份",	"安图生物",	"华友钴业",	"欧派家居",	"晨光文具",	"兆易创新",	"洛阳钼业",]

# stockCode = ["000001",	"000002",	"000063"]
# stockName =  ["平安银行",	"万科A",	  "中兴通讯"]
#行业龙头: https://xueqiu.com/7639513890/143988644
# stockCode =["600519", 	"600276", 	"600887", 	"603288", 	"601318", 	"603517", 	"600900", 	"000002", 	"002594", 	"000651", 	"000333", 	"600660", 	"600332", 	"002230", 	"300144", 	"000538", 	"600436", 	"600993", 	"600585", 	"002024", 	"002415", 	"002223", 	"002739", 	"600305", 	"000895", 	"300015", 	"002352", 	"600315", 	"002001", 	"002003", 	"002004", 	"002007", 	"002008", 	"002010", 	"002022", 	"002028", 	"002030", 	"002031", 	"002041", 	"002045", 	"002046", 	"002048", 	"002056", 	"002063", 	"002073", 	"002080", 	"002090", 	"002091", 	"002094", 	"002098", 	"002101", 	"002103", 	"002014", 	"002106", 	"002111", 	"002117", 	"002119", 	"002121", 	"002125", 	"002126", 	"002130", 	"002131", 	"002138", 	"002139", 	"002140", 	"002144", 	"002149", 	"002151", 	"002158", 	"002160", 	"002161", 	"002176", 	"002179", 	"002182", 	"002183", 	"002190", 	"002196", 	"002197", 	"002201", 	"002202", 	"002206", 	"002209", 	"002211", 	"002213", 	"002218", 	"002222", 	"002224", 	"002225", 	"002232", 	"002242", 	"002243", 	"002246", 	"002258", 	"002265", 	"002273", 	"002282", 	"002283", 	"002284", 	"002335", 	"002337", 	"002341", 	"002348", 	"002402", 	"002403", 	"002405", 	"002406", 	"002407", 	"002408", 	"002409", 	"002410", 	"002414", 	"002420", 	"002423", 	"002428", 	"002430", 	"002436", 	"002438", 	"002443", 	"002444", 	"002446", 	"002448", 	"002449", 	"002454", 	"002455", 	"002458", 	"002459", 	"002460", 	"300001", 	"300004", 	"300011", 	"300012", 	"300014", 	"300016", 	"300017", 	"300019", 	"300024", 	"300026", 	"300027", 	"300030", 	"300032", 	"300037", 	"300045", 	"300046", 	"300049", 	"300053", 	"300054", 	"300058", 	"300059", 	"300062", 	"300063", 	"300065", 	"300067", 	"300070", 	"300072", 	"300073", 	"300074", 	"300075", 	"300077", 	"300082", 	"300084", 	"300085", 	"300091", 	"300093", 	"300095", 	"300097", 	"300137", ]
# stockName = ["贵州茅台", 	"恒瑞医药", 	"伊利股份", 	"海天味业", 	"中国平安", 	"绝味食品", 	"长江电力", 	"万科", 	"比亚迪", 	"格力电器", 	"美的集团", 	"福耀玻璃", 	"白云山", 	"科大讯飞", 	"宋城演艺", 	"云南白药", 	"片仔癀", 	"马应龙", 	"海螺水泥", 	"苏宁易购", 	"海康威视", 	"鱼跃医疗", 	"万达电影", 	"恒顺醋业", 	"双汇发展", 	"爱尔眼科", 	"顺丰控股", 	"上海家化", 	"新和成", 	"伟星股份", 	"华邦健康", 	"华兰生物", 	"大族激光", 	"传化智联", 	"科华生物", 	"思源电气", 	"达安基因", 	"巨轮智能", 	"登海种业", 	"国光电器", 	"轴研科技", 	"宁波华翔", 	"横店东磁", 	"远光软件", 	"软控股份", 	"中材科技", 	"金智科技", 	"江苏国泰", 	"青岛金王", 	"浔兴股份", 	"广东鸿图", 	"广博股份", 	"恒宝股份", 	"莱宝高科", 	"威海广泰", 	"东港股份", 	"康强电子", 	"科陆电子", 	"湘潭电化", 	"银轮股份", 	"沃尔核材", 	"利欧股份", 	"顺络电子", 	"拓邦股份", 	"东华科技", 	"宏达高科", 	"西部材料", 	"北斗星通", 	"汉钟精机", 	"常铝股份", 	"远望谷", 	"江特电机", 	"中航光电", 	"云海金属", 	"怡亚通", 	"成飞集成", 	"方正电机", 	"证通电子", 	"九鼎新材", 	"金风科技", 	"海利得", 	"达意隆", 	"宏达新材", 	"特尔佳", 	"拓日新能", 	"福晶科技", 	"三力士", 	"濮耐股份", 	"启明信息", 	"九阳股份", 	"通产丽星", 	"北化股份", 	"利尔化学", 	"西仪股份", 	"水晶光电", 	"博深工具", 	"天润曲轴", 	"亚太股份", 	"科华恒盛", 	"赛象科技", 	"新纶科技", 	"高乐股份", 	"和而泰", 	"爱仕达", 	"四维图新", 	"远东传动", 	"多氟多", 	"齐翔腾达", 	"雅克科技", 	"广联达", 	"高德红外", 	"毅昌股份", 	"中原特钢", 	"云南锗业", 	"杭氧股份", 	"兴森科技", 	"江苏神通", 	"金洲管道", 	"巨星科技", 	"盛路通信", 	"中原内配", 	"国星光电", 	"松芝股份", 	"百川股份", 	"益生股份", 	"天业通联", 	"赣锋锂业", 	"特锐德", 	"南风股份", 	"鼎汉技术", 	"华测检测", 	"亿纬锂能", 	"北陆药业", 	"网宿科技", 	"硅宝科技", 	"机器人", 	"红日药业", 	"华谊兄弟", 	"阳普医疗", 	"金龙机电", 	"新宙邦", 	"华力创通", 	"台基股份", 	"福瑞股份", 	"欧比特", 	"鼎龙股份", 	"蓝色光标", 	"东方财富", 	"中能电气", 	"天龙集团", 	"海兰信", 	"安诺其", 	"碧水源", 	"三聚环保", 	"当升科技", 	"华平股份", 	"数字政通", 	"国民技术", 	"奥克股份", 	"海默科技", 	"银之杰", 	"金通灵", 	"金刚玻璃", 	"华伍股份", 	"智云股份", 	"先河环保",]

#2020-11-2
# stockCode = ["002044",	"002129",	"002153",	"002252","000656"]

#2020-12-1
# stockCode = ["002007",	"002024",	"002027",	"002352","002027" ,"002475" ,"002773" ,"300408"]
# stockCode = ["002001",	"300122",	"600196",	"600309","600588" ]

#2020-12-1 晚
# stockCode = ["002241","300015","300347","300413", "600570", "601933", "001979" ]

# 石基信息(SZ: 002153)，上海莱士(SZ:002252)，中环股份(SZ:002129)
# stockCode = ["002153","002252","002129"]
#
stockName = ['']
# stockCode = ["002001"] #x新和成
# stockCode = ["000001"] #平安银行
# stockCode = ["000651"] #格力电器
# stockCode = ["002007"] #华兰
# stockCode = ["600487"] # 亨通光电
# stockCode = ["002230"] #
# stockCode = ["002153"] #石基
# stockCode = ["000776"]
stockCode = ["001979"] #招商
# stockCode = ["300572","300285"]
# 获取季度数据
# getSeasonData(stockCode)





#交易策略执行
checkPolicy(stockCode,stockName)

#数据处理，主要通过for循环来处理的数据
# processFor(stockCode,1,stockName, 'filePath')  #1表示网上取数据并导出文件， 0表示在本地取数据，也不导出文件; 2 直接读取已经过process的csv文件。


#根据K线数据进行数据二次处理，主要是通过df来处理
# processKline(stockCode,0)

#计算均线动态（目前沪深300成分股的5日、10日的均线动态）
# getMaLineTrend(stockCode,stockName)

#最原始但K线数据
# getOnlyKline(stockCode)

#经过处理后但K线数据
#getKlineData(stockCode)

# getKlineDataSplit(stockCode)



# def fun1(name):
#     print('测试%s多进程' %name)
#
# if __name__ == '__main__':
#     print('这里执行几次乐')
#     array = []
#     process_list = []
#     p = Process
#     for i in range(10):  #开启5个子进程执行fun1函数
#         # fun1("dddd")
#
#         p = Process(target=fun1,args=('Python',)) #实例化进程对象
#         p.start()
#         process_list.append(p)
#         # p.join()
#     for i in process_list:
#         p.join()
#
#     print('结束测试')


#
# #
# import multiprocessing
# def func(c):
#     lg = bs.login()
#     test = getKlineDataOne(c)
#     lg = bs.logout()
#     return  test
#
# if __name__ == "__main__":
#     pool = multiprocessing.Pool(processes=100) # 创建4个进程
#     res_list = []
#     good_res_list = []
#
#     for i in stockCode:  #若4个进程，每次同时执行4个
#         res = pool.apply_async(func, (i,))
#         # good_res_list.extend(res.get()) #单进程逻辑
#         res_list.append(res)
#     pool.close() # 关闭进程池，表示不能在往进程池中添加进程
#     pool.join() # 等待进程池中的所有进程执行完毕，必须在close()之后调用
#     print("Sub-process(es) done.")
#     print("Sub-process(es) done.")
#     print("Sub-process(es) done.")
#     print("Sub-process(es) done.")
#     print("Sub-process(es) done.")
#
#     for res in res_list: #之前一直有错误，很可能是进程未结果，就调用，所以必须先close进程。
#         good_res = res.get()
#         if good_res:
#             good_res_list.extend(good_res)
#
#     # print(good_res_list)
#     resultMulti = pd.DataFrame(good_res_list)
#
#     resultMulti.to_csv("/Users/miketam/Downloads/getKlineDataMultiProcess.csv",  encoding="gbk", index=False)

######这部分是我写的代码########################


#### 登出系统 ####
bs.logout()


