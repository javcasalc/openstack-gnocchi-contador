import keystoneauth1.identity
import keystoneauth1.session
import gnocchiclient.client
import os
import datetime
import dateutil.relativedelta
import dateutil.parser


def AbrirSesionKeystone():
    """
    Función que inicia el proceso de autenticación ante Keystone. Obtiene un token.

    :return: Devuelve el token de sesión.
    """
    try:
        auth = keystoneauth1.identity.v3.Password(auth_url=os.environ['OS_AUTH_URL'],
                                                  username=os.environ['OS_USERNAME'],
                                                  password=os.environ['OS_PASSWORD'],
                                                  user_domain_name=os.environ['OS_USER_DOMAIN_NAME'],
                                                  project_id=os.environ['OS_PROJECT_ID'],
                                                  project_name=os.environ['OS_PROJECT_NAME'])
    except:
        raise (Exception)

    try:
        sesion = keystoneauth1.session.Session(auth=auth)
        #sesion = keystoneauth1.session.Session(auth=auth, verify=os.environ['OS_CACERT'])
    except:
        raise (Exception)

    return sesion


def AbrirSesionGenocchi(sesion_keystone):
    """
    Función que abre la sesión contra el interfaz Gnocchi del sistema OpenStack.

    :param sesion_keystone:
    :return: token gnocchi.
    """
    try:
        gnocchic = gnocchiclient.client.Client(session=sesion_keystone, version=1)
    except:
        raise (Exception)

    return gnocchic


def ListarRecursosGnocchi(sesion_gnocchi):
    """
    Pregunta a Gnocchi por los recursos del proyecto.

    :param sesion_gnocchi:
    :return: lista con todos los recursos utilizados en el proyecto
    """
    try:
        resources_list = sesion_gnocchi.resource.list()
    except:
        raise (Exception)

    return resources_list


def ObtenerMedicionesRecurso(sesion_gnocchi, metric, start, stop):
    """
    Entre dos fechas, y para una métrica concreta, se obtiene la lista de mediciones hechas.

    :param sesion_gnocchi:
    :param metric:
    :param start:
    :param stop:
    :return: lista con las mediciones (measures) hechas para la métrica en el intervalo indicado
    """
    try:
        mediciones_list = sesion_gnocchi.metric.get_measures(metric, start=start, stop=stop)
    except:
        raise (Exception)

    return mediciones_list


def ObtenerInicioFinMesActual():
    """
    Función auxiliar que calcula las fechas frontera (por ejemplo, 1/Enero y 31/eEnero) del mes actual.

    :return: fecha inicio, fecha final
    """
    hoy = datetime.date.today()
    dia_inicio_mes = datetime.datetime(hoy.year, hoy.month, 1, tzinfo=datetime.timezone.utc)
    dia_final_mes = dia_inicio_mes + dateutil.relativedelta.relativedelta(months=1)

    return dia_inicio_mes, dia_final_mes


def ObtenerInicioFinMesAnterior():
    """
    Función auxiliar que calcula las fechas frontera(por ejemplo, 1/Enero y 31/eEnero) del mes anterior.

    :return: Fecha inicio del mes anterior, fecha inicio del mes actual
    """
    hoy = datetime.date.today()
    if hoy.month > 1:
        dia_inicio_mes = datetime.datetime(hoy.year, hoy.month - 1, 1, tzinfo=datetime.timezone.utc)
    else:
        dia_inicio_mes = datetime.datetime(hoy.year - 1, 12, 1, tzinfo=datetime.timezone.utc)
    dia_final_mes = dia_inicio_mes + dateutil.relativedelta.relativedelta(months=1)

    return dia_inicio_mes, dia_final_mes



def RecursoVivoEnMesIndicado(recurso, dia_inicio_mes, dia_final_mes):
    """
    Función auxiliar que determina si un recurso se estaba utilizando en un intervalo de tiempo dado
    :param recurso:
    :param dia_inicio_mes:
    :param dia_final_mes:
    :return: True o False
    """

    recurso_started_at = dateutil.parser.parse(recurso['started_at'])

    if recurso_started_at < dia_final_mes:
        if recurso['ended_at'] == None:
            return True
        else:
            recurso_ended_at = dateutil.parser.parse(recurso['ended_at'])
            if recurso_ended_at > dia_inicio_mes:
                return True

    return False

