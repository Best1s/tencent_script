# -*- coding: utf-8 -*-
# api https://console.cloud.tencent.com/api/explorer?Product=monitor&Version=2018-07-24&Action=DescribeBaseMetrics&SignVersion= 

# https://cloud.tencent.com/document/product/248/45146
import pylab as mpl     #import matplotlib as mpl
import numpy as np 
from matplotlib import pyplot as plt
from getInstanceId import get_cvm_instanceid,get_monitor_date,get_cdb_instanceid,get_redis_instanceid
import time
import json
import os.path
from jinja2 import  Environment, FileSystemLoader
import requests
import math

mpl.rcParams['font.sans-serif'] = ['FangSong']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
nowtime = time.time()
stime = time.strftime("%Y-%m-%d %H:00:00", time.localtime(nowtime - 604800))
etime = time.strftime("%Y-%m-%d %H:00:01", time.localtime(nowtime ))    
titletime = etime[:10]
js_paths = []
alertInfo = []
picName = []
js_ids = []

def dingtalk_robot(htmlname):
    url = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxxxxx"
    headers = {'Content-Type':'application/json'}
    link = htmlname.split(".")[0] + "日线上服务器巡检报告已生成\n\n[点击：http://192.168.x.xx" + htmlname +"](http://192.168.xx.xx"+ htmlname+ ")\n\n"
    data_dict = {
        "msgtype":"markdown",
        "markdown":{
            "title":"巡检报告",
            "text":link
        }
    }

    json_data =json.dumps(data_dict)

    #response = requests.post(url, data=json_data,headers=headers)
    #print(response.text)        # {"errcode":0,"errmsg":"ok"}

def create_file(filename,content):
    with open(filename, 'w') as f:
        f.write(content)
        f.close()

def crete_html():
    htmlname = titletime + ".html"
    path = os.path.dirname(__file__)
    loader = FileSystemLoader(path)
    env = Environment(loader=loader)
    title = stime[:10] + " -- " + etime 
    template = env.get_template('./templates/base.html')   
    content = template.render({"title":titletime,"js_ids":js_ids,"js_paths":js_paths,"cvmNum":cvmNum,"cdbNum":cdbNum})
    with open("./html/" + htmlname, 'w') as f:
        f.write(content)
        f.close()
    dingtalk_robot(htmlname)

def create_js(title,data,metric,instanceid_name):
    id = titletime + metric
    js_ids.append(id)
    js_file_path= "./js/" + id + ".js"
    print("creating ",js_file_path)
    js_paths.append(js_file_path)
    data = json.loads(data,encoding='utf-8')
    sort_data = analyse_metric_data(data)
    new_data = {}
    date = []
    maxInstanceId = {}
    nowInstanceId = {}
    topMaxInstanceId = []
    topNowInstanceId = []
    #print(data)
    for i in sort_data.keys():
        value = sort_data.get(i).get("Values")
        i = instanceid_name.get(i)
        try:
            maxInstanceId[i] = max(value)
            nowInstanceId[i] = value[-1]
        except ValueError:
            maxInstanceId[i] = 0           
            nowInstanceId[i] = 0
            
    topMaxInstanceId = dict(sorted(maxInstanceId.items(), key=lambda e: e[1])[-15:])
    topNowInstanceId = dict(sorted(nowInstanceId.items(), key=lambda e: e[1])[-15:])
    for instanceid in instanceid_name.keys():
        try:
            new_data[instanceid_name.get(instanceid)] = sort_data.get(instanceid).get("Values")
        except:
            #print(new_data[instanceid_name.get(instanceid)],sort_data.get(instanceid,""))
            continue
        if len(date) < len(sort_data.get(instanceid).get("Timestamps")):
            date = sort_data.get(instanceid).get("Timestamps")
    date = timestamps_convert_date(date)
    path = os.path.dirname(__file__)
    loader = FileSystemLoader(path)
    env = Environment(loader=loader)
    template = env.get_template('./templates/base.js.html')   
    content = template.render({ "title":title, "instanceid_name":list(topNowInstanceId.keys()), "date":date, "data":new_data, "id":id })
    with open("./html/" + js_file_path, 'w') as f:
        f.write(content)
        f.close()



def timestamps_convert_date(dates):
    """
    ：时间戳转成日期 type: list
    """
    tmp = []
    for date in dates:
        #tmp.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(date)))
        tmp.append(time.strftime("%m-%d %H:%M", time.localtime(date)))
    return tmp

def analyse_metric_data(data):
    ins = {}
    for DataPoints in data.get("DataPoints"):
        for Dimensions in DataPoints.get("Dimensions"):
            if "InstanceId" in Dimensions.get("Name"):
                InstanceId = Dimensions.get("Value")
            Timestamps = DataPoints.get("Timestamps")
            Values = DataPoints.get("Values")
            ins[InstanceId] = {
                "Timestamps":Timestamps,
                "Values":Values
                }
    return ins



