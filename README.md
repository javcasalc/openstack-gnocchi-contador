# openstack-gnocchi-contador
Contador de uso de recursos Openstack mediante interfaz Gnocchi.

En un cloud basado en Openstack, el servicio "metering" es implementado por Gnocchi (http://gnocchi.xyz/)
Gnocchi almacena el uso de los recursos Openstack (instancias, redes, imágenes, volúmenes, etc.) en una base
de datos basada en series temporales (TSDB: https://en.wikipedia.org/wiki/Time_series_database).

Este programa consulta al interfaz Metering de Openstack, mediante Ghnocchi, y obtiene una visión de los
recursos utilizados en el mes en curso, y en el mes pasado.

# Instrucciones de Uso:

1) Instala Python3 (https://www.python.org/) y una vez instalado, crea un entorno virtual con Miniconda 
(https://conda.io/miniconda.html) o Virtualenv (https://virtualenv.pypa.io/en/stable/installation/)
2) Desde el entorno virtual instala los módulos necesarios: "pip install -r requirements.txt"
3) Con el Python3 y el entorno configurados, es el momento de obtener el fichero de acceso al 
API v3 Openstack del cloud al que se quiere acceder, normalmente suele ser algo tipo:

    https://<URL_CLOUD_OPENSTACK>/project/api_access/openrc/
    

4) Se descargará un fichero cuyo nombre suele ser parecido a "usuario-openrc.sh".
5) Añadir la siguiente línea al fichero descargado: 

    "echo export OS_AUTH_TYPE=password >> usuario-openrc.sh"
    
6) Leer el fichero con el comando "source usuario-openrc.sh". Normalmente pedirá la clave del usuario.
7) Si todo ha ido bien, finalmente podremos lanzar el programa contador de uso de recursos:

    "python gnocchi-contador-uso-recursos.py"

    


# Ejemplo de uso:


[usuario1@linux ]$ python gnocchi-contador-uso-recursos.py 
-------------------------------------------------------------------------------------------------------
USO DE RECURSOS INTERVALO FECHAS: %s ----- %s 2017-10-01 00:00:00+00:00 2017-11-01 00:00:00+00:00
-------------------------------------------------------------------------------------------------------
+--------------+--------------------+
|   Recurso    |        Uso         |
+--------------+--------------------+
|    vcpus     | 10935.882352941177 |
|    ram_MB    |     5555200.0      |
|    hdd_GB    |      10850.0       |
|   images_B   |   156864084480.0   |
|     S3_B     |   356561735680.0   |
| ip_flotantes |      30655.0       |
|  out_bytes   |      15646.0       |
+--------------+--------------------+

-------------------------------------------------------------------------------------------------------
USO DE RECURSOS INTERVALO FECHAS: %s ----- %s 2017-09-01 00:00:00+00:00 2017-10-01 00:00:00+00:00
-------------------------------------------------------------------------------------------------------
+--------------+-----+
|   Recurso    | Uso |
+--------------+-----+
|    vcpus     |  0  |
|    ram_MB    |  0  |
|    hdd_GB    |  0  |
|   images_B   |  0  |
|     S3_B     |  0  |
| ip_flotantes |  0  |
|  out_bytes   |  0  |
+--------------+-----+



