from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.cdb.v20170320 import cdb_client, models
import json
def get_mysql_instance(SecretId, SecretKey):
    try: 
        cred = credential.Credential(SecretId, SecretKey) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cdb.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cdb_client.CdbClient(cred, "ap-guangzhou", clientProfile) 

        req = models.DescribeDBInstancesRequest()
        params = '{}'
        req.from_json_string(params)

        resp = client.DescribeDBInstances(req) 
        js = json.loads(resp.to_json_string())
        mysql_Instance = {}
        if  js["Items"] != None:
                for data in js["Items"]:
                    if "rc" not in data["InstanceName"]:
                        mysql_Instance[data["InstanceId"]] = data["InstanceName"]
                        print(data["InstanceId"],"\t",data["InstanceName"])
                return mysql_Instance

    except TencentCloudSDKException as err: 
        print(err) 