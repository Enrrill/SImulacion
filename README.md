* * INTALACION DEL PROGRAMA * * 

El programa no se instala en la computadora directamente, se ejecutan los archivos desde una terminal, para ver esto vaya directamente al apartado de _COMANDOS DE EJECUCION_



* * COMPORTAMIENTO * * 

+ Simula el comportamiento y la propagacion de una epidemia, cuenta con distintos parametros para manipular la simulacion y poder ver distintos escenarios

+ Cuenta con una grafica que muestra el comportamiento de los individuos durante la empidemia, mostrando valores como los infectados, muertos, inmunes y sanos

+ Hay un contador de dias para aproximarlo mas a un caso real

+ Al terminar la simulacion, se creara un archivo excel que guardara los datos, parametros y configuraciones de la simulacion, mostrandolos luego en una grafica



* * PARAMETROS MANIPULABLES * *

+ Población + = la cantidad de individuos puede ser cambiada a conveniencia
+ Velocidad de la simulacion + = que tan rapido avanza la simulacion
+ Radio de infeccion + = que tan cerca debe estar un individuo de otro para transmitir la enfermedad
+ Probabilidad (Prob) de infeccion + = que tan contagiosa y agresiva es la enfermedad para los individuos
+ Probabilidad (Prob) de inmunidad + = que tanto puede resistir un individuo la agresividad de la enfermedad
+ Tiempo de vida + = para calcular la muerte de un individuo se utiliza la Prob de inmunidad y el tiempo de vida, si la inmunidad es alta pero el tiempo de vida es corto la Prob de que el individuo muera es mas alta, caso contrario ocurre si la inmunidad es baja pero el tiempo de vida es alto (el individuo puede permanecer mas tiempo infectado antes de sanar o morir).

* * PARAMETROS FIJOS * *

Hay ciertos escenarios predeterminados que se pueden probar, teniendo en cuenta empidemias de la vida real, estos simulan lo que las enfermedades fueron en su tiemp.

* * COMANDOS DE EJECUCION * *

para ejecutar el programa solo debe abrir una consola en la carpeta donde se encuentren los archivos y ejecutar los siguientes comandos

+ Iniciar simulacion: 

python main.py

+ Ver grafica de las simulaciones Previas:

python analiticas.py

