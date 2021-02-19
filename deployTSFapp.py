# document https://cloud.tencent.com/document/product/649/36071
# pip install tencentcloud-sdk-python
# parame:
# avg[1] : Groupid
# avg[2] : Server docker images address  eg: ccr.ccs.tencentyun.com/tsf_3137077628/rc_provider
# avg[3] : TagName eg: 0628-18.24.06-rc-1d84c2e7
# avg[3] : InstanceNum  pod num

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.tsf.v20180326 import tsf_client, models
import sys
import json

def deployment_images(secretId, secret_key, params):
    try: 
        cred = credential.Credential(secretId, secret_key) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tsf.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tsf_client.TsfClient(cred, "ap-guangzhou", clientProfile) 

        req = models.DeployContainerGroupRequest()        
        req.from_json_string(params)

        resp = client.DeployContainerGroup(req)
        js = json.loads(resp.to_json_string())
        if js["Result"] == True:
            print("INFO: deployment tencent SUCCESSFUL!!!")
            return 0         

    except TencentCloudSDKException as err: 
        print("ERROR��deployment tencent fault!!!",err)
        sys.exit(1)

if __name__ == '__main__':
    secretId = 'xxxxx'
    secret_key = 'xxxxx'
    GroupId = sys.argv[1]
    Server = sys.argv[2]
    TagName = sys.argv[3]
    InstanceNum = sys.argv[4]
    params = {
        "GroupId" : GroupId,
        "Server" : Server.split("/")[0],
        "Reponame" : Server.split("com/")[1],
        "TagName" : TagName,
        "InstanceNum" : InstanceNum,
        "CpuRequest" : "0.5",
        "MemRequest" : "1024",
        "CpuLimit" : "8",
        "MemLimit" : "8192",
        "UpdateType" : "1",
        "UpdateIvl" : "60",
        "JvmOpts" : "-Xmx5440M -Xms5440M -XX:MaxMetaspaceSize=512M -XX:MetaspaceSize=512M -XX:+UseG1GC -XX:MaxGCPauseMillis=100 -XX:+ParallelRefProcEnabled -XX:AutoBoxCacheMax=20000",
        "AgentCpuLimit" : "2",
        "AgentMemLimit" : "2048",
        }
    params = json.dumps(params)
    deployment_images(secretId, secret_key, params)