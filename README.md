
# terraform-module-registry-github

This is a simple Terraform module Registry written in Python that implements the [Terraform Module Registry Protocol](https://developer.hashicorp.com/terraform/internals/module-registry-protocol)
and the [Remote Service Discovery](https://developer.hashicorp.com/terraform/internals/remote-service-discovery) 
functionality.

It can be used to provide a lightweight self-hosted Terraform module Registry able to resolve Terraform modules hosted 
on GitHub by proxying the requests made by Terraform clients.

## How to run it
First you need to generate the certificates to serve traffic over HTTPS by running
```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -addext "subjectAltName = DNS:your.domain.com" 
```
Since running is performed via Docker, build the image first by running
```
docker build -t terraform-module-registry-github:latest .
```
Then you can 
```
docker run -p 443:443 -e GITHUB_TOKEN=<YOUR GITHUB TOKEN> terraform-module-registry-github:latest <your yaml config file>
```

## How to configure it
An example of configuration can be found in [sample-config.yml](examples/sample-config.yml) and its usage in a Terraform
project can be found in [sample-usage.tf](examples/sample-usage.tf).

## Why is it served over HTTPS instead of HTTP?
The Terraform client automatically makes HTTPS requests, so HTTP would not work.