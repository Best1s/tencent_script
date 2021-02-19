#pip3 install tencentcloud-sdk-python -i https://pypi.doubanio.com/simple
# argv[1] : LoadBalancerId      use: python3.6 getLBclient_ip.py LoadBalancerId

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.clb.v20180317 import clb_client, models
import sys

def get_lb_client_ip(SecretId, SecretKey, LoadBalancerId):
    try:
        cred = credential.Credential(SecretId, SecretKey) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "clb.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = clb_client.ClbClient(cred, "ap-guangzhou", clientProfile) 
        req = models.DescribeClassicalLBTargetsRequest()
        params = '{"LoadBalancerId":"' + LoadBalancerId + '"}'
        req.from_json_string(params)
        resp = client.DescribeClassicalLBTargets(req) 
        return resp.to_json_string()
    except TencentCloudSDKException as err: 
        print("ERROR:",err)
        exit(126)

if __name__ == '__main__':
    SecretId = 'xxxxx'
    SecretKey = 'xxxxx'
    LoadBalancerId = sys.argv[1]    
    date = get_lb_client_ip(SecretId, SecretKey, LoadBalancerId)
    ip = ""
    if date:
        for i in date.split('PrivateIpAddresses": ["'):
            ip = i.split('"')[0] + " " + ip
    if ip[:-3]:
        print(ip[:-3])
