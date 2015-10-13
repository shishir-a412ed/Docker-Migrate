import sys
import os
import subprocess

def import_docker(graph, import_location):
        if not os.path.isdir(import_location):
                sys.exit("Specified directory {0} does not exist".format(import_location))
        try:
                #import docker images
                import_images(import_location)
                #import docker containers
                import_containers(graph, import_location)
                #import docker volumes
                import_volumes(graph, import_location)
        except:
                e = sys.exc_info()[0]
                sys.exit(e)

        print("docker import completed successfully")
        print("Would you like to cleanup (rm -rf {0}) the temporary directory [y/N]".format(import_location))
        choice=sys.stdin.read(1)
        if (choice == 'y') or (choice == 'Y'):
           print("Deleting {0}".format(import_location))
           subprocess.check_call("rm -rf {0}".format(import_location), shell=True)
        else:
           print("Cleanup operation aborted")
        print("Please restart docker daemon for the changes to take effect")

def import_images(import_location):
        tarballs = subprocess.check_output("ls {0}/images".format(import_location), shell=True)
        splitTarballs = tarballs.split()
        for i in splitTarballs:
            print("Importing image {0}".format(i))
            subprocess.check_call("docker load < {0}/images/{1}".format(import_location, i), shell=True)

def import_containers(graph, import_location):
        if not os.path.isdir(import_location + "/containers"):
                sys.exit("Specified directory {0} does not exist.No containers to import.".format(import_location+"/containers"))

        containers = subprocess.check_output("ls {0}/containers".format(import_location), shell=True)
        splitContainers = containers.split()
        for i in splitContainers:
                print("Importing container ID:{0}".format(i[8:]))
                subprocess.check_call("/usr/bin/containers-migrate.sh import --container-id={0} --graph={1} --import-location={2}".format(i[8:], graph, import_location+"/containers"), shell=True)

def import_volumes(graph, import_location):
        print("Importing Volumes")
        subprocess.check_call(
            "tar --selinux -xzvf {0}/volumes/volumeData.tar.gz -C {1}/volumes > /dev/null".format(import_location, graph), shell=True)
        if os.path.isdir(graph + "/vfs"):
            subprocess.check_call(
                "tar --selinux -xzvf {0}/volumes/vfsData.tar.gz -C {1}/vfs > /dev/null".format(import_location, graph), shell=True)
