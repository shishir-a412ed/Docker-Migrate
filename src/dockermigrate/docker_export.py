"""
export docker images, containers and volumes into a filesystem directory.
"""
import sys
import os
import subprocess

def export_docker(graph, export_location):
    """
    This is a wrapper function for exporting docker images, containers
    and volumes.
    """
    if not os.path.isdir(export_location):
        os.mkdir(export_location)
    try:
        #export docker images
        export_images(export_location)
        #export docker containers
        export_containers(graph, export_location)
        #export docker volumes
        export_volumes(graph, export_location)
    except:
        error = sys.exc_info()[0]
        sys.exit(error)

    print("docker export completed successfully")

def export_images(export_location):
    """
    Method for exporting docker images into a filesystem directory.
    """
    if not os.path.isdir(export_location + "/images"):
        os.mkdir(export_location + "/images")
    images = subprocess.check_output("docker images", shell=True)
    split_images = images.split()[7:]  # cut off the headers
    names = []
    tags = []
    for i in range(0, len(split_images)):
        # only take the image and its tags and the image ID (to help in the <none>:<none> case)
        if i % 8 == 0:
            names.append(split_images[i])
            tags.append(split_images[i+1])
    for i in range(0, len(names)):
        print("Exporting image {0}:{1}".format(names[i], tags[i]))
        if names[i] == '<none>':
            print("This is a dangling image and will not be exported")
        else:
            subprocess.check_call(
                "docker save {0}:{1} > {2}/images/{3}-{4}.tar".format(
                    names[i], tags[i], export_location, names[i].replace("/", "~"),
                    tags[i].replace("/", "~")), shell=True)

def export_containers(graph, export_location):
    """
    Method for exporting docker containers into a filesystem directory.
    """
    if not os.path.isdir(export_location + "/containers"):
        os.mkdir(export_location + "/containers")

    containers = subprocess.check_output("docker ps -aq", shell=True)
    split_containers = containers.split()
    for i in range(0, len(split_containers)):
        print("Exporting container ID:{0}".format(split_containers[i]))
        subprocess.check_call("/usr/bin/containers-migrate.sh export --container-id={0}"
                              " --graph={1} --export-location={2}"
                              .format(split_containers[i], graph, export_location+"/containers"),
                              shell=True)

def export_volumes(graph, export_location):
    """
    Method for exporting docker volumes into a filesystem directory.
    """
    if not os.path.isdir(export_location + "/volumes"):
        os.mkdir(export_location + "/volumes")
    print("Exporting Volumes")
    subprocess.check_call("tar --selinux -zcvf {0}/volumes/volumeData.tar.gz"
                          " -C {1}/volumes . > /dev/null"
                          .format(export_location, graph), shell=True)
    if os.path.isdir(graph + "/vfs"):
        subprocess.check_call("tar --selinux -zcvf {0}/volumes/vfsData.tar.gz"
                              " -C {1}/vfs . > /dev/null"
                              .format(export_location, graph), shell=True)


