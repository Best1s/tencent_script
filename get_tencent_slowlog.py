from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.cdb.v20170320 import cdb_client, models
from multiprocessing import Process
import json
import time

def get_mysql_instance(SecretId, SecretKey, tp):
    try: 
        cred = credential.Credential(SecretId, SecretKey) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cdb.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cdb_client.CdbClient(cred, "ap-guangzhou", clientProfile) 

        req = models.DescribeDBInstancesRequest()
        if tp:
            #params = '{\"InstanceTypes\":[1]}'
            params = '{\"OrderBy\":\"instanceId\"}'
        else:
            params = '{}'
        req.from_json_string(params)

        resp = client.DescribeDBInstances(req) 
        js = json.loads(resp.to_json_string())
        mysql_Instance = {}
        if js["Items"] != None:
                for data in js["Items"]:
                    if "rc" not in data["InstanceName"]:
                        mysql_Instance[data["InstanceId"]] = data["InstanceName"]
                return mysql_Instance  # parm: dict

    except TencentCloudSDKException as err: 
        print(err)

def get_mysql_slowlog(SecretId, SecretKey, InstanceId, InstanceIdName, stime, etime, process_sleep):
    time.sleep(process_sleep)
    try: 
        cred = credential.Credential(SecretId, SecretKey) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cdb.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cdb_client.CdbClient(cred, "ap-guangzhou", clientProfile) 

        req = models.DescribeSlowLogDataRequest()
        params = '{\"InstanceId\":\"' + InstanceId + '\",\"StartTime\":' + str(stime) + ',\"EndTime\":' + str(etime) + ',\"Limit\":400}'
        req.from_json_string(params)
        resp = client.DescribeSlowLogData(req)
        js = json.loads(resp.to_json_string())
        if  js["Items"] != None:
            for data in js["Items"]:
                data["InstanceName"] = InstanceIdName
                data['SqlText'] = data['SqlText'].replace('\n', '').replace('  ', '').replace("'","")
                print(data)
            return 0
        else:
            return 0
    except TencentCloudSDKException as err: 
        print(err)
if __name__ == '__main__':
    SecretId = 'xxxxxx'
    SecretKey = 'xxxxxxx'
    now_time = int(time.time()) - 10
    stime = now_time - 10
    etime = now_time
    mysqlInstanceIds = get_mysql_instance(SecretId, SecretKey, tp="1")
    mysqlInstanceIds.update(get_mysql_instance(SecretId, SecretKey, tp=""))
#    print(mysqlInstanceIds)
    if mysqlInstanceIds:
        while True:                      
            #print("stime:",stime,"etime",etime,"notime:", int(time.time()) - 10)
            process_sleep = 0
            for InstanceId,InstanceIdName in mysqlInstanceIds.items():
                #time.sleep(0.5)                
                #get_mysql_slowlog(SecretId, SecretKey, InstanceId, InstanceIdName, stime, etime, process_sleep)
                process = Process(target=get_mysql_slowlog,args=(SecretId, SecretKey, InstanceId, InstanceIdName, stime, etime, process_sleep))
                process.start()
                process_sleep += 0.2
            now_time = int(time.time()) - 10
            ctime = now_time - etime
            stime = etime + 1
            if ctime > 1:
                etime = now_time
            else:
                etime = etime +9
            time.sleep(10)