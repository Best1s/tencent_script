# -*- coding: utf-8 -*-
# api https://console.cloud.tencent.com/api/explorer?Product=cvm&Version=2017-03-12&Action=DescribeInstances&SignVersion=
# docment https://cloud.tencent.com/document/product/213/15728
# monitor document https://cloud.tencent.com/document/product/248/6843
import json
import math
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models as cvm_models
from tencentcloud.cdb.v20170320 import cdb_client, models as cdb_models
from tencentcloud.redis.v20180412 import redis_client, models as redis_models
from tencentcloud.monitor.v20180724 import monitor_client, models as monitor_models

cred = credential.Credential("xxxxx", "xxxxx") 
httpProfile = HttpProfile()
clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile

def analyse_data(data, excludestr="rc"):
    tmp = {}
    for instance in data:
        if excludestr not in instance["InstanceName"].lower():   
            tmp[instance["InstanceId"]] = instance["InstanceName"]      
    return tmp

def get_cvm_instanceid():
    ins = {}
    cvmNum=0
    try:
        httpProfile.endpoint = "cvm.tencentcloudapi.com"
        client = cvm_client.CvmClient(cred, "ap-guangzhou", clientProfile)
        req = cvm_models.DescribeInstancesRequest()
        params = {
            "Offset": 0,
            "Limit": 1
        }
        req.from_json_string(json.dumps(params))
        resp = client.DescribeInstances(req)
        data = json.loads(resp.to_json_string())
        totalCount = data["TotalCount"]
        for i in range(math.ceil(totalCount/100)):
            params = {
            "Offset": i * 100,
            "Limit": 100            
            }
            req.from_json_string(json.dumps(params))
            resp = client.DescribeInstances(req)
            data = json.loads(resp.to_json_string()).get("InstanceSet")
            cvmNum += len(data)
            ins = dict(analyse_data(data),**ins)
        print("cvmNum is: ",cvmNum)
        print("not rc cvmNum is:",len(ins.keys()))
        return cvmNum, ins
    except TencentCloudSDKException as err: 
        print(err)

def get_cdb_instanceid():
    ins = {}
    global num
    num=0
    try:
        httpProfile.endpoint = "cdb.tencentcloudapi.com"
        client = cdb_client.CdbClient(cred, "ap-guangzhou", clientProfile)
        req = cdb_models.DescribeDBInstancesRequest()
        params = {
            "Limit": 200
        }
        req.from_json_string(json.dumps(params))

        resp = client.DescribeDBInstances(req) 
        data = json.loads(resp.to_json_string())
        totalCount = data.get("TotalCount")
        ins = analyse_data(data.get("Items"))
        print("cdbNum is: ",totalCount)
        print("not rc cdbNum is:",len(ins.keys()))
        return totalCount,ins
    except TencentCloudSDKException as err: 
        print(err)

def get_redis_instanceid():    #not authorized to perform operation (redis:DescribeInstances)
    ins = {}
    try:
        httpProfile.endpoint = "redis.tencentcloudapi.com"
        client = redis_client.RedisClient(cred, "ap-guangzhou", clientProfile)
        req = redis_models.DescribeInstancesRequest()
        params = {
            "Limit": 2000
        }
        req.from_json_string(json.dumps(params))
        resp = client.DescribeInstances(req) 
        data = json.loads(resp.to_json_string())
        return data
    except TencentCloudSDKException as err: 
        print(err) 

def send_message(msg):
    try: 
        httpProfile.endpoint = "monitor.tencentcloudapi.com"
        client = monitor_client.MonitorClient(cred, "ap-guangzhou", clientProfile)
        req = monitor_models.SendCustomAlarmMsgRequest()
        params = {
            "Module": "monitor",
            "PolicyId": "cm-qt41xhob",
            "Msg": msg
        }
        req.from_json_string(json.dumps(params))
        resp = client.SendCustomAlarmMsg(req) 
        print(resp.to_json_string())
    except TencentCloudSDKException as err: 
        print(err)

def get_monitor_date(namespace,metric,stime,etime,instances):
    """
    :param instances: 实例 instances
    :type instances: list
    :param namespace: 资源
    :type namespace: str
    :param metric: 监控指标
    :type metric: str
    :param stime,etime: 开始时间,结束时间
    :type stime,etime: ios time str eg: "2020-11-10 00:00:00"
    """
    try: 
        httpProfile.endpoint = "monitor.tencentcloudapi.com"
        client = monitor_client.MonitorClient(cred, "ap-guangzhou", clientProfile)
        req = monitor_models.GetMonitorDataRequest()
        insdata = []

        for i in instances.keys():
            tmp = {
                "Dimensions":
                    [
                        {
                            "Name": "InstanceId",
                            "Value": i
                        }
                    ]
                }
            insdata.append(tmp)

        params = {
        "Instances": insdata,
        "Namespace": namespace,
        "MetricName": metric,
        "Period": 3600,
        #"Period": 300,
        "StartTime": stime,
        "EndTime": etime,
        }
        req.from_json_string(json.dumps(params))

        resp = client.GetMonitorData(req) 
        #print(resp.to_json_string()) 
        return(resp.to_json_string()) 

    except TencentCloudSDKException as err: 
        print(err)
        return 0


if __name__ == '__main__':
    date = get_cvm_instanceid()
    if date:
        print(date)

        