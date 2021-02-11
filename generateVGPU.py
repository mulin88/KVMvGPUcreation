import os
import subprocess
import uuid
# import libvirt

folder_cProfile = "/sys/bus/pci/devices/0000\:3b\:00.0/mdev_supported_types/"
folder_qProfile = "/sys/bus/pci/devices/0000\:d8\:00.0/mdev_supported_types/"
uuid_cProfile = []
uuid_qProfile = []
gpu_pci_C_profile = "0000:3b:00.0"   # for C profile
gpu_pci_Q_profile = "0000:d8:00.0"   # for Q profile
vGpu_C_profile = "nvidia-430"
vGpu_Q_profile = "nvidia-410"

vm_cProfile = ["mwp-node1", "mwp-node2", "mwp-node3", "mwp-node4"]
vm_qProfile = ["win10-enterprise", "ubuntu1"]

def shutdownVM():
    # TBD
    print("To shutdown all VM w/ libvirt before others")


if __name__ == '__main__':
    C_available_instances = 0
    Q_available_instances = 0

    # Check current avaiable vGPU instances
    cmd_C_available = "cat {}{}/available_instances".format(folder_cProfile,vGpu_C_profile)
    stream = os.popen(cmd_C_available)
    C_available_instances = int(stream.read().strip())
    cmd_Q_available = "cat {}{}/available_instances".format(folder_qProfile,vGpu_Q_profile)
    stream = os.popen(cmd_Q_available)
    Q_available_instances = int(stream.read().strip())

    #Generate UUID for GPU C_Profile
    if C_available_instances > 0:
        for i in range(C_available_instances):
            output = uuid.uuid4()
            uuid_cProfile.append(output)

    #Generate UUID for GPU Q_Profile
    if Q_available_instances > 0:
        for i in range(Q_available_instances):
            output = uuid.uuid4()
            uuid_qProfile.append(output)

    # Generate Q profile vGPU instances
    for i in range(4):
        cmd = "mdevctl start -u {} -p {} --type {}".format(uuid_qProfile[i], gpu_pci_Q_profile, vGpu_Q_profile)
        os.system(cmd)
        cmd2 = " mdevctl define --auto --uuid {}".format(uuid_qProfile[i])
        os.system(cmd2)

    # Generate C profile vGPU instances
    for i in range(4):
        cmd = "mdevctl start -u {} -p {} --type {}".format(uuid_cProfile[i], gpu_pci_C_profile, vGpu_C_profile)
        os.system(cmd)
        cmd2 = " mdevctl define --auto --uuid {}".format(uuid_cProfile[i])
        os.system(cmd2)



