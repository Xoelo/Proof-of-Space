"""
Proof of Space (PoS) - versión PASO A PASO
---------------------------------------------
Usa pocos nonces para poder ver los datos de cada minero.
El programa se detiene en cada paso: pulsa Enter para avanzar.

    python proof_of_space_paso_a_paso.py          -> con pausas
    python proof_of_space_paso_a_paso.py --auto   -> sin pausas
"""
import hashlib
import sys

SCOOPS = 8        # partes en que se divide cada nonce
RANGO = 1000      # los valores guardados van de 0 a 999 (así se leen mejor)
NUM_BLOQUES = 3
PAUSAR = "--auto" not in sys.argv


# ---------- utilidades ----------
def sha(texto):
    """SHA-256 devuelto como número entero."""
    return int(hashlib.sha256(texto.encode()).hexdigest(), 16)


def corto(numero):
    """Versión abreviada de un hash para poder leerlo."""
    return hex(numero)[2:10] + "..."


def titulo(texto):
    print("\n" + "=" * 62)
    print(texto)
    print("=" * 62)


def pausa():
    if PAUSAR:
        try:
            input("\n   [Enter para continuar]")
        except EOFError:
            pass


# ---------- minero ----------
class Minero:
    def __init__(self, nombre, nonces):
        self.nombre = nombre
        self.victorias = 0
        # PLOTTING: se calcula una vez y se guarda en disco
        self.plot = [
            [sha(f"{nombre}-{n}-{s}") % RANGO for s in range(SCOOPS)]
            for n in range(nonces)
        ]

    def mostrar_plot(self, scoop_marcado=None):
        cabecera = "   nonce | " + " ".join(f"s{s:<4}" for s in range(SCOOPS))
        print(cabecera)
        for i, nonce in enumerate(self.plot):
            celdas = []
            for s, valor in enumerate(nonce):
                if s == scoop_marcado:
                    celdas.append(f"[{valor:>3}]")
                else:
                    celdas.append(f" {valor:>3} ")
            print(f"   {i:>5} | " + " ".join(celdas))

    def leer_scoop(self, scoop):
        """Lee solo el scoop pedido de cada nonce y devuelve el mejor."""
        valores = [nonce[scoop] for nonce in self.plot]
        mejor = min(valores)
        return mejor, valores.index(mejor), valores


# ---------- simulación ----------
def main():
    mineros = [
        Minero("Alice", nonces=6),   # mucha capacidad
        Minero("Bob", nonces=3),     # capacidad media
        Minero("Carol", nonces=1),   # poca capacidad
    ]

    titulo("PASO 1 - PLOTTING: cada minero llena su disco con hashes")
    print("Cada fila es un 'nonce' y cada columna (s0..s7) un 'scoop'.")
    print("Más nonces = más espacio ocupado = más valores entre los que elegir.")
    for m in mineros:
        print(f"\n {m.nombre} ({len(m.plot)} nonces):")
        m.mostrar_plot()
    pausa()

    cadena = [{"altura": 0, "hash": sha("genesis")}]
    print(f"\nBloque génesis creado. Hash: {corto(cadena[0]['hash'])}")

    for altura in range(1, NUM_BLOQUES + 1):
        anterior = cadena[-1]
        titulo(f"BLOQUE {altura}")

        # PASO 2: reto
        reto = sha(str(anterior["hash"]))
        print(f"PASO 2 - RETO\n   Se calcula a partir del hash del bloque anterior.")
        print(f"   Hash anterior : {corto(anterior['hash'])}")
        print(f"   Reto          : {corto(reto)}")
        pausa()

        # PASO 3: scoop elegido
        scoop = reto % SCOOPS
        print(f"PASO 3 - SCOOP ELEGIDO\n   reto % {SCOOPS} = {scoop}")
        print(f"   Todos los mineros deben leer la columna s{scoop} de sus nonces.")
        pausa()

        # PASO 4 y 5: lectura y deadline
        print("PASO 4 - LECTURA DEL DISCO (la columna elegida va entre [ ])")
        resultados = {}
        for m in mineros:
            mejor, idx_nonce, valores = m.leer_scoop(scoop)
            resultados[m.nombre] = mejor
            print(f"\n {m.nombre}:")
            m.mostrar_plot(scoop_marcado=scoop)
            print(f"   Valores leídos: {valores}")
            print(f"   Mejor (menor) : {mejor}  (nonce {idx_nonce})  -> DEADLINE = {mejor} s")
        pausa()

        # PASO 6: ganador
        print("PASO 5 - COMPARAR DEADLINES")
        for nombre, d in sorted(resultados.items(), key=lambda x: x[1]):
            print(f"   {nombre:<6} {d} s")
        ganador = min(mineros, key=lambda m: resultados[m.nombre])
        ganador.victorias += 1
        print(f"\n   >> Gana {ganador.nombre}: espera {resultados[ganador.nombre]} s y forja el bloque.")
        pausa()

        # PASO 7: nuevo bloque
        nuevo_hash = sha(f"{anterior['hash']}{ganador.nombre}{resultados[ganador.nombre]}")
        cadena.append({"altura": altura, "hash": nuevo_hash})
        print("PASO 6 - BLOQUE FORJADO")
        print(f"   Altura: {altura} | Minero: {ganador.nombre} | Hash: {corto(nuevo_hash)}")
        print(f"   Este hash será la base del reto del siguiente bloque.")
        pausa()

    titulo("RESULTADO FINAL")
    for m in mineros:
        print(f"   {m.nombre:<6} capacidad: {len(m.plot)} nonces | bloques ganados: {m.victorias}")
    print("\nCon pocos bloques el azar pesa mucho; con muchos, los bloques ganados")
    print("se reparten en proporción a la capacidad de cada minero.")


if __name__ == "__main__":
    main()
