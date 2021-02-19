from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.cdb.v20170320 import cdb_client, models 
try: 
    cred = credential.Credential("xxxxx", "xxxxx") 
    httpProfile = HttpProfile()
    httpProfile.endpoint = "cdb.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = cdb_client.CdbClient(cred, "ap-guangzhou", clientProfile) 

    req = models.ModifyRoGroupInfoRequest()
    params = '{\"RoGroupId\":\"cdbrg-m8sw499j\",\"RoGroupInfo\":{\"WeightMode\":\"custom\"},\"RoWeightValues\":[{\"InstanceId\":\"cdbro-m8sw499j\",\"Weight\":4}]}'
    req.from_json_string(params)

    resp = client.ModifyRoGroupInfo(req) 
    print(resp.to_json_string()) 

except TencentCloudSDKException as err: 
    print(err)