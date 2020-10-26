import datetime
from multiprocessing import Process



def codeFormat(code):
    temp = code[0:1]
    if temp == '3' or temp == '0':
        # print("深交所代码")
        code = "sz." + code
    else:
        code = "sh." + code
    #print(code)
    return code


def dateSeasonFormat(date):
    dateStr = date
    data_time = datetime.datetime.strptime(dateStr, '%Y-%m-%d')  # 把字符转换为时间格式
    DATETIME_FORMAT = '%Y'
    yearStr = data_time.strftime(DATETIME_FORMAT)  # 把时间格式转换为字符
    quarter = (data_time.month - 1) // 3 + 1
    yearQuarter = yearStr + "Q" + str(quarter)
    date = yearQuarter  # 修改日期为 XXXX年XX季度
    # print( i[0] + "，" + i[1] +  "，" + i[5])
    return date



def func1(args):
    print('测试%s多进程' %args)

def multiProcess():
    process_list = []
    # for i in range(1):
    p = Process(target=func1, args=('test',))
    p.start()
    p.join()
    # process_list.append(p)
    # for i in process_list:
    #     p.join()
    print("test finish")