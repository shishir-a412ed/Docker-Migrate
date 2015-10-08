#!/bin/bash
# bash script to migrate containers from one backend storage to another.
set -e

main() {
if [ "$USER" != "root" ];then
	echo "Run 'containers-migrate' as root user"
	exit 
fi

NUMARGS=$#

if [ $NUMARGS -eq 0 ] || [ "$1" = "--help" ];then 
	echo "Usage: containers-migrate COMMAND [OPTIONS]"
	echo -e "       containers-migrate [--help]\n"
	echo -e "A self-sufficient tool for migrating docker containers from one backend storage to another\n"
	echo "Commands:"
	echo "    export  Export a container from an existing storage"
	echo "    import  Import a container into a new storage" 
	exit
fi

if [ "$1" = "export" ];then
   if [ -z "$2" ]; then
	echo "containers-migrate: "export" requires a minimum of 1 argument." 
	echo -e "See 'containers-migrate export --help'\n"
	echo -e "Usage: containers-migrate export [OPTIONS]\n"
	echo "Export a container from an existing storage"
	exit
   elif [ "$2" = "--help" ];then
	echo -e "\nUsage: containers-migrate export [OPTIONS]\n"
	echo -e "Export a container from an existing storage\n"
	echo "--container-id      ID of the container to be exported" 
	echo "--graph   	    Root of the Docker runtime (Default: /var/lib/docker)"
	echo "--export-location   Path for exporting the container (Default: /var/lib/docker-migrate)"
	exit
   else
	container_export $2 $3 $4
   fi
fi

if [ "$1" = "import" ];then
   if [ -z "$2" ]; then
        echo "containers-migrate: "import" requires a minimum of 1 argument." 
        echo -e "See 'containers-migrate import --help'\n"
        echo -e "Usage: containers-migrate import [OPTIONS]\n"
        echo "Import a container into a new storage"
        exit
   elif [ "$2" = "--help" ];then
        echo -e "\nUsage: containers-migrate import [OPTIONS]\n"
        echo -e "Import a container into a new storage\n"
        echo "--container-id      ID of the container to be imported" 
        echo "--graph             Root of the Docker runtime (Default: /var/lib/docker)"
	echo "--import-location   Path for importing the container (Default: /var/lib/docker-migrate)"
        exit
   else
        container_import $2 $3 $4
   fi
fi

}

container_export(){
	for arg in "$@"
	do 
		flag=$(echo $arg|cut -d'=' -f 1)
		val=$(echo $arg|cut -d'=' -f 2)
		case "$flag" in
			--container-id)
				containerID=$val
			;;
			--graph)
				dockerRootDir=$val
			;;
			--export-location)
				exportPath=$val
			;;
		esac
	done

	if [ -z "$containerID" ]; then
		echo "--container-id cannot be null"
		exit 1
	fi

	if [ -z "$exportPath" ]; then
		exportPath="/var/lib/docker-migrate"
	fi

        dockerPid=$(ps aux|grep [d]ocker|awk 'NR==1{print $2}')
        dockerCmdline=$(cat /proc/$dockerPid/cmdline)||exit 1
        if [[ $dockerCmdline =~ "-g=" ]] || [[ $dockerCmdline =~ "-g/" ]] || [[ $dockerCmdline =~ "--graph" ]];then
                if [ -z "$dockerRootDir" ];then
                        echo "Docker is not located at the default (/var/lib/docker) root location."
                        echo "Please provide the new root location of the docker runtime in --graph option."
        		exit 1
                fi
        else
                dockerRootDir="/var/lib/docker"
        fi
        notruncContainerID=$(docker ps -aq --no-trunc|grep $containerID)||exit 1
        tmpDir=$exportPath/migrate-$containerID
        mkdir -p $tmpDir
        cd $tmpDir
	containerBaseImageID=$(docker inspect --format '{{.Image}}' $containerID)||exit 1
	echo $dockerRootDir>dockerInfo.txt
	echo $containerBaseImageID>>dockerInfo.txt
	echo $notruncContainerID>>dockerInfo.txt
        /tmp/tar -cf container-metadata.tar $dockerRootDir/containers/$notruncContainerID 2> /dev/null
        imageID=$(docker commit $containerID)||exit 1
        mkdir $tmpDir/temp
        docker save $imageID > $tmpDir/temp/image.tar||exit 1
	cd $tmpDir/temp
        /tmp/tar -xf image.tar
        cd $tmpDir/temp/$imageID
        cp layer.tar $tmpDir/container-diff.tar
        cd $tmpDir
        rm -rf temp
        docker rmi -f $imageID 1>/dev/null||exit 1
	echo "Container exported succesfully"
}

container_import(){
	for arg in "$@"
        do
                flag=$(echo $arg|cut -d'=' -f 1)
                val=$(echo $arg|cut -d'=' -f 2)
                case "$flag" in
                        --container-id)
                                containerID=$val
                        ;;
                        --graph)
                                dockerRootDir=$val
                        ;;
                        --import-location)
                                importPath=$val
                        ;;
                esac
        done

        if [ -z "$containerID" ]; then
                echo "--container-id cannot be null"
                exit
        fi

        if [ -z "$importPath" ]; then
                importPath="/var/lib/docker-migrate"
        fi

	dockerPid=$(ps aux|grep [d]ocker|awk 'NR==1{print $2}')
        dockerCmdline=$(cat /proc/$dockerPid/cmdline)||exit 1
        if [[ $dockerCmdline =~ "-g=" ]] || [[ $dockerCmdline =~ "-g/" ]] || [[ $dockerCmdline =~ "--graph" ]];then
                if [ -z "$dockerRootDir" ];then
                        echo "Docker is not located at the default (/var/lib/docker) root location."
                        echo "Please provide the new root location of the docker runtime in --graph option."
                        exit 1
                fi
        else
                dockerRootDir="/var/lib/docker"
        fi

	cd $importPath/migrate-$containerID
	dockerBaseImageID=$(sed -n '2p' dockerInfo.txt)||exit 1	
	cat container-diff.tar|docker run -i -v /tmp/tar:/tmp/tar $dockerBaseImageID /tmp/tar -xf -
	newContainerID=$(docker ps -lq)||exit 1
	newContainerName=$(docker inspect -f '{{.Name}}' $newContainerID)||exit 1
	newNotruncContainerID=$(docker ps -aq --no-trunc|grep $newContainerID)||exit 1					
	cd $dockerRootDir/containers/$newNotruncContainerID
	rm -rf *
	cp $importPath/migrate-$containerID/container-metadata.tar .
	/tmp/tar -xf container-metadata.tar	
	rm container-metadata.tar
	oldDockerRootDir=$(sed -n '1p' $importPath/migrate-$containerID/dockerInfo.txt)||exit 1
	oldNotruncContainerID=$(sed -n '3p' $importPath/migrate-$containerID/dockerInfo.txt)||exit 1
	cp -r ${oldDockerRootDir:1}/containers/$oldNotruncContainerID/* .
	baseDir=$(echo $oldDockerRootDir|cut -d"/" -f 2)
	rm -rf $baseDir

	sed -i "s|$oldDockerRootDir/containers/$oldNotruncContainerID|$dockerRootDir/containers/$oldNotruncContainerID|g" config.json

	cd $dockerRootDir
	find . -name "*$newNotruncContainerID*" -type d -exec rename $newNotruncContainerID $oldNotruncContainerID {} +
	find . -name "*$newNotruncContainerID*" -type f -exec rename $newNotruncContainerID $oldNotruncContainerID {} +
	
	echo "Container imported succesfully"
}

main "$@"
