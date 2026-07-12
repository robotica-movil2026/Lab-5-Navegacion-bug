
**Lab-5-Navegacion-bug**  
**Marco teórico.**  
1. Mencionar dos características de:  
- **Navegación planeada:**  
- Requiere de un mapeo del entorno, y reconocer su propia pose en el mismo, con lo cual traza una ruta con algoritmos como el A* o Dijkstra. *Al depender de un mapa trazado, cualquier cambio en el mismo puede arruinar el movimiento planeado a menos de que se haga un SLAM y replantear la ruta*  
- El algoritmo de respuesta es estatico y no presenta cambios al momento de encontrar cambios imprevistos. *En caso de modificar el mapa, el robot actuara de la forma planeada, sin importar que ya no pueda avanzar*  
- **Navegación basada en comportamientos:**  
- Una tarea de navegación compleja se descompone en varios comportamientos simples, con una maquina de estados que contempla el cambio constante entre ellos. *Permite al robot actuar de forma inteligente y evitar obstaculos moviles e inesperados*  
- No requiere necesariamente de un mapeo, pero si de una definición clara de la meta y el origen, conociendo en todo momento la relación del robot con la meta. *Requiere de mecanismos de sensorica complejos, que incluyen la aplicación de balizas o elementos parecidos*  
2. Investigaciones y robots desarrollados por:  
- **Rodney Brooks:**  
   
 Pionero en robotica con un enfoque en movimiento *Basado en comportamientos*,  
- Mark Tidlen  
3. Tres algoritmos de planeación de rutas para espaciós con obstaculos  
4. Descripción de  
- **Bug 0:**  
- **Bug 1:**  
- **Bug 2:**  
5. Al menos un algoritmo para la resolución de laberintos.  
**Evitar obstaculos:**  
Con uno de los algoritmos bug, hacer un recorrido entre dos puntos, evitando dos o mas obstaculos.  
- El distanciamiento debe de ser suficiente para que el ev3 pueda sortear los obstaculos  
- Se debe trazar una linea recta entre el origen y el final  
**Superar laberintos**  
a
