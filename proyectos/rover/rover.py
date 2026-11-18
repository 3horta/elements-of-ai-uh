# . terreno normal
# * terreno pedregoso
# A superficie arenada
# D superficie con dunas
# O obstáculo
# M lugar con muestras
# R rover 
# C zona de comunicación 

import heapq
import random
class Rover:
    def __init__(self,x,y,energy,memory):
        self.x=x
        self.y=y
        self.battery=energy
        self.memory=memory
        self.max_memory=memory
        self.max_energy=energy
        self.time=0
        self.collected_samples = set() 
        self.cost=0
        
    @property   
    def posicion(self):
        print(f"Posición: {self.x},{self.y}")
        return (self.x,self.y)
    
    @property
    def energy(self):
        print(f"Energía restante: {self.battery}")
        return self.battery
    
    @property
    def space_of_memory(self):
        print(f"Memoria restante: {self.memory}")
        return self.memory
    
    @property
    def actual_time(self):
        print(f"Tiempo transcurrido: {self.time}")
        return self.time
    
    @property
    def actual_cost(self):        
        print(f"Costo actual: {self.cost}")
        return self.cost
    
class Entorno:
    def __init__(self,size_x=15,size_y=15,x=0,y=0,energy=100,memory=50,base=(0,0),seed=1234):
        self.size_x=size_x
        self.size_y=size_y
        self.random = random.Random(seed)
        self.base=base
        self.rover=Rover(x,y,energy,memory)
        self.map=self.generate_valid_map(size_x,size_y,seed)

    def generate_valid_map(self,size_x,size_y,seed,max_intentos=100):
        """Genera mapas con la semilla hasta obtener uno resoluble"""
        for _ in range(max_intentos):
            mapa=self.minimal_conditions(self.generate_map(size_x,size_y,seed))
            if self.is_solvable(mapa):
                return mapa
        raise ValueError("No se pudo generar un mapa resoluble con estos parámetros")

    def generate_map(self,size_x,size_y,seed):
        """Genera el mapa aleatoriamente con los obstáculos"""
        terrain=['.',"*", 'A', 'D', 'O','M','C']
        weights = [0.5,0.3 ,0.25, 0.15, 0.1,0.2,0.1]
        # return [[random.choices(terrain, weights)[0] for _ in range(size_x)] for _ in range(size_y)]
        return [[self.random.choices(terrain, weights)[0] for _ in range(size_x)] for _ in range(size_y)]

    def minimal_conditions(self, mapa):
        """Comprueba que el mapa cumpla con las condiciones básicas"""

        bx, by = self.base

        mapa[bx][by] = "."
        rx, ry = self.rover.x, self.rover.y
        mapa[rx][ry] = "."

        # Solo casillas sin obstáculo, muestra ni comunicación, para no pisar nada
        posiciones_libres = []
        for i in range(self.size_x):
            for j in range(self.size_y):
                if (i, j) == (bx, by) or (i, j) == (rx, ry):
                    continue
                if mapa[i][j] in ("O", "M", "C"):
                    continue
                posiciones_libres.append((i, j))

        if not any("M" in fila for fila in mapa):
            # sample elige dos casillas distintas
            for x, y in self.random.sample(posiciones_libres, 2):
                mapa[x][y] = "M"
                posiciones_libres.remove((x, y))

        if not any("C" in fila for fila in mapa):

            posicion = self.random.choice(posiciones_libres)

            x, y = posicion
            mapa[x][y] = "C"
        return mapa

    def energy_costs(self, mapa, origen, inverso=False):
        """Energía mínima para llegar desde origen a cada casilla (Dijkstra).
        Con inverso=True da la energía para llegar desde cada casilla hasta origen."""
        dist = {origen: 0}
        cola = [(0, origen)]
        while cola:
            d, (x, y) = heapq.heappop(cola)
            if d > dist[(x, y)]:
                continue
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if (dx, dy) == (0, 0) or not (0 <= nx < self.size_x and 0 <= ny < self.size_y):
                        continue
                    if mapa[nx][ny] == "O":
                        continue
                    # Moverse cuesta según la casilla a la que se entra
                    entrada = mapa[x][y] if inverso else mapa[nx][ny]
                    nd = d + self.cost_mov(entrada)[0]
                    if nd < dist.get((nx, ny), float("inf")):
                        dist[(nx, ny)] = nd
                        heapq.heappush(cola, (nd, (nx, ny)))
        return dist

    def is_solvable(self, mapa):
        """Comprueba que la misión se pueda completar con un viaje por muestra:
        llegar a la base, y desde ella ir a cada M y volver, e ir a una C, transmitir
        y volver, sin pasar de la batería máxima. Es una condición suficiente."""
        bateria = self.rover.max_energy
        if self.rover.max_memory < 15:
            return False

        desde_base = self.energy_costs(mapa, self.base)
        hacia_base = self.energy_costs(mapa, self.base, inverso=True)
        inicio = (self.rover.x, self.rover.y)
        if hacia_base.get(inicio, float("inf")) > bateria:
            return False

        def ida_y_vuelta(destino, gasto):
            if destino not in desde_base:
                return float("inf")
            return desde_base[destino] + gasto + hacia_base[destino]

        muestras = [(i, j) for i in range(self.size_x) for j in range(self.size_y) if mapa[i][j] == "M"]
        comunicaciones = [(i, j) for i in range(self.size_x) for j in range(self.size_y) if mapa[i][j] == "C"]

        # Recolectar gasta 8 de energía; transmitir una muestra, int(15/3) = 5
        if any(ida_y_vuelta(m, 8) > bateria for m in muestras):
            return False
        return any(ida_y_vuelta(c, 5) <= bateria for c in comunicaciones)
    
    def show_map(self):
        """ Mostrar el mapa"""

        for i in range(self.size_x):
            fila=""
            for j in range(self.size_y):
                if (i,j)==(self.rover.x,self.rover.y):
                    fila += " R "
                elif (i, j) == self.base:
                    fila += " B "
                else:
                    fila += " " + self.map[i][j] + " "
            print(fila)
    
    def possible_actions(self):
        """Listado de posibles acciones"""
        possibles=[]
        actions = [(-1, -1),(-1, 0),(-1, 1),(0, -1),(0, 1),(1, -1),(1, 0),(1, 1)]
        for dx,dy in actions:
            nx = self.rover.x + dx
            ny = self.rover.y + dy
            
            if not (0 <= nx < self.size_x and 0 <= ny < self.size_y):
                continue
            
            terrain = self.map[nx][ny]
            if terrain== "O":
                continue
            
            cost = self.cost_mov(terrain)[0]
            if cost > self.rover.battery:
                continue

            possibles.append((dx, dy))

        return possibles       
        
    def cost_mov(self, posicion):
        """Coste de moverse """
        if posicion == '.': return 1,2
        if posicion == 'A': return 2,6
        if posicion == 'D': return 3,8
        if posicion == '*': return 5,10   
        if posicion == 'M': return 10,1
        if posicion == 'C': return 10,1             
        else: return False,False
        
    def mov(self,dx,dy):
        """Realiza la acción de moverse"""
        nx = self.rover.x + dx
        ny = self.rover.y + dy
        if not (0 <= nx < self.size_x and 0 <= ny < self.size_y):
            print("Movimiento inválido: fuera del mapa")
            return False
        
        posicion = self.map[nx][ny]
        if posicion == "O":
            print("Movimiento inválido: hay un obstáculo")
            return False

        cost_battery, cost_time = self.cost_mov(posicion)[0], self.cost_mov(posicion)[1]
        if self.rover.battery < cost_battery:
            print("Movimiento inválido: batería insuficiente")
            return False
    
        self.rover.x += dx
        self.rover.y += dy
        self.rover.battery -= cost_battery
        self.rover.time += cost_time
        self.rover.cost += cost_battery + cost_time
        return True
            
    def collect_samples(self):
        """Ejecuta la acción de recolectar muestras."""

        posicion = self.map[self.rover.x][self.rover.y]
        if posicion == "M":
            if self.rover.battery < 8:
                return "No tiene suficiente energía para recolectar la muestra"
            elif self.rover.memory < 15:
                return "No tiene suficiente memoria para recolectar la muestra"
            self.rover.battery -= 8
            self.rover.memory -= 15
            self.rover.time += 8
            self.map[self.rover.x][self.rover.y]="."
            self.rover.cost += 15+8
            self.rover.collected_samples.add((self.rover.x, self.rover.y))
            
    def charge(self):
        """Recarga la batería del rover si está en la base."""

        posicion = self.rover.posicion
        if posicion == self.base:
            if self.rover.battery == self.rover.max_energy:
                return "La batería ya está completa"
            energy=self.rover.max_energy-self.rover.battery
            self.rover.battery = self.rover.max_energy
            self.rover.time += int(energy/2)
            self.rover.cost +=int(energy/2)
            return True
        return "No estás en la base, no puedes recargar la batería"
        
    def transmit_information(self):
        """Ejecuta la acción de dejar muestras y transmitir información."""

        posicion = self.map[self.rover.x][self.rover.y]
        if posicion == "C":
            space = self.rover.max_memory - self.rover.memory
            if (space/3) > self.rover.battery :
                return "No tiene suficiente energía para transmitir la información recolectada"
            self.rover.memory = self.rover.max_memory
            self.rover.time += int(space/3)
            self.rover.battery -= int(space/3)
            self.rover.cost += int(space/3) + int(space/3)
            return
        return "No estás en un punto de comunicación"
    
    def is_objective(self):
        """Define el estado objetivo"""
        if self.rover.posicion != self.base:
            return False
        for fila in self.map:
            if "M" in fila:
                return False
        if self.rover.max_memory != self.rover.memory:
            return False
        return True
