"""
Simulación sencilla de Proof of Capacity (PoC)
----------------------------------------------
1. PLOTTING: cada minero precalcula y guarda hashes en "disco" (su plot).
2. RETO:     cada bloque genera un reto a partir del bloque anterior.
3. DEADLINE: cada minero lee SOLO una parte de su plot (el "scoop" que
             indica el reto) y obtiene su mejor tiempo de espera.
4. GANADOR:  el menor deadline forja el bloque.
Más espacio guardado = más intentos = más probabilidad de ganar.
"""
import hashlib

SCOOPS = 8  # cada nonce se divide en 8 "scoops" (en Burstcoin son 4096)


def sha(texto):
    """Devuelve el hash SHA-256 como número entero."""
    return int(hashlib.sha256(texto.encode()).hexdigest(), 16)


class Minero:
    def __init__(self, nombre, nonces):
        self.nombre = nombre
        self.victorias = 0
        # FASE 1: PLOTTING (se hace una sola vez y se guarda en disco)
        # Cada nonce guarda SCOOPS hashes. Más nonces = más capacidad.
        self.plot = [
            [sha(f"{nombre}-{n}-{s}") % 100_000 for s in range(SCOOPS)]
            for n in range(nonces)
        ]

    def calcular_deadline(self, reto):
        # FASE 2: el reto elige qué scoop hay que leer de cada nonce
        scoop = reto % SCOOPS
        # Solo se LEE el disco (no hay cálculo pesado): se queda el menor valor
        return min(nonce[scoop] for nonce in self.plot)


def simular(mineros, num_bloques):
    cadena = [{"altura": 0, "hash": sha("genesis"), "minero": "-", "deadline": 0}]

    for altura in range(1, num_bloques + 1):
        anterior = cadena[-1]

        # El reto depende del bloque anterior (todos lo conocen)
        reto = sha(str(anterior["hash"]))

        # Cada minero calcula su deadline
        deadlines = {m.nombre: m.calcular_deadline(reto) for m in mineros}

        # Gana el que tenga el deadline más bajo
        ganador = min(mineros, key=lambda m: deadlines[m.nombre])
        ganador.victorias += 1

        bloque = {
            "altura": altura,
            "hash": sha(f"{anterior['hash']}{ganador.nombre}{deadlines[ganador.nombre]}"),
            "minero": ganador.nombre,
            "deadline": deadlines[ganador.nombre],
        }
        cadena.append(bloque)
        print(f"Bloque {altura:>3} | ganador: {ganador.nombre:<6} | deadline: {bloque['deadline']} s")

    return cadena


if __name__ == "__main__":
    mineros = [
        Minero("Alice", nonces=1000),  # mucha capacidad
        Minero("Bob", nonces=500),     # capacidad media
        Minero("Carol", nonces=100),   # poca capacidad
    ]

    print("Capacidad (nonces):", {m.nombre: len(m.plot) for m in mineros}, "\n")
    simular(mineros, num_bloques=30)

    print("\n--- Resultado final ---")
    for m in mineros:
        print(f"{m.nombre}: {m.victorias} bloques ({m.victorias / 30:.0%})")
