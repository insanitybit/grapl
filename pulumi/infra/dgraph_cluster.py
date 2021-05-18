from pathlib import Path
from typing import Any, Optional

import pulumi_aws as aws
from infra.bucket import Bucket
from infra.config import DEPLOYMENT_NAME, DGRAPH_LOG_RETENTION_DAYS
from infra.swarm import Ec2Port, Swarm

import pulumi
from pulumi.output import Output
from pulumi.resource import ResourceOptions

# These are COPYd in from Dockerfile.pulumi
DGRAPH_CONFIG_DIR = Path("../src/js/grapl-cdk/dgraph").resolve()


class DgraphCluster(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        vpc: aws.ec2.Vpc,
        opts: Optional[pulumi.ResourceOptions] = None,
    ) -> None:
        super().__init__("grapl:DgraphSwarmCluster", name=name, props=None, opts=opts)
        child_opts = pulumi.ResourceOptions(parent=self)

        self.log_group = aws.cloudwatch.LogGroup(
            f"{name}-dgraph-logs",
            retention_in_days=DGRAPH_LOG_RETENTION_DAYS,
            opts=child_opts,
        )

        self.swarm = Swarm(
            name=f"{name}-dgraph-swarm",
            vpc=vpc,
            log_group=self.log_group,
            internal_service_ports=[
                Ec2Port("tcp", x)
                for x in (
                    # DGraph alpha/zero port numbers
                    # https://dgraph.io/docs/deploy/dgraph-zero/
                    5080,
                    6080,
                    7081,
                    7082,
                    7083,
                    8081,
                    8082,
                    8083,
                    9081,
                    9082,
                    9083,
                )
            ],
            opts=child_opts,
        )

        self.dgraph_config_bucket = Bucket(
            logical_bucket_name="dgraph-config-bucket",
            opts=child_opts,
        )
        self.dgraph_config_bucket.grant_read_permissions_to(self.swarm.role)
        self.dgraph_config_bucket.upload_to_bucket(DGRAPH_CONFIG_DIR)

    @property
    def alpha_host_port(self) -> pulumi.Output[str]:
        # endpoint might be a better name
        return self.swarm.cluster_host_port()

    def allow_connections_from(self, other: aws.ec2.SecurityGroup) -> None:
        """
        Need to pass in a lambda? Access its `.function.security_group`
        """
        self.swarm.allow_connections_from(
            other, Ec2Port("tcp", 9080), opts=ResourceOptions(parent=self)
        )


class LocalStandInDgraphCluster(DgraphCluster):
    """
    We can't use the real DgraphCluster object yet because
    we are in this about-to-kill-off-local-grapl limbo world.

    However, I still want to feed an object matching its API into
    other lambdas, to replace `mg_alphas()`.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    @property
    def alpha_host_port(self) -> pulumi.Output[str]:
        config = pulumi.Config()
        endpoint = config.get("MG_ALPHAS") or f"{DEPLOYMENT_NAME}.dgraph.grapl:9080"
        return Output.from_input(endpoint)

    def allow_connections_from(self, other: aws.ec2.SecurityGroup) -> None:
        pass
