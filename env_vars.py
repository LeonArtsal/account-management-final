import os

postgres_endpoint = os.environ['DP_ACCTMGMT_POSTGRES_URL']
bucket_name = os.environ['DP_ACCTMGMT_S3_BUCKET']
bucket_file_name =  os.environ['DP_ACCTMGMT_EXPORTED_FILENAME']
aws_access_key_id = os.environ['DP_ACCTMGMT_AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['DP_ACCTMGMT_AWS_SECRET_ACCESS_KEY']
aws_region = os.environ['DP_ACCTMGMT_AWS_REGION']

# optional
aws_role_arn = os.environ['DP_ACCTMGMT_AWS_ROLE_ARN'] if 'DP_ACCTMGMT_AWS_ROLE_ARN' in os.environ else None
aws_profile_local = os.environ['DP_ACCTMGMT_AWS_PROFILE_LOCAL'] if 'DP_ACCTMGMT_AWS_PROFILE_LOCAL' in os.environ else None