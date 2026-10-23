A=host.artifacts(frame_id='a35831fe-107a-4961-bc9f-e6fd6d255601',limit=500)
print(A['count'], A.get('truncated'))
ART=pd.DataFrame(A['artifacts'])[['id','filename','latest_version_id','content_type','is_user_upload']]
print(ART.to_string())