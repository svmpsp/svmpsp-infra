"""A DigitalOcean Python Pulumi program"""
from pathlib import Path

import pulumi
import pulumi_digitalocean as do


svmpsp_hosting_cloud_init = Path("assets/droplet-cloud-init.yaml").read_text()

# Compute configuration
svmpsp_hosting_droplet = do.Droplet(
  "svmpsp-dev-hosting",
  image="ubuntu-24-04-x64",
  name="svmpsp-dev-hosting",
  region=do.Region.FRA1,
  size="s-1vcpu-512mb-10gb",
  ssh_keys=["cc:da:89:ec:c9:68:48:e0:f9:7b:9d:f3:d6:5a:08:36"],
  user_data=svmpsp_hosting_cloud_init,
)

# Cloud Firewall configuration
droplet_firewall = do.Firewall("web",
    name="svmpsp-dev-default-fw",
    droplet_ids=[svmpsp_hosting_droplet.id],
    inbound_rules=[
        # Allow SSH connections to droplet
        do.FirewallInboundRuleArgs(
            protocol="tcp",
            port_range="22",
            source_addresses=[
                "0.0.0.0/0",
                "::/0",
            ],
        ),
        # Allow droplet to serve HTTP
        do.FirewallInboundRuleArgs(
            protocol="tcp",
            port_range="80",
            source_addresses=[
                "0.0.0.0/0",
                "::/0",
            ],
        ),
        # Allow droplet to serve HTTPS
        do.FirewallInboundRuleArgs(
            protocol="tcp",
            port_range="443",
            source_addresses=[
                "0.0.0.0/0",
                "::/0",
            ],
        ),
        # Allow droplet to be pinged
        do.FirewallInboundRuleArgs(
            protocol="icmp",
            source_addresses=[
                "0.0.0.0/0",
                "::/0",
            ],
        ),
    ],
    outbound_rules=[
        # Allow droplet to access internet
        do.FirewallOutboundRuleArgs(
            protocol="tcp",
            port_range="1-65535",
            destination_addresses=[
                "0.0.0.0/0",
                "::/0",
            ]
        ),
        # Allow droplet to ping (ICMP)
        do.FirewallOutboundRuleArgs(
            protocol="icmp",
            destination_addresses=[
                "0.0.0.0/0",
                "::/0",
            ],
        ),
    ])

# DNS configuration
svmpsp_dns_domain = do.Domain(
  "svmpsp-dev-domain",
  name="svmpsp.dev"
)

main_dns_record = do.DnsRecord(
    "@",
    domain=svmpsp_dns_domain.id,
    type=do.RecordType.A,
    name="@",
    value=svmpsp_hosting_droplet.ipv4_address)

www_dns_record = do.DnsRecord(
    "www",
    domain=svmpsp_dns_domain.id,
    type=do.RecordType.A,
    name="www",
    value=svmpsp_hosting_droplet.ipv4_address)


# Export the name of the domain
pulumi.export("domain_name", svmpsp_dns_domain.name)
pulumi.export("droplet_ipv4", svmpsp_hosting_droplet.ipv4_address)