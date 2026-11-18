from copy import deepcopy
from rover import Entorno


def validar_plan(entorno, plan, tiempo_maximo=None,
                 recompensa_muestra=100):
    """
    Valida un plan del rover sobre una copia del entorno.

    Parámetros
    ----------
    entorno : Entorno
        Instancia inicial del entorno.
    plan : list
        Secuencia de acciones que ejecutará el rover.

        Acciones permitidas:
            ("mover", dx, dy)
            ("recolectar",)
            ("transmitir",)
            ("recargar",)

    tiempo_maximo : int, float o None
        Tiempo máximo de la misión. Si es None no se limita el tiempo.

    recompensa_muestra : int o float
        Puntos obtenidos por cada muestra transmitida.

    Devuelve
    --------
    dict
        Resultado de la validación, errores, estado final
        y puntuación de la misión.
    """

    if not isinstance(entorno, Entorno):
        raise TypeError("El entorno debe ser una instancia de Entorno.")

    if not isinstance(plan, (list, tuple)):
        raise TypeError("El plan debe ser una lista o tupla de acciones.")

    if (not isinstance(recompensa_muestra, (int, float)) or isinstance(recompensa_muestra, bool) or recompensa_muestra < 0):
        raise ValueError("La recompensa debe ser un número no negativo.")

    if tiempo_maximo is not None and (not isinstance(tiempo_maximo, (int, float)) or isinstance(tiempo_maximo, bool) or tiempo_maximo < 0):
        raise ValueError("El tiempo máximo debe ser None o un número no negativo.")


    sim = deepcopy(entorno)

    def excede_tiempo(tiempo_accion):
        """Indica si ejecutar la acción superaría el tiempo máximo."""
        return (tiempo_maximo is not None and sim.rover.time + tiempo_accion > tiempo_maximo)

    errores = []
    acciones_ejecutadas = 0

    muestras_transmitidas = set()

    for numero, accion in enumerate(plan, start=1):


        if (not isinstance(accion, (tuple, list))or len(accion) == 0  or not isinstance(accion[0], str)):
            errores.append({
                "accion": numero,
                "tipo": "formato",
                "mensaje": "La acción está vacía o mal formada."
            })
            break

        nombre = accion[0]

        if nombre == "mover":

            if len(accion) != 3:
                errores.append({
                    "accion": numero,
                    "tipo": "formato",
                    "mensaje": "La acción mover necesita dx y dy."
                })
                break

            dx, dy = accion[1], accion[2]

            # Los desplazamientos deben ser enteros.
            if (not isinstance(dx, int) or isinstance(dx, bool) or not isinstance(dy, int)or isinstance(dy, bool)):
                errores.append({
                    "accion": numero,
                    "tipo": "movimiento",
                    "mensaje": "dx y dy deben ser enteros."
                })
                break

            if (dx not in (-1, 0, 1) or dy not in (-1, 0, 1) or (dx == 0 and dy == 0)):
                errores.append({
                    "accion": numero,
                    "tipo": "movimiento",
                    "mensaje": "El desplazamiento no está permitido."
                })
                break

            nx = sim.rover.x + dx
            ny = sim.rover.y + dy

            if not (0 <= nx < sim.size_x and 0 <= ny < sim.size_y):
                errores.append({
                    "accion": numero,
                    "tipo": "limites",
                    "mensaje": "El rover intentó salir del mapa."
                })
                break

            terreno = sim.map[nx][ny]
            if terreno == "O":
                errores.append({
                    "accion": numero,
                    "tipo": "obstaculo",
                    "mensaje": "El destino contiene un obstáculo."
                })
                break

            coste_bateria, coste_tiempo = sim.cost_mov(terreno)

            if coste_bateria is False:
                errores.append({
                    "accion": numero,
                    "tipo": "terreno",
                    "mensaje": "El terreno no tiene costes definidos."
                })
                break

            if sim.rover.battery < coste_bateria:
                errores.append({
                    "accion": numero,
                    "tipo": "bateria",
                    "mensaje": "Batería insuficiente para moverse."
                })
                break

            if excede_tiempo(coste_tiempo):
                errores.append({
                    "accion": numero,
                    "tipo": "tiempo",
                    "mensaje": "El movimiento superaría el tiempo máximo."
                })
                break

            ejecutada = sim.mov(dx, dy)

            if ejecutada is not True:
                errores.append({
                    "accion": numero,
                    "tipo": "ejecucion",
                    "mensaje": "No se pudo ejecutar el movimiento."
                })
                break
            

        # ACCIÓN: RECOLECTAR
        elif nombre == "recolectar":

            if len(accion) != 1:
                errores.append({
                    "accion": numero,
                    "tipo": "formato",
                    "mensaje": "Recolectar no necesita argumentos."
                })
                break

            x, y = sim.rover.x, sim.rover.y

            if sim.map[x][y] != "M":
                errores.append({
                    "accion": numero,
                    "tipo": "recoleccion",
                    "mensaje": "No hay ninguna muestra en esta posición."
                })
                break

            if sim.rover.battery < 8:
                errores.append({
                    "accion": numero,
                    "tipo": "bateria",
                    "mensaje": "Batería insuficiente para recolectar."
                })
                break

            if sim.rover.memory < 15:
                errores.append({
                    "accion": numero,
                    "tipo": "memoria",
                    "mensaje": "Memoria insuficiente para recolectar."
                })
                break

            if excede_tiempo(8):
                errores.append({
                    "accion": numero,
                    "tipo": "tiempo",
                    "mensaje": "Recolectar superaría el tiempo máximo."
                })
                break

            sim.collect_samples()

        # ACCIÓN: TRANSMITIR
        elif nombre == "transmitir":

            if len(accion) != 1:
                errores.append({
                    "accion": numero,
                    "tipo": "formato",
                    "mensaje": "Transmitir no necesita argumentos."
                })
                break

            x, y = sim.rover.x, sim.rover.y

            if sim.map[x][y] != "C":
                errores.append({
                    "accion": numero,
                    "tipo": "comunicacion",
                    "mensaje": "El rover no está en una zona de comunicación."
                })
                break

            memoria_ocupada = (
                sim.rover.max_memory - sim.rover.memory
            )

            energia_necesaria = int(memoria_ocupada / 3)
            tiempo_necesario = int(memoria_ocupada / 3)

            if energia_necesaria > sim.rover.battery:
                errores.append({
                    "accion": numero,
                    "tipo": "bateria",
                    "mensaje": "Batería insuficiente para transmitir."
                })
                break

            if excede_tiempo(tiempo_necesario):
                errores.append({
                    "accion": numero,
                    "tipo": "tiempo",
                    "mensaje": "Transmitir superaría el tiempo máximo."
                })
                break

            pendientes = (
                sim.rover.collected_samples - muestras_transmitidas
            )

            sim.transmit_information()

            muestras_transmitidas.update(pendientes)

        # ACCIÓN: RECARGAR
        elif nombre == "recargar":

            if len(accion) != 1:
                errores.append({
                    "accion": numero,
                    "tipo": "formato",
                    "mensaje": "Recargar no necesita argumentos."
                })
                break

            posicion_actual = (
                sim.rover.x,
                sim.rover.y
            )

            if posicion_actual != sim.base:
                errores.append({
                    "accion": numero,
                    "tipo": "recarga",
                    "mensaje": "El rover no está en la base."
                })
                break

            if sim.rover.battery == sim.rover.max_energy:
                errores.append({
                    "accion": numero,
                    "tipo": "recarga",
                    "mensaje": "La batería ya está completa."
                })
                break

            energia = (sim.rover.max_energy - sim.rover.battery)

            tiempo_necesario = int(energia / 2)

            if excede_tiempo(tiempo_necesario):
                errores.append({
                    "accion": numero,
                    "tipo": "tiempo",
                    "mensaje": "Recargar superaría el tiempo máximo."
                })
                break

            sim.charge()

        # ACCIÓN DESCONOCIDA
        else:
            errores.append({
                "accion": numero,
                "tipo": "accion_desconocida",
                "mensaje": f"Acción desconocida: {nombre}"
            })
            break

        acciones_ejecutadas += 1


    objetivo_alcanzado = sim.is_objective()

    muestras_pendientes = (sim.rover.collected_samples - muestras_transmitidas)

    mision_completada = (objetivo_alcanzado and len(muestras_pendientes) == 0)

    puntuacion = (
        recompensa_muestra * len(muestras_transmitidas)
        - sim.rover.cost
    )

    resultado = {
        "factible": len(errores) == 0,
        "mision_completada": mision_completada,
        "objetivo_alcanzado": objetivo_alcanzado,
        "errores": errores,
        "acciones_ejecutadas": acciones_ejecutadas,
        "acciones_totales": len(plan),
        "posicion_final": (sim.rover.x,sim.rover.y),
        "bateria_restante": sim.rover.battery,
        "memoria_restante": sim.rover.memory,
        "tiempo_total": sim.rover.time,
        "tiempo_maximo": tiempo_maximo,
        "coste_total": sim.rover.cost,
        "muestras_recogidas": len(sim.rover.collected_samples),
        "muestras_transmitidas": len(muestras_transmitidas),
        "muestras_pendientes": len(muestras_pendientes),
        "puntuacion": puntuacion
    }

    return resultado



