import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Tuple

import pulumi_aws as aws
from infra import policies
from infra.bucket import Bucket
from infra.config import DEPLOYMENT_NAME, DGRAPH_LOG_RETENTION_DAYS

import pulumi
from pulumi.output import Output
from pulumi.resource import ResourceOptions

# These are COPYd in from Dockerfile.pulumi
SWARM_INIT_DIR = Path("../src/js/grapl-cdk/swarm").resolve()


@dataclass
class Ec2Port:
    protocol: str
    port: int

    def to_network_io_args(
        self,
    ) -> Tuple[aws.ec2.SecurityGroupIngressArgs, aws.ec2.SecurityGroupEgressArgs]:
        ingress = aws.ec2.SecurityGroupIngressArgs(
            from_port=self.port,
            to_port=self.port,
            protocol=self.protocol,
            self=True,
        )
        egress = aws.ec2.SecurityGroupEgressArgs(
            from_port=self.port,
            to_port=self.port,
            protocol=self.protocol,
            self=True,
        )
        return (ingress, egress)


class Swarm(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        vpc: aws.ec2.Vpc,
        internal_service_ports: Sequence[Ec2Port],
        log_group: aws.cloudwatch.LogGroup,
        opts: Optional[pulumi.ResourceOptions] = None,
    ) -> None:
        super().__init__("grapl:SwarmResource", name=name, props=None, opts=opts)

        child_opts = pulumi.ResourceOptions(parent=self)

        # allow hosts in the swarm security group to communicate
        # internally on the following ports:
        #   TCP 2376 -- secure docker client
        #   TCP 2377 -- inter-node communication (only needed on manager nodes)
        #   TCP + UDP 7946 -- container network discovery
        #   UDP 4789 -- overlay network traffic
        internal_rules = [
            port.to_network_io_args()
            for port in (
                Ec2Port("tcp", 2376),
                Ec2Port("tcp", 2377),
                Ec2Port("tcp", 7946),
                Ec2Port("udp", 7946),
                Ec2Port("udp", 4789),
                *internal_service_ports,
            )
        ]

        ingress_rules = [ingress for ingress, _ in internal_rules]

        # allow hosts in the swarm security group to make outbound
        # connections to the Internet for these services:
        #   TCP 443 -- AWS SSM Agent (for handshake)
        #   TCP 80 -- yum package manager and wget (install Docker)
        egress_rules = [
            aws.ec2.SecurityGroupEgressArgs(
                from_port=443,
                to_port=443,
                protocol="tcp",
                self=True,
            ),
            aws.ec2.SecurityGroupEgressArgs(
                from_port=80,
                to_port=80,
                protocol="tcp",
                self=True,
            ),
        ] + [egress for _, egress in internal_rules]

        self.security_group = aws.ec2.SecurityGroup(
            "SwarmSecurityGroup",
            opts=child_opts,
            description=f"Docker Swarm security group",
            ingress=ingress_rules,
            egress=egress_rules,
            vpc_id=vpc.id,
            name=f"{DEPLOYMENT_NAME}-grapl-swarm",
        )

        self.role = aws.iam.Role(
            f"{DEPLOYMENT_NAME}-grapl-swarm-role",
            description="IAM role for Swarm instances",
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "ec2.amazonaws.com",
                            },
                        }
                    ],
                }
            ),
            opts=child_opts,
        )

        # CloudWatchAgentServerPolicy allows the Swarm instances to
        # run the CloudWatch Agent.
        policies.attach_policy(
            role=self.role, policy=policies.CLOUDWATCH_AGENT_SERVER_POLICY
        )
        policies.attach_policy(role=self.role, policy=policies.SSM_POLICY)
        policies._attach_policy_to_ship_logs_to_cloudwatch(
            role=self.role, log_group=log_group, opts=child_opts
        )

        self.swarm_hosted_zone = aws.route53.Zone(
            "SwarmZone",
            name=f"{DEPLOYMENT_NAME}.dgraph.grapl",
            vpcs=[
                aws.route53.ZoneVpcArgs(
                    vpc_id=vpc.id,
                )
            ],
            opts=child_opts,
        )

        self.swarm_config_bucket = Bucket(
            logical_bucket_name="swarm-config-bucket",
            opts=child_opts,
        )
        self.swarm_config_bucket.grant_read_permissions_to(self.role)
        self.swarm_config_bucket.upload_to_bucket(SWARM_INIT_DIR)

        # InstanceProfile for swarm instances
        aws.iam.InstanceProfile(
            "SwarmInstanceProfile",
            opts=child_opts,
            role=self.role.name,
            name=f"{DEPLOYMENT_NAME}-swarm-instance-profile",
        )

    def cluster_host_port(self) -> pulumi.Output[str]:
        return Output.concat(self.swarm_hosted_zone.name, ":9080")

    def allow_connections_from(
        self, other: aws.ec2.SecurityGroup, port_range: Ec2Port, opts: ResourceOptions
    ) -> None:
        descriptor = "".join(
            [
                "from_",
                other._name,
                "_to_",
                self.security_group._name,
                "_for_",
                str(port_range),
            ]
        )

        # We'll accept connections from Other into SecurityGroup
        aws.ec2.SecurityGroupRule(
            f"ingress_{descriptor}",
            opts=opts,
            type="ingress",
            source_security_group_id=other.id,
            security_group_id=self.security_group.id,
            from_port=port_range.port,
            to_port=port_range.port,
            protocol=port_range.protocol,
        )

        # Allow connections out of Other to Self
        aws.ec2.SecurityGroupRule(
            f"egress_{descriptor}",
            opts=opts,
            type="egress",
            # Perhaps this is wrong
            source_security_group_id=self.security_group.id,
            security_group_id=other.id,
            from_port=port_range.port,
            to_port=port_range.port,
            protocol=port_range.protocol,
        )
