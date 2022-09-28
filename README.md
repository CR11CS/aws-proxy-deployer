## AWS Proxy Deployer

 - Quickly deploy or destroy an AWS EC2 instance proxy server from the
   command line with your specified security group in CIDR notation in
   your specified region.
   
  - Proxy server is accessible only to your specified security group and
   is usable without any further configuration. 
   
  - Default proxy server settings are to operate without an HTTP 'via'
   header to act as a transparent proxy but configurations can be
   modified in the `tinyproxy-install.sh` script.


Requires **AWS_ACCESS_KEY_ID** and **AWS_SECRET_ACCESS_KEY** environment variables present or simply place your AWS rootkeys.csv file in the same directory as the script.

**usage:** `aws-proxy-deployer action [flag] <"value">`

    ACTIONS:
        [deploy,        Deploy proxy using standard defaults..............................]
        [destroy,       Destroy active proxy resources from AWS...........................]

    FLAGS:
        [-r, --region   Specify AWS region to deploy proxy in.............................]
        [-p, --permit   Permit additional user via comma-separated IPv4 CIDR notation.....]

    REGIONS:
        'us-east-2':'US East (Ohio)'                   |   'ap-northeast-1':'Asia Pacific (Tokyo)'
        'us-east-1':'US East (N. Virginia)'            |   'ca-central-1':'Canada (Central)'
        'us-west-1':'US West (N. California)'          |   'eu-central-1':'Europe (Frankfurt)'
        'us-west-2':'US West (Oregon)'                 |   'eu-west-1':'Europe (Ireland)'
        'ap-south-1':'Asia Pacific (Mumbai)'           |   'eu-west-2':'Europe (London)'
        'ap-northeast-3':'Asia Pacific (Osaka)'        |   'eu-west-3':'Europe (Paris)'
        'ap-northeast-2':'Asia Pacific (Seoul)'        |   'eu-north-1':'Europe (Stockholm)'
        'ap-southeast-1':'Asia Pacific (Singapore)'    |   'sa-east-1':'South America (Sao Paulo)'
        'ap-southeast-2':'Asia Pacific (Sydney)'       |

