# -*- coding: utf-8 -*-
# monitor https://console.cloud.tencent.com/api/explorer?Product=monitor&Version=2018-07-24&Action=GetMonitorData&SignVersion=
# cdb https://console.cloud.tencent.com/api/explorer?Product=cdb&Version=2017-03-20&Action=DescribeRoGroups&SignVersion=

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.monitor.v20180724 import monitor_client, models as monitor_models  # monitor
from tencentcloud.cdb.v20170320 import cdb_client, models  # cbd
import time
import json
import sys

def get_tencent_mysql_cpu(SecretId, SecretKey, params, nums):
    try: 
        cred = credential.Credential(SecretId, SecretKey) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "monitor.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = monitor_client.MonitorClient(cred, "ap-guangzhou", clientProfile)
        req = monitor_models.GetMonitorDataRequest()
        req.from_json_string(params)
        resp = client.GetMonitorData(req)        
        js = json.loads(resp.to_json_string())
        cpus = []
        try:
            for i in range(nums):
                print(js["DataPoints"][i]["Values"][0])
                cpus.append(js["DataPoints"][i]["Values"][0])
            print(max(cpus))
        except IndexError:
            print("GET MYSQL CPU ERROR: IndexERROR")
            exit(1)
    except TencentCloudSDKException as err: 
        print("get monitor ERROR:",err)
        exit(1)

def get_tencent_mysql_slavelist(SecretId, SecretKey, InstanceId):
    try: 
        cred = credential.Credential(SecretId, SecretKey) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cdb.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cdb_client.CdbClient(cred, "ap-guangzhou", clientProfile)
        req = models.DescribeRoGroupsRequest()
        params = '{"InstanceId":"' + InstanceId + '"}'
        req.from_json_string(params)
        resp = client.DescribeRoGroups(req) 
        js = json.loads(resp.to_json_string())
        mysql_slaves = []
        try:
            nums = len(js["RoGroups"][0]["RoInstances"])
            for i in range(nums):
                mysql_slaves.append((js["RoGroups"][0]["RoInstances"][i]["InstanceId"]))
            return mysql_slaves
        except IndexError:
            print("ERROR: plase check InstanceId is master!")
            exit(1)
    except TencentCloudSDKException as err: 
        print("get slavelist ERROR:", err)
        exit(1)

if __name__ == '__main__':
    #print(time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(time.time())))
    timestamp = time.time() - 10
    timeArray = time.localtime(timestamp)
    date=time.strftime("%Y-%m-%dT%H:%M:%S+08:00", timeArray)
    SecretId = 'xxxxx'
    SecretKey = 'xxxxx'
    InstanceId = sys.argv[1] 
    mysql_slaveIDs = get_tencent_mysql_slavelist(SecretId, SecretKey, InstanceId)
    Instances = []
    Instances.append(['{"Dimensions":[{"Name":"InstanceId","Value":"' + slaveID + '"}]}'for slaveID in mysql_slaveIDs])
    Instances=",".join(Instances[0])
    params='{"Namespace":"QCE/CDB","MetricName":"CPUUseRate","Period":5,"StartTime":"' + date + '","StartTime":"' + date + '","Instances":[' + str(Instances) + ']}'  
    get_tencent_mysql_cpu(SecretId, SecretKey, params, len(mysql_slaveIDs)) 
    



