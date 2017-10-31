from utils import *
import dateutil.relativedelta
import dateutil.parser
from prettytable import PrettyTable



class ContadorUsoRecursos():
    """
    ContadorUsoRecursos recopila información de uso de los distintos tipos de recursos entre dos fechas.


    Args:
        - fecha_inicio: fecha de inicio desde la cual contar el uso de recursos
        - fecha_final: fecha final hasta la cual contar el uso de recursos
        - sesion_gnocchi: sesión gnocchi ante el API OpenStack
    """

    def __init__(self, fecha_inicio, fecha_final, sesion_gnocchi):
        """
        Inicialización de la clase

        :param fecha_inicio:
        :param fecha_final:
        :param sesion_gnocchi:
        """
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final
        self.sesion_gnocchi = sesion_gnocchi
        self.contador = dict()
        self.contador['vcpus'] = 0  # cuenta en unidades
        self.contador['ram_MB'] = 0  # cuenta en MBytes
        self.contador['hdd_GB'] = 0  # cuenta en GBytes
        self.contador['images_B'] = 0  # cuenta en Bytes
        self.contador['S3_B'] = 0  # cuenta en Bytes
        self.contador['ip_flotantes'] = 0
        self.contador['out_bytes'] = 0  # cuenta en Bytes

    def ActualizarContadorGauge(self, tipo_contador, metric):
        """
        Los contadores tipo "Gauge" son contadores que almacenan un valor de unidades en cada momento, donde
        cada medición no tiene relación con la anterior ni la siguiente. Por ejemplo, la temperatura en una serie
        temporal, sería un ejemplo de contador tipo Gauge.

        :param tipo_contador:
        :param metric:
        :return: None. Actualiza el contador de la clase.
        """
        mediciones_list = ObtenerMedicionesRecurso(self.sesion_gnocchi, metric, self.fecha_inicio, self.fecha_final)
        for i in range(len(mediciones_list) - 1):
            timestamp_0 = dateutil.parser.parse(mediciones_list[i][0])
            timestamp_1 = dateutil.parser.parse(mediciones_list[i + 1][0])
            minutos_intervalo = (timestamp_1 - timestamp_0).total_seconds() / 60.0
            self.contador[tipo_contador] += minutos_intervalo * mediciones_list[i][2]

    def ActualizarContadorIncremental(self, tipo_contador, metric):
        """
        Los contadores tipo incremental, son contadores que conforme avanza la serie temporal, van sumando/restando a
        partir del valor anterior. Por ejemplo, el dinero que se va gastando durante el mes, cuando empieza el mes el
        gatos es 0, pero conforme se hacen compras, el contador va subiendo, 10€, 200€, 250€. Al final del mes, el
        contador indica el dinero total gastado en el mes.
        :param tipo_contador:
        :param metric:
        :return: None. Actualiza el contador de la clase.
        """
        mediciones_list = ObtenerMedicionesRecurso(self.sesion_gnocchi, metric, self.fecha_inicio, self.fecha_final)
        if len(mediciones_list) > 0:
            # el último valor de la serie indica el total. Pero restar valor inicial.
            self.contador[tipo_contador] += mediciones_list[-1][2] - mediciones_list[0][
                2]  # el último valor de la serie indica el total

    def ActualizarContadoresUso(self):
        """
        Función que repasa cada recurso utilizado en el proyecto, y si se utilzó en el intervalo de tiempo
        especificado en la clase, entonces se calcula su uso.

        :return: None. Es una función que actualiza los contadores de la clase.
        """
        recursos = ListarRecursosGnocchi(sesion_gnocchi)

        for resource in recursos:
            if RecursoVivoEnMesIndicado(resource, self.fecha_inicio, self.fecha_final):
                if resource['type'] == 'instance':
                    self.ActualizarContadorGauge('vcpus', resource['metrics']['vcpus'])
                    self.ActualizarContadorGauge('hdd_GB', resource['metrics']['disk.root.size'])
                    self.ActualizarContadorGauge('ram_MB', resource['metrics']['memory'])

                elif resource['type'] == 'instance_network_interface':
                    self.ActualizarContadorIncremental('out_bytes', resource['metrics']['network.outgoing.bytes'])

                elif resource['type'] == 'ceph_account':
                    self.ActualizarContadorGauge('S3_B', resource['metrics']['radosgw.objects.size'])

                elif resource['type'] == 'image':
                    self.ActualizarContadorGauge('images_B', resource['metrics']['image.size'])

                elif resource['type'] == 'network':
                    self.ActualizarContadorGauge('ip_flotantes', resource['metrics']['ip.floating'])

    def ImprimirUsoRecursos(self):
        """
        Función que realiza una impresión en texto del uso de los recursos.

        :return: None
        """
        tabla = PrettyTable()
        tabla.field_names = ["Recurso", "Uso"]

        print("-------------------------------------------------------------------------------------------------------")
        print("USO DE RECURSOS INTERVALO FECHAS: %s ----- %s", self.fecha_inicio, self.fecha_final)
        print("-------------------------------------------------------------------------------------------------------")
        for key in self.contador.keys():
            tabla.add_row([key, self.contador[key]])

        print(tabla)
        print("")


if __name__ == "__main__":
    sesion_keystone = AbrirSesionKeystone()

    sesion_gnocchi = AbrirSesionGenocchi(sesion_keystone)

    dia_inicio_mes_actual, dia_final_mes_actual = ObtenerInicioFinMesActual()
    dia_inicio_mes_anterior, dia_final_mes_anterior = ObtenerInicioFinMesAnterior()

    UsoRecursosMesEnCurso = ContadorUsoRecursos(dia_inicio_mes_actual, dia_final_mes_actual, sesion_gnocchi)
    UsoRecursosMesEnAnterior = ContadorUsoRecursos(dia_inicio_mes_anterior, dia_final_mes_anterior, sesion_gnocchi)

    UsoRecursosMesEnCurso.ActualizarContadoresUso()
    UsoRecursosMesEnAnterior.ActualizarContadoresUso()

    UsoRecursosMesEnCurso.ImprimirUsoRecursos()
    UsoRecursosMesEnAnterior.ImprimirUsoRecursos()


