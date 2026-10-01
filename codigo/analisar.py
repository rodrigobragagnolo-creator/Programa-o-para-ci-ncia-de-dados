"""Valida os CSVs e reproduz as tabelas e figuras da análise.

Execução: python codigo/analisar.py (a partir de entrega_benchmark).
Não modifica os dados de entrada e não exclui observações.
"""
from pathlib import Path
import json
import re
import hashlib
import platform
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OPS = ['alloc_ms', 'write_ms', 'read_ms', 'free_ms']
LABELS = dict(zip(OPS, ['Alocação', 'Escrita', 'Leitura', 'Liberação']))
COLS = ['bloco_MB', 'teste'] + OPS
BLOCKS = list(range(100, 1001, 100))
COLORS = {'Linux': '#236078', 'Windows': '#bd7136'}

def validar(path):
    df = pd.read_csv(path)
    if list(df.columns) != COLS:
        raise ValueError(f'{path.name}: cabeçalho inesperado')
    if len(df) != 1000 or df.isna().any().any():
        raise ValueError(f'{path.name}: contagem ou células ausentes inválidas')
    for col in COLS:
        df[col] = pd.to_numeric(df[col], errors='raise')
        if not np.isfinite(df[col]).all():
            raise ValueError(f'{path.name}: valores não finitos')
    for col in ['bloco_MB', 'teste']:
        if (df[col] % 1 != 0).any():
            raise ValueError(f'{path.name}: {col} deve conter inteiros')
        df[col] = df[col].astype(int)
    expected = {(b, t) for b in BLOCKS for t in range(1, 101)}
    actual = set(map(tuple, df[['bloco_MB', 'teste']].to_numpy()))
    if actual != expected or df.duplicated(['bloco_MB', 'teste']).any():
        raise ValueError(f'{path.name}: combinações de bloco e teste inválidas')
    if (df[OPS] < 0).any().any():
        raise ValueError(f'{path.name}: tempos negativos')
    df['total_ms'] = df[OPS].sum(axis=1)
    return df

