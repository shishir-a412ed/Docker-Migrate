## docker-migrate
 
Docker migrate is a CLI tool that allows the user to easily 
migrate images, volumes, and containers from one version of Docker
to another. With this tool, users can quickly save all their data 
from the current docker instance, change the docker storage backend, 
and then import all their old data to the new system.

## setup

To setup docker-migrate on your linux environment, do the following:

	a) git clone git@github.com:shishir-a412ed/Docker-Migrate.git
	b) cd Docker-Migrate/src
	c) cp containers-migrate.sh tar /tmp 

## how to use docker-migrate

`./docker-migrate.py -h|--help` should display the help menu.

docker-migrate has two commands: 

	a) export 
	b) import
        
## docker-migrate export

`./docker-migrate.py export [-h|--help] [--graph] [--export-location]`
	
`./docker-migrate.py export -h|--help` will display the help menu.

docker-migrate export has 2 optional flags:

**--graph**

Root of the docker runtime. If you are running docker at the 
default location (`/var/lib/docker`), you don't need to pass this flag.
However if you are running docker at a custom location. This flag must 
be set.
	
**--export-location**

Directory in which to temporarily store the files (can be an existing 
directory, or the command will create one). If no directory is specified, 
`/var/lib/docker-migrate` would be used as default.

The export command will export all the current images, volumes, and
containers to the specified directory, in the /images, /volumes,
/containers subdirectories.

## docker-migrate import

`./docker-migrate.py import [-h|--help] [--graph] [--import-location]`

`./docker-migrate import -h|--help` will display the help menu.

docker-migrate import has 2 optional flags:

**--graph**

Root of the docker runtime. If you are running docker at the
default location (`/var/lib/docker`), you don't need to pass this flag.
However if you are running docker at a custom location. This flag must 
be set.

**--import-location**

Directory from which to import the files (images, containers and volumes). 
If this flag is not set docker-migrate will assume the import location to 
be `/var/lib/docker-migrate`. Whether you set this flag or use the default, 
the directory must be present for the import to happen successfully.

The import command will import images, volumes, and containers from
the specified directory into the new docker instance.
        
## author
Primary: Shishir Mahajan, 2015

Secondary Jenny Ramseyer, 2015