def draw_pic(data,InstanceidName,picPrefix,title):
    """
    :param data: 拉取的腾讯云监控指标原始数据
    :type data: json str
    :param InstanceidName: instanceid备注的名称
    :type InstanceidName: dict
    :param profix: 图片文件前缀
    :type profix: str
    :param title : 资源标题
    :type title: str
    """
    InstanceId = ""
    maxInstanceId = {}
    nowInstanceId = {}
    topMaxInstanceId = []
    topNowInstanceId = []
    pltxticks = []
    lableNum = 0
    over80 = ""

    data = json.loads(data,encoding='utf-8')
    sort_data = analyse_metric_data(data)
    if not os.path.exists("html/pic"):
        os.makedirs("html/pic")

    fig = plt.figure(dpi=128, figsize=(7,5))
    #title = title + data.get("MetricName")
    plt.title(title)
    #ylable = data.get("MetricName") + "(%)"
    ylable = title
    plt.ylabel(ylable)
    #plt.xlabel("date")    
    picPath = "./html/pic/" + picPrefix + data.get("MetricName")  + titletime + '.png'
    print("drawing ",picPath)

    for i in sort_data.keys():
        value = sort_data.get(i).get("Values")
        try:
            maxInstanceId[i] = max(value)
            nowInstanceId[i] = value[-1]
        except ValueError:
            maxInstanceId[i] = 0           
            nowInstanceId[i] = 0
            
    topMaxInstanceId = dict(sorted(maxInstanceId.items(), key=lambda e: e[1],reverse=True)[-15:])
    topNowInstanceId = dict(sorted(nowInstanceId.items(), key=lambda e: e[1],reverse=True))

    for nowInstanceId in topNowInstanceId.keys():
        lableNum += 1
        date = timestamps_convert_date(sort_data.get(nowInstanceId).get("Timestamps"))
        value = sort_data.get(nowInstanceId).get("Values")
        try:
            if value[-1] > 80:
                over80 = nowInstanceId + " " + InstanceidName.get(nowInstanceId) + title + " 当前: " + str(value[-1])
                alertInfo.append(over80)
        except IndexError:
            print(nowInstanceId," - ",InstanceidName.get(nowInstanceId)," 没有数据" )
        if lableNum < 16:
            InstanceId = InstanceidName.get(nowInstanceId) + " - " + str(math.ceil(max(value)))  + " - " + str(math.ceil(value[-1]))
            #print(InstanceidName.get(nowInstanceId)," : ",date[-1]," : ",value[-1])
            plt.plot(date, value, label = InstanceId)
        else:
            plt.plot(date, value)
        if len(pltxticks) < len(date):
            pltxticks = date        

    
    tmp = []
    tmp = pltxticks[::24]
    tmp.append(pltxticks[-1])
    plt.xticks(tmp)

    #plt.xticks(pltxticks[::288])
    #plt.xticks(rotation=270)
    fig.autofmt_xdate()
    plt.legend(loc='upper left', bbox_to_anchor=(1.00, 1))
    fig.subplots_adjust(right=0.70,left=0.070)
    fig.set_size_inches(10, 6)
    fig.savefig(picPath,bbox_inches='tight',pad_inches=0.0)
    picName.append(picPath.replace("/html",""))   
    #plt.show()

if __name__ == '__main__':
    InstanceidName = {}
    Instanceid = [] 
    cvmMetrics = ["CPUUsage","MemUsage"]
    cdbMetrics = ["CpuUseRate","MemoryUseRate","SlowQueries","SelectCount","Qps","Tps"]
    cvmNum = 0
    cdbNum = 0
    cvmTitle = {
        "CPUUsage":"cvm-CPUUsage(%)",
        "MemUsage":"cvm-MemUsage(%)",
        "DiskUsage":"cvm-DiskUsage(%)",
        }
    cdbTitle = {
        "CpuUseRate":"cdb-CpuUseRate(%)",
        "MemoryUseRate":"cdb-MemoryUseRate(%)",
        "SlowQueries":"cdb-SlowQueries(个/3600s)慢查询数",
        "SelectCount":"cdb-SelectCount(次/3600s)查询数",
        "Qps":"cdb-Qps(执行操作数QPS/3600s)访问量占比",
        "Tps":"cdb-Tps(个/3600s)执行事务数",
        }


    cvmNum,cvm_Instanceid = get_cvm_instanceid() 
    cdbNum,cdb_Instanceid = get_cdb_instanceid() 
    #redis_Instanceid = get_redis_instanceid()
    


    for metric in cvmMetrics:
        cvmData = get_monitor_date(instances=cvm_Instanceid,namespace="QCE/CVM",metric=metric,stime=stime,etime=etime)
        #draw_pic(cvmData,cvm_Instanceid,"cvm-",cvmTitle.get(metric))
        create_js(title=cvmTitle.get(metric),metric=metric,instanceid_name=cvm_Instanceid,data=cvmData)

    cvm_Storage = get_monitor_date(instances=cvm_Instanceid,namespace="QCE/BLOCK_STORAGE",metric="DiskUsage",stime=stime,etime=etime)
    create_js(title="cvm-DiskUsage(%)",metric="cvm-DiskUsage",instanceid_name=cvm_Instanceid,data=cvm_Storage)
    #draw_pic(cvm_Storage,cvm_Instanceid,"cvm-","cvm-DiskUsage(%)")

    for metric in cdbMetrics:
        cdbData = get_monitor_date(instances=cdb_Instanceid,namespace="QCE/CDB",metric=metric,stime=stime,etime=etime)
        create_js(title=cdbTitle.get(metric),metric=metric,instanceid_name=cdb_Instanceid,data=cdbData)
        #draw_pic(cdbData,cdb_Instanceid,"cdb-",cdbTitle.get(metric))
    crete_html()



