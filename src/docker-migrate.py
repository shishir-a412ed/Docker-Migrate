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
	print(args)
	exit("success")

	if os.geteuid() != 0:
		os.system("clear")
                exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

	if args.which == "exportp":
		export_docker(args.graph, args.export_location)		
	elif args.which == "importp":	
		import_docker(args.graph, args.import_location)


def export_docker(exportDir):
	if not os.path.isdir(exportDir):
		os.mkdir(exportDir)
	#export docker images
	export_images(exportDir)
	#export docker containers
	export_containers(exportDir)
	#export docker volumes
	export_volumes(exportDir)
	print("docker export completed successfully")

def import_docker(importDir):
        if not os.path.isdir(importDir):
        	sys.exit("Specified directory {0} does not exist".format(importDir))
	#import docker images
        import_images(importDir)
        #import docker containers
        import_containers(importDir)
        #import docker volumes
        import_volumes(importDir)
	print("docker import completed successfully")

def export_images(exportDir):
	if not os.path.isdir(exportDir + "/images"):
        	os.mkdir(exportDir + "/images")
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
            print("Saving image {0}:{1}".format(names[i], tags[i]))
            if names[i] == '<none>':
            	print("This is a dangling image and will not be exported")
	    else:
                subprocess.call(
                    "docker save {0}:{1} > {2}/images/{3}-{4}.tar".format(
                      	names[i], tags[i], exportDir, names[i].replace("/", "~"), tags[i].replace("/", "~")), shell=True)

def export_containers(exportDir):
	if not os.path.isdir(exportDir + "/containers"):
            os.mkdir(exportDir + "/containers")

def export_volumes(exportDir):
	if not os.path.isdir(exportDir + "/volumes"):
            os.mkdir(exportDir + "/volumes")
	subprocess.call(
            "tar -zcvf {0}/volumes/volumeData.tar.gz -C /var/lib/docker/volumes . > /dev/null".format(exportDir), shell=True)
        if os.path.isdir("/var/lib/docker/vfs"):
            subprocess.call("tar -zcvf {0}/volumes/vfsData.tar.gz -C /var/lib/docker/vfs . > /dev/null".format(exportDir), shell=True)

def import_images(importDir):
	tarballs = subprocess.check_output("ls {0}/images".format(importDir), shell=True)
        splitTarballs = tarballs.split()
        for i in splitTarballs:
            print("Loading image {0}".format(i))
            subprocess.call("docker load < {0}/images/{1}".format(importDir, i), shell=True)

def import_containers(importDir):
	print("import_containers")

def import_volumes(importDir):
	subprocess.call(
            "tar xzvf {0}/volumes/volumeData.tar.gz -C /var/lib/docker/volumes > /dev/null".format(importDir), shell=True)
        if os.path.isdir("/var/lib/docker/vfs"):
            subprocess.call(
                "tar -xzvf {0}/volumes/vfsData.tar.gz -C /var/lib/docker/vfs > /dev/null".format(importDir), shell=True)

main()



	
