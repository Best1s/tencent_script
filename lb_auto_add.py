#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
# get tencentcloud InstanceId
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.cvm.v20170312 import cvm_client, models as cvmmodels
from tencentcloud.clb.v20180317 import clb_client, models 

def get_InstanceId(ip, secretId, secret_key):
    try: 
        cred = credential.Credential(secretId, secret_key) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cvm.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cvm_client.CvmClient(cred, "ap-guangzhou", clientProfile)
        req = cvmmodels.DescribeInstancesRequest()
        params = '{"Filters":[{"Name":"private-ip-address","Values":["' + ip + '"]}]}'
        req.from_json_string(params)
        resp = client.DescribeInstances(req) 
        data = resp.to_json_string()
        return data.replace('"',"").split("InstanceId: ")[1].split(",")[0]   # InstanceId
    except TencentCloudSDKException as err: 
        print(err)

def register_lb(LoadBalancerId,InstanceId, Weight, secretId, secret_key):
    try: 
        cred = credential.Credential(secretId, secret_key) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "clb.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = clb_client.ClbClient(cred, "ap-guangzhou", clientProfile)
        req = models.RegisterTargetsWithClassicalLBRequest()
        params = '{"LoadBalancerId":"' + LoadBalancerId + '","Targets":[{"InstanceId":"' + InstanceId + '","Weight":' + Weight + '}]}'
        req.from_json_string(params)
        resp = client.RegisterTargetsWithClassicalLB(req) 
        print(resp.to_json_string() + "\n ????????LB?ɹ???")
    except TencentCloudSDKException as err: 
        print(err)

def get_host_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    secretId = 'xxxxx'
    secret_key = 'xxxxx'
    ip = get_host_ip()
    LoadBalancerId = "lb-xxxx"
    InstanceId = get_InstanceId(ip, secretId, secret_key)
    Weight = "20"
    register_lb(LoadBalancerId, InstanceId, Weight,secretId, secret_key)    