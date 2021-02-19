# https://cloud.tencent.com/document/product/214/38304

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.clb.v20180317 import clb_client, models
try: 
    cred = credential.Credential("aaaaa", "xxxxxx") 
    httpProfile = HttpProfile()
    httpProfile.endpoint = "clb.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = clb_client.ClbClient(cred, "ap-guangzhou", clientProfile) 

    req = models.BatchDeregisterTargetsRequest()
    params = {
        "LoadBalancerId": "fffffid",
        "Targets": [
            {
                "ListenerId": "������ID",
                "InstanceId": "�ӻ�ID",
                "EniIp": "��������ip",
                "Port": 80
            }
        ]
    }
    req.from_json_string(json.dumps(params))

    resp = client.BatchDeregisterTargets(req) 
    print(resp.to_json_string()) 

except TencentCloudSDKException as err: 
    print(err) 