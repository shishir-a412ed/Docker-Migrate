#       DOCKER MIGRATE

	      This tool allows the user to easily migrate images, volumes, and
        containers from one version of Docker to another. With this tool, 
        users can quickly save all their data from the current docker
        instance, change the docker storage backend, and then import all 
        their old data to the new system.
        
##      ./docker-migrate export [directory]

        Specify the directory in which to temporarily store the files (can be
        an existing directory, or the command will create one). If no directory
        is specified, `/var/lib/docker-migrate` would be used as default.
        The export command will export all the current images, volumes, and
        containers to the specified directory, in the /images, /volumes,
        /containers subdirectories.

## ./docker-migrate import [directory]
        
        Specify the directory from which to read the files (must be an
        existing directory).If no directory is specified, 
        `/var/lib/docker-migrate` would be used as default.
        The import command will import images, volumes, and containers from
        the specified directory into the new docker instance.
        
        Primary Author: Jenny Ramseyer, 2015
        Secondary Author: Shishir Mahajan, 2015