def mostrar_resultado(resultado):
    """
    Imprime un resumen legible de la validación.
    """

    print("\n" + "=" * 50)
    print("         RESULTADO DE LA VALIDACIÓN")
    print("=" * 50)

    print("Plan factible:", resultado["factible"])
    print("Misión completada:", resultado["mision_completada"])
    print("Objetivo alcanzado:", resultado["objetivo_alcanzado"])
    print(
        "Acciones ejecutadas:",
        resultado["acciones_ejecutadas"],
        "/",
        resultado["acciones_totales"]
    )

    print("Posición final:", resultado["posicion_final"])
    print("Batería restante:", resultado["bateria_restante"])
    print("Memoria restante:", resultado["memoria_restante"])
    print("Tiempo total:", resultado["tiempo_total"])
    if resultado["tiempo_maximo"] is not None:
        print("Tiempo máximo:", resultado["tiempo_maximo"])
    print("Coste total:", resultado["coste_total"])
    print("Muestras recogidas:", resultado["muestras_recogidas"])
    print("Muestras transmitidas:", resultado["muestras_transmitidas"])
    print("Muestras pendientes:", resultado["muestras_pendientes"])
    print("Puntuación:", resultado["puntuacion"])
    if resultado["errores"]:
        print("\nRestricciones incumplidas:")

        for error in resultado["errores"]:
            print(
                f"  Acción {error['accion']}: "
                f"{error['mensaje']}"
            )
    else:
        print("\nNo se detectaron infracciones durante la ejecución.")

    if not resultado["mision_completada"]:
        print("\nAdvertencia: el plan no completó la misión.")

    print("=" * 50)