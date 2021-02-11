import os
import subprocess
import xml.etree.ElementTree as ET
import tempfile
import shutil
# import libvirt

sampleVMxmlFolder = '/root/changeXMLuuid'
sampleXMlfile = 'mwp-node1.xml'
tmpXMLfile = sampleVMxmlFolder + "/" + sampleXMlfile + ".new"

uuid_cProfile = []
uuid_qProfile = []
vGpu_C_profile = "nvidia-430"
vGpu_Q_profile = "nvidia-410"

vm_cProfile = ["mwp-node1", "mwp-node2", "mwp-node3", "mwp-node4"]
vm_qProfile = ["ubuntu1", "win10-enterprise"]

def allVMshutdown():
    cmd = "virsh list"
    stream = os.popen(cmd)
    lines = 0
    for line in stream:
        if line != "\n":
            lines += 1
    if lines > 2:
        return -1
    else:
        return 0

def readVGPUinstancesUUID():
    cmd = "mdevctl list"
    stream = os.popen(cmd)
    for line in stream:
        element = line.split()
        if element[2] == vGpu_C_profile:
            uuid_cProfile.append(element[0])
        elif element[2] == vGpu_Q_profile:
            uuid_qProfile.append(element[0])
        else:
            print("vGPU profile does not match! {}".format(element[2]))
    cProfileAmount = len(uuid_cProfile)
    qProfileAmount = len(uuid_qProfile)
    print("Total vGPU instances found {}, C_profile {}, Q_profile {}".format(cProfileAmount+qProfileAmount, cProfileAmount, qProfileAmount))


def addOrReplaceUUID():
    tempFolder = tempfile.mkdtemp()
    print("Folder for VM xmls files: {}".format(tempFolder))
    os.system("cd {}".format(tempFolder))

    for vms, uuids in zip([vm_cProfile, vm_qProfile], [uuid_cProfile, uuid_qProfile]):
        for index, vm in enumerate(vms):
            new_uuid = uuids[index]
            os.system("virsh dumpxml {} > {}/{}.old.xml".format(vm, tempFolder, vm))
            vm_xml_old = "{}/{}.old.xml".format(tempFolder, vm)
            vm_xml_new = "{}/{}.new.xml".format(tempFolder, vm)
            vmTree = ET.parse(vm_xml_old)
            vmRoot = vmTree.getroot()

            if vmRoot.findall('*/hostdev') == []:
                print("{} previous UUID not exist".format(vm))
                # add a new block
                hostdevblock = ET.Element("hostdev")
                hostdevblock.attrib['mode'] = 'subsystem'
                hostdevblock.attrib['type'] = 'mdev'
                hostdevblock.attrib['model'] = 'vfio-pci'
                sourceEl = ET.Element("source")
                hostdevblock.append(sourceEl)
                addressEl = ET.Element("address")
                addressEl.attrib['uuid'] = new_uuid
                sourceEl.append(addressEl)
                hostdevblock.tail = "\n    "

                deviceRoot = vmRoot.find('.//devices')
                if deviceRoot != []:
                    deviceRoot.insert(0, hostdevblock)
                else:
                    print("{} can't find device block/n".format(vm))
            else:
                print("vm {} previous UUID exist".format(vm))
                for hostdevitem in vmRoot.findall('*/hostdev'):
                    for child in hostdevitem:
                        if child.tag == 'source':
                            for subitem in child:
                                if subitem.tag == 'address':
                                    print("vm {} Previous uuid: {}".format(vm, subitem.attrib['uuid']))
                                    subitem.attrib['uuid'] = new_uuid
                                    print(subitem.attrib['uuid'])
                                    print("vm {} New uuid: {}".format(vm, subitem.attrib['uuid']))
    
            # save the changes to file
            tree = ET.ElementTree(vmRoot)
            with open(vm_xml_new, "wb") as xmlFile:
                tree.write(xmlFile)

if __name__ == '__main__':
    readVGPUinstancesUUID()

    if len(uuid_cProfile) < len(vm_cProfile) or len(uuid_qProfile) < len(vm_qProfile):
        print("There are not enough vGPU instances for predefined VMs")
        exit(0)

    if allVMshutdown() != 0:
        print("There are VM still running, please shutdown\n")
        exit(0)

    addOrReplaceUUID()




