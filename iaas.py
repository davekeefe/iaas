"""
CALM DSL IaaS Blueprint

"""

from calm.dsl.builtins import AhvVmDisk, AhvVmNic, AhvVmGC
from calm.dsl.builtins import ref, basic_cred, AhvVmResources, AhvVm
from calm.dsl.builtins import vm_disk_package, read_spec

from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint
from calm.dsl.builtins import CalmVariable, CalmTask, action

from calm.dsl.builtins import parallel, read_provider_spec
from calm.dsl.builtins import read_local_file, provider_spec

NutanixPublicKey = read_local_file("nutanix_public_key")
NutanixKey = read_local_file("nutanix_key")
NutanixCred = basic_cred(
                    "nutanix",
                    name="Nutanix",
                    type="KEY",
                    password=NutanixKey,
                    default=True
                )

Centos74_Image = vm_disk_package(
                    name="centos7_generic",
                    config_file="image_configs/centos74_disk.yaml"
                )

class IaaS(Service):
    """IaaS service"""

    @action
    def NginxInstall():
        CalmTask.Exec.ssh(
            name="Intall Nginx",
            filename="scripts/nginx_install.sh",
            cred=NutanixCred
        )


class IaaSPackage(Package):
    """IaaS Package"""

    services = [ref(IaaS)]

    @action
    def __install__():
        IaaS.NginxInstall(name="Intall Ngnix")


class IaaSAhvVmResources(AhvVmResources):

    memory = 1
    vCPUs = 1
    cores_per_vCPU = 1
    disks = [
        AhvVmDisk.Disk.Scsi.cloneFromVMDiskPackage(Centos74_Image, bootable=True)
    ]
    nics = [
        AhvVmNic.NormalNic("vLAN_115"),
    ]
    boot_type = "BIOS"

    guest_customization = AhvVmGC.CloudInit(filename="scripts/guest_cus.yaml")


class IaaSAhvVm(AhvVm):

    resources = IaaSAhvVmResources


class IaaSVM(Substrate):
    """
    IaaS AHV Spec
    Default 1 CPU & 1 GB of memory
    1 disks 
    """

    provider_spec = IaaSAhvVm

    os_type = "Linux"
    readiness_probe = {
        "disabled": False,
        "delay_secs": "60",
        "connection_type": "SSH",
        "connection_port": 22,
        "credential": ref(NutanixCred),
    }


class IaaSDeployment(Deployment):
    """
    IaaS deployment
    """

    packages = [ref(IaaSPackage)]
    substrate = ref(IaaSVM)
    min_replicas = "1"
    max_replicas = "1"


class Default(Profile):
    """
    Default IaaS Application profile.
    """

    deployments = [IaaSDeployment]
    nutanix_public_key = CalmVariable.Simple.Secret(
        NutanixPublicKey,
        label="Nutanix Public Key",
        is_hidden=True,
        is_mandatory=False,
        runtime=False
    )
    domain_name = CalmVariable.Simple(
        "drm-poc.local",
        label="Domain Name",
        is_mandatory=True,
        runtime=True,
    )

class IaaS_Demo(Blueprint):
    """IaaS blueprint"""

    profiles = [Default]
    packages = [IaaSPackage,
                Centos74_Image]
    services = [IaaS]
    substrates = [IaaSVM]
    credentials = [NutanixCred]


def main():
    print(IaaS_Demo.json_dumps(pprint=True))


if __name__ == "__main__":
    main()
