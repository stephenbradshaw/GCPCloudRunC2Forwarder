# GCPCloudRunC2Forwarder

This Google Cloud Run application can be used to forward traffic fronted from the Google Cloud Run domain to a C2 server running on a GCP compute instance VM.

This is a POC application only and has a few potential indicators that could be use to identify running instances, so read the code in main.py and modify as required before attempting to use.

The code here is functionally identical to the [GCP App Engine app](https://github.com/stephenbradshaw/GCPAppEngineC2Forwarder) but the Cloud Run deployment approach is a little easier to manage, so I would recommend it over the GCP App Engine approach as long as the Cloud Run frontend domain is equally suitable for you.


# Pre deployment setup and configuration

Setup a project in GCP with a VPC (the default one is fine) and at least one compute instance running a C2 server with a HTTP listener. In more complex setups you can use a multi host setup with a HTTP proxy (Apache, Nginx, etc) that filters and then forwards HTTP traffic to the C2s HTTP listener on another host to provide some seperation and protection for the C2 server. Take note of the IP address of the C2 server (or proxy server in a multi host setup), as we will need to specify this at deploy time for the application.

Cloud Run essentially builds a container based on an application you provide, and in the usual container pattern we can provide runtime parameters to the application using environment variables - we will set the destination address for the C2 server in the GCP environment using the `DESTINATION` environment variable.

We can also use [Direct VPC egress](https://cloud.google.com/run/docs/configuring/vpc-direct-vpc) to allow traffic to flow direct from the Cloud Run container by running the container within the same (or an adjacent) subnet as your destination C2 GCP compute VM. You then need to create firewall rules to allow traffic to the port on the destination host.

In my test environment, I chose to deploy the container to the same subnet as the destination compute VM (which was the default subnet in the same region), and created a [firewall rule](https://console.cloud.google.com/net-security/firewall-manager/firewall-policies/list) that allowed all internal traffic to port 80 on the destination host from all other hosts in the subnet. You can choose a more segmented approach if you wish.


# Deployment variables


The example deployment steps below will reference some of the following variables you will want to replace with your own appropriate values, taking the pre deployment steps as discussed above into consideration:
* `<SERVICE_NAME>` - the name for the cloud run service you will deploy - can be almost any arbitrary string, but will appear in the auto-generated domain so dont be too obvious about it if you want deniability
* `<REGION>` - the GCP region in which the Cloud Run app will be deployed e.g. `us-central1`
* `<C2_INTERNAL_IP>` - the internal IP address of the C2 HTTP listener you want to forward traffic to
* `<PROJECT_ID>` - ID of the GCP project in which you are deploying resources, can be obtained from various locations in the console such as the [welcome page](https://console.cloud.google.com/welcome/new)
* `<SUBNET_NAME>` - name of the subnet to which you want your Cloud Run container to be connected to, e.g. `default`


# Deployment steps


[Install and configure](https://cloud.google.com/sdk/docs/install) the GCloud CLI. 


Configure the CLI for your project

```
gcloud config set project <PROJECT_ID>
```

Enable the appropriate APIs in GCP:

```
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

Deploy the application, using this repository as the present working directory


```
gcloud run deploy <SERVICE_NAME> --source . --set-env-vars='DESTINATION=<C2_INTERNAL_IP>' --region=<REGION> --subnet='projects/<PROJECT_ID>/regions/<REGION>/subnetworks/<SUBNET_NAME>'
```

The `--subnet` switch value above refers to the internal resource name of the subnet to which you want to attach your Cloud Run container, you should confirm it is referring to the correct resource using the [GCP subnets page](https://console.cloud.google.com/networking/networks/list?pageTab=CURRENT_PROJECT_SUBNETS) if you have any issues.


Once complete this will spit out a URL at which your C2 service can be reached, with a form similar to the following: `https://<SERVICE_NAME>-<12_DIGIT_NUMBER>.<REGION>.run.app`


You can monitor/troubleshoot/delete the application after this point using the [GCP Cloud Run console](https://console.cloud.google.com/run)
