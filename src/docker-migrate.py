#!/usr/bin/env python

import sys
import os
import subprocess
import argparse

def main():
	if len(sys.argv) == 1:
		sys.exit("""
	docker-migrate: too few arguments.
	Try 'docker-migrate --help' for more information.
	""")

	parser = argparse.ArgumentParser(description='docker migrate')
	subparsers = parser.add_subparsers(help="commands")

	exportp = subparsers.add_parser("export", help="export a docker instance",
        	epilog="export a docker instance."
        	"The export command would export docker images, containers and volumes. ")
	exportp.set_defaults(which='exportp')

	importp = subparsers.add_parser("import", help="import a docker instance",
        	epilog="import a docker instance."
        	"The import command would import docker images, containers and volumes. ")
	importp.set_defaults(which='importp')

	exportp.add_argument("--graph", dest="graph", default="/var/lib/docker",
                        help="Root of the Docker runtime (Default: /var/lib/docker)")
	exportp.add_argument("--export-location", dest="export_location", default="/var/lib/docker-migrate",
                        help="Path for exporting docker (Default: /var/lib/docker-migrate)")

	importp.add_argument("--graph", dest="graph", default="/var/lib/docker",
                        help="Root of the Docker runtime (Default: /var/lib/docker)")
	importp.add_argument("--import-location", dest="import_location", default="/var/lib/docker-migrate",
                        help="Path for importing docker (Default: /var/lib/docker-migrate)")

	args = parser.parse_args()

	if os.geteuid() != 0:
		os.system("clear")
                exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

	if args.which == "exportp":
		export_docker(args.graph, args.export_location)		
	elif args.which == "importp":	
		import_docker(args.graph, args.import_location)


def export_docker(graph, export_location):
	if not os.path.isdir(export_location):
		os.mkdir(export_location)
	#export docker images
	export_images(export_location)
	#export docker containers
	export_containers(graph, export_location)
	#export docker volumes
	export_volumes(graph, export_location)
	print("docker export completed successfully")

def import_docker(graph, import_location):
        if not os.path.isdir(import_location):
        	sys.exit("Specified directory {0} does not exist".format(import_location))
	#import docker images
        import_images(import_location)
        #import docker containers
        import_containers(graph, import_location)
        #import docker volumes
        import_volumes(graph, import_location)
	print("docker import completed successfully")

def export_images(export_location):
	if not os.path.isdir(export_location + "/images"):
        	os.mkdir(export_location + "/images")
	images = subprocess.check_output("docker images", shell=True)
        splitImages = images.split()[7:]  # cut off the headers
        names = []
        tags = []
        for i in range(0, len(splitImages)):
            # only take the image and its tags and the image ID (to help in the <none>:<none> case)
            if (i % 8 == 0):
                names.append(splitImages[i])
                tags.append(splitImages[i+1])
        for i in range(0, len(names)):
            print("Exporting image {0}:{1}".format(names[i], tags[i]))
            if names[i] == '<none>':
            	print("This is a dangling image and will not be exported")
	    else:
                subprocess.call(
                    "docker save {0}:{1} > {2}/images/{3}-{4}.tar".format(
                      	names[i], tags[i], export_location, names[i].replace("/", "~"), tags[i].replace("/", "~")), shell=True)

def export_containers(graph, export_location):
	if not os.path.isdir(export_location + "/containers"):
            os.mkdir(export_location + "/containers")

	containers = subprocess.check_output("docker ps -aq", shell=True)
        splitContainers = containers.split()
	for i in range(0, len(splitContainers)):
		print("Exporting container ID:{0}".format(splitContainers[i]))
		subprocess.call("/tmp/containers-migrate.sh export --container-id={0} --graph={1} --export-location={2}".format(splitContainers[i], graph, export_location+"/containers"), shell=True)


def export_volumes(graph, export_location):
	if not os.path.isdir(export_location + "/volumes"):
            os.mkdir(export_location + "/volumes")
	print("Exporting Volumes")
	subprocess.call(
            "tar -zcvf {0}/volumes/volumeData.tar.gz -C {1}/volumes . > /dev/null".format(export_location, graph), shell=True)
        if os.path.isdir(graph + "/vfs"):
            subprocess.call("tar -zcvf {0}/volumes/vfsData.tar.gz -C {1}/vfs . > /dev/null".format(export_location, graph), shell=True)

def import_images(import_location):
	tarballs = subprocess.check_output("ls {0}/images".format(import_location), shell=True)
        splitTarballs = tarballs.split()
        for i in splitTarballs:
            print("Importing image {0}".format(i))
            subprocess.call("docker load < {0}/images/{1}".format(import_location, i), shell=True)

def import_containers(graph, import_location):
	if not os.path.isdir(import_location + "/containers"):
                sys.exit("Specified directory {0} does not exist.No containers to import.".format(import_location+"/containers"))

	containers = subprocess.check_output("ls {0}/containers".format(import_location), shell=True)
	splitContainers = containers.split()
	for i in splitContainers:
		print("Importing container ID:{0}".format(i[8:]))	
		subprocess.call("/tmp/containers-migrate.sh import --container-id={0} --graph={1} --import-location={2}".format(i[8:], graph, import_location+"/containers"), shell=True)

def import_volumes(graph, import_location):
	print("Importing Volumes")
	subprocess.call(
            "tar xzvf {0}/volumes/volumeData.tar.gz -C {1}/volumes > /dev/null".format(import_location, graph), shell=True)
        if os.path.isdir(graph + "/vfs"):
            subprocess.call(
                "tar -xzvf {0}/volumes/vfsData.tar.gz -C {1}/vfs > /dev/null".format(import_location, graph), shell=True)

main()



	