def main():
    for p in ['tabelas', 'graficos']:
        (ROOT / p).mkdir(exist_ok=True)
    dados, audit, stats = {}, [], []
    for sistema in COLORS:
        path = ROOT / 'dados' / f'resultados_{sistema.lower()}.csv'
        df = validar(path)
        dados[sistema] = df
        txt = (ROOT / 'dados' / f'tempo_total_{sistema.lower()}.txt').read_text()
        if f'Sistema operacional: {sistema}' not in txt:
            raise ValueError('Identificação incompatível no TXT')
        total_txt = float(re.search(r'Tempo total em ms:\s*([\d.]+)', txt)[1])
        audit.append({'sistema': sistema, 'registros': len(df), 'validacao': 'aprovada',
                      'soma_operacoes_ms': df.total_ms.sum(), 'tempo_txt_ms': total_txt,
                      'diferenca_txt_csv_ms': total_txt - df.total_ms.sum(),
                      'sha256_csv': hashlib.sha256(path.read_bytes()).hexdigest()})
        for bloco, grupo in df.groupby('bloco_MB'):
            for op in OPS + ['total_ms']:
                s = grupo[op]
                q1, q3 = s.quantile([.25, .75])
                iqr = q3 - q1
                stats.append({'sistema': sistema, 'bloco_MB': bloco, 'operacao': op,
                              'n': len(s), 'media_ms': s.mean(), 'mediana_ms': s.median(),
                              'desvio_padrao_ms': s.std(ddof=1), 'cv_pct': 100*s.std(ddof=1)/s.mean(),
                              'min_ms': s.min(), 'max_ms': s.max(), 'q1_ms': q1, 'q3_ms': q3,
                              'p95_ms': s.quantile(.95),
                              'sinalizados_iqr': int(((s < q1-1.5*iqr) | (s > q3+1.5*iqr)).sum())})
    estat = pd.DataFrame(stats)
    estat.to_csv(ROOT/'tabelas/estatisticas_por_bloco.csv', index=False, float_format='%.6f')
    pd.DataFrame(audit).to_csv(ROOT/'tabelas/validacao.csv', index=False, float_format='%.6f')
    comparisons = []
    for bloco in BLOCKS:
        for op in OPS + ['total_ms']:
            l = estat.query('sistema == "Linux" and bloco_MB == @bloco and operacao == @op').iloc[0]
            w = estat.query('sistema == "Windows" and bloco_MB == @bloco and operacao == @op').iloc[0]
            comparisons.append({'bloco_MB': bloco, 'operacao': op, 'linux_media_ms': l.media_ms,
                                'windows_media_ms': w.media_ms, 'linux_dp_ms': l.desvio_padrao_ms,
                                'windows_dp_ms': w.desvio_padrao_ms,
                                'reducao_linux_vs_windows_pct': 100*(w.media_ms-l.media_ms)/w.media_ms,
                                'menor_media': 'Linux' if l.media_ms < w.media_ms else 'Windows' if w.media_ms < l.media_ms else 'Empate'})
    comp = pd.DataFrame(comparisons)
    comp.to_csv(ROOT/'tabelas/comparacao_por_bloco.csv', index=False, float_format='%.6f')
    glob = []
    for op in OPS + ['total_ms']:
        l, w = dados['Linux'][op].mean(), dados['Windows'][op].mean()
        glob.append({'operacao': op, 'linux_media_ms': l, 'windows_media_ms': w,
                     'reducao_linux_vs_windows_pct': 100*(w-l)/w,
                     'menor_media': 'Linux' if l < w else 'Windows'})
    pd.DataFrame(glob).to_csv(ROOT/'tabelas/resumo_global.csv', index=False, float_format='%.6f')
    combined = pd.concat([d.assign(sistema=s) for s,d in dados.items()], ignore_index=True)
    combined.to_csv(ROOT/'tabelas/dados_consolidados.csv', index=False, float_format='%.6f')
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 2, figsize=(8, 5.1), constrained_layout=True)
    for op, ax in zip(OPS, axes.flat):
        for sistema, color in COLORS.items():
            part = estat.query('sistema == @sistema and operacao == @op')
            ax.errorbar(part.bloco_MB, part.media_ms, yerr=part.desvio_padrao_ms,
                        label=sistema, color=color, marker='o', markersize=3, capsize=2)
        ax.set(title=LABELS[op], xlabel='Bloco (MB conforme CSV)', ylabel='Tempo (ms)')
        ax.grid(alpha=.18)
        ax.legend(frameon=False)
    fig.savefig(ROOT/'graficos/operacoes_por_bloco.png', dpi=220)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
    for sistema, color in COLORS.items():
        part = estat.query('sistema == @sistema and operacao == "total_ms"')
        ax.errorbar(part.bloco_MB, part.media_ms, yerr=part.desvio_padrao_ms,
                    label=sistema, color=color, marker='o', capsize=3)
    ax.set(xlabel='Bloco (MB conforme CSV)', ylabel='Soma média por teste (ms)', title='Alocação + escrita + leitura + liberação')
    ax.grid(alpha=.18); ax.legend(frameon=False)
    fig.savefig(ROOT/'graficos/total_por_bloco.png', dpi=220); plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(8, 5.1), constrained_layout=True)
    for op, ax in zip(OPS, axes.flat):
        for sistema, color in COLORS.items():
            df = dados[sistema]
            normalized = df[op] / df.bloco_MB
            ax.plot(np.arange(1, len(df)+1), normalized, color=color, linewidth=.6, label=sistema)
        ax.set(title=LABELS[op], xlabel='Posição no arquivo', ylabel='Tempo por MB (ms/MB)')
        ax.legend(frameon=False); ax.grid(alpha=.18)
    fig.savefig(ROOT/'graficos/variacao_na_sequencia.png', dpi=220); plt.close(fig)
    (ROOT/'tabelas/ambiente_analise.json').write_text(json.dumps({
        'python':sys.version, 'plataforma':platform.platform(),
        'numpy':np.__version__, 'pandas':pd.__version__, 'matplotlib':matplotlib.__version__,
        'nota':'Ambiente de análise; não é o computador da coleta.'}, ensure_ascii=False, indent=2))
    print(pd.DataFrame(glob).to_string(index=False))
    print(comp.query('operacao == "total_ms"').to_string(index=False))
    print('Validação aprovada para os dois arquivos. Nenhuma observação removida.')

if __name__ == '__main__':
    main()
