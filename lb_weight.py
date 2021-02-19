#!/usr/bin/python
# -*- coding: utf-8 -*-
#argv[1]:LoadBalancerId
#argv[2]:ListenerId
#argv[3]:Targets.0.InstanceId
#argv[4]:Targets.0.Port
#argv[5]:Weight
import sys
import base64
import hashlib
import hmac
import random
import time
import os
import requests
import socket 


# get tencentcloud InstanceId
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.cvm.v20170312 import cvm_client, models
def get_InstanceId(ip, secretId, secret_key):
    try: 
        cred = credential.Credential(secretId, secret_key) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, "ap-guangzhou", clientProfile)
        req = models.DescribeInstancesRequest()
        params = '{"Filters":[{"Name":"private-ip-address","Values":["' + ip + '"]}]}'
        req.from_json_string(params)
        resp = client.DescribeInstances(req) 
        data = resp.to_json_string()
        return data.replace('"',"").split("InstanceId: ")[1].split(",")[0]   # InstanceId
    except TencentCloudSDKException as err: 
        print(err)

def get_string_to_sign(method, endpoint):
    s = method + endpoint + "/?"
    query_str = "&".join("%s=%s" % (k, data[k]) for k in sorted(data))
    return s + query_str


def sign_str(key, s, method):
    hmac_str = hmac.new(key.encode("utf8"), s.encode("utf8"), method).digest()
    return base64.b64encode(hmac_str)


if __name__ == '__main__':
    endpoint = "clb.tencentcloudapi.com"
    secretId = 'xxxxx'
    secret_key = 'xxxxx'
    ip = socket.gethostbyname(socket.gethostname())
    LoadBalancerId = "xxx"
    ListenerId = ""
    InstanceId = get_InstanceId(ip, secretId, secret_key)
    Port = "80"
    Weight = 20
    data = {
        'Action': 'ModifyTargetWeight',
        'SecretId': secretId,
        'Region': 'ap-guangzhou',
        'Timestamp': int(time.time()),
        'Nonce': random.randint(0, 1000000),
        'Version': '2018-03-17',
        'LoadBalancerId': LoadBalancerId,
        'ListenerId': ListenerId,
        'Targets.0.InstanceId': InstanceId,
        'Targets.0.Port': Port,
        'Weight': Weight
    }

    s = get_string_to_sign("GET", endpoint)
    data["Signature"] = sign_str(secret_key, s, hashlib.sha1)
    print(data["Signature"])
    resp = requests.get("https://" + endpoint, params=data)
    print(resp.text)
    os.system("sleep 2")
