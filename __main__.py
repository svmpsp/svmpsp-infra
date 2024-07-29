"""A DigitalOcean Python Pulumi program"""
from pathlib import Path

import pulumi
import pulumi_digitalocean as do

svmpspHostingDropletCloudInit = Path("assets/droplet-cloud-init.yaml").read_text()

# Compute configuration
svmpspHostingDroplet = do.Droplet(
  "svmpsp-dev-hosting",
  image="ubuntu-24-04-x64",
  name="svmpsp-dev-hosting",
  region=do.Region.FRA1,
  size="s-1vcpu-512mb-10gb",
  ssh_keys=["cc:da:89:ec:c9:68:48:e0:f9:7b:9d:f3:d6:5a:08:36"],
  user_data=svmpspHostingDropletCloudInit,
)

# DNS configuration
svmpspDomain = do.Domain(
  "svmpsp-dev-domain",
  name="svmpsp.dev"
)

mainDnsRecord = do.DnsRecord(
    "@",
    domain=svmpspDomain.id,
    type=do.RecordType.A,
    name="@",
    value=svmpspHostingDroplet.ipv4_address)

wwwDnsRecord = do.DnsRecord(
    "www",
    domain=svmpspDomain.id,
    type=do.RecordType.A,
    name="www",
    value=svmpspHostingDroplet.ipv4_address)


# Export the name of the domain
pulumi.export("domain_name", svmpspDomain.name)
pulumi.export("droplet_ipv4", svmpspHostingDroplet.ipv4_address)