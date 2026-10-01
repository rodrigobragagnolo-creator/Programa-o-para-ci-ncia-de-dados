import time
import csv
import platform


# ============================================================
# CONFIGURAÇÕES DO EXPERIMENTO
# ============================================================

TAMANHOS_MB = range(100, 1001, 100)
REPETICOES = 100

sistema = platform.system()

if sistema == "Windows":
    arquivo_csv = "resultados_windows.csv"
elif sistema == "Linux":
    arquivo_csv = "resultados_linux.csv"
else:
    arquivo_csv = "resultados_outro.csv"

arquivo_tempo_total = f"tempo_total_{sistema.lower()}.txt"


print("=" * 60)
print("MICROBENCHMARK DE OPERAÇÕES DE MEMÓRIA")
print("=" * 60)

print(f"Sistema operacional: {sistema}")
print(f"Arquivo de resultados: {arquivo_csv}")
print(f"Repetições por tamanho: {REPETICOES}")
print("Tamanhos: 100 MB até 1000 MB")
print("=" * 60)


# ============================================================
# INÍCIO DO TEMPO TOTAL DO EXPERIMENTO
# ============================================================

inicio_experimento = time.perf_counter_ns()


# ============================================================
# CRIAÇÃO DO CSV
# ============================================================

with open(
    arquivo_csv,
    "w",
    encoding="utf-8",
    newline=""
) as arquivo:

    escritor = csv.writer(arquivo)

    # Cabeçalho definido no protocolo
    escritor.writerow([
        "bloco_MB",
        "teste",
        "alloc_ms",
        "write_ms",
        "read_ms",
        "free_ms"
    ])


    # ========================================================
    # TAMANHOS DE 100 MB ATÉ 1000 MB
    # ========================================================

    for mb in TAMANHOS_MB:

        bloco_bytes = mb * 1024 * 1024

        print()
        print(f"Testando bloco de {mb} MB...")

        # O padrão é criado ANTES da medição da escrita.
        # Assim, medimos somente a operação de escrita.
        padrao = b'\xAA' * bloco_bytes


        # ====================================================
        # 100 REPETIÇÕES PARA CADA TAMANHO
        # ====================================================

        for teste in range(1, REPETICOES + 1):


            # ------------------------------------------------
            # 1. ALOCAÇÃO
            # ------------------------------------------------

            t0 = time.perf_counter_ns()

            bloco = bytearray(bloco_bytes)

            t1 = time.perf_counter_ns()

            alloc_ms = (t1 - t0) / 1_000_000


            # ------------------------------------------------
            # 2. ESCRITA
            # ------------------------------------------------

            t2 = time.perf_counter_ns()

            bloco[:] = padrao

            t3 = time.perf_counter_ns()

            write_ms = (t3 - t2) / 1_000_000


            # ------------------------------------------------
            # 3. LEITURA
            # ------------------------------------------------

            t4 = time.perf_counter_ns()

            soma = sum(bloco)

            t5 = time.perf_counter_ns()

            read_ms = (t5 - t4) / 1_000_000


            # ------------------------------------------------
            # 4. LIBERAÇÃO
            # ------------------------------------------------

            t6 = time.perf_counter_ns()

            bloco.clear()
            del bloco

            t7 = time.perf_counter_ns()

            free_ms = (t7 - t6) / 1_000_000


            # ------------------------------------------------
            # GRAVAR UMA NOVA LINHA NO CSV
            # ------------------------------------------------

            escritor.writerow([
                mb,
                teste,
                f"{alloc_ms:.6f}",
                f"{write_ms:.6f}",
                f"{read_ms:.6f}",
                f"{free_ms:.6f}"
            ])


            # Apenas para acompanhar o progresso.
            # Este print ocorre FORA das medições.
            print(
                f"{mb} MB | "
                f"Teste {teste:03d}/{REPETICOES} | "
                f"Alloc: {alloc_ms:.3f} ms | "
                f"Write: {write_ms:.3f} ms | "
                f"Read: {read_ms:.3f} ms | "
                f"Free: {free_ms:.3f} ms"
            )


        # Libera também o padrão antes de passar
        # para o próximo tamanho.
        del padrao


# ============================================================
# FIM DO TEMPO TOTAL DO EXPERIMENTO
# ============================================================

fim_experimento = time.perf_counter_ns()

tempo_total_ms = (
    fim_experimento - inicio_experimento
) / 1_000_000

tempo_total_s = tempo_total_ms / 1000
tempo_total_min = tempo_total_s / 60


# ============================================================
# SALVAR TEMPO TOTAL EM ARQUIVO SEPARADO
# ============================================================

with open(
    arquivo_tempo_total,
    "w",
    encoding="utf-8"
) as arquivo:

    arquivo.write(f"Sistema operacional: {sistema}\n")
    arquivo.write(f"Tempo total em ms: {tempo_total_ms:.6f}\n")
    arquivo.write(f"Tempo total em segundos: {tempo_total_s:.6f}\n")
    arquivo.write(f"Tempo total em minutos: {tempo_total_min:.6f}\n")


# ============================================================
# RESULTADO FINAL
# ============================================================

print()
print("=" * 60)
print("EXPERIMENTO FINALIZADO")
print("=" * 60)

print(f"CSV criado: {arquivo_csv}")
print("Total de registros: 1000")

print()
print(f"Tempo total: {tempo_total_ms:.3f} ms")
print(f"Tempo total: {tempo_total_s:.3f} segundos")
print(f"Tempo total: {tempo_total_min:.2f} minutos")

print()
print(f"Tempo total salvo em: {arquivo_tempo_total}")