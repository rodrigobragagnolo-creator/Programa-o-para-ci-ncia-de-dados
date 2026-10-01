# Comparação de operações de memória no Windows e no Linux

Autores: Rodrigo Pires Bragagnolo e Alexandre Mayer da Rosa.
Grupo: Senhores Supremos do Universo.

## Resultado

Nos dados fornecidos, o Linux apresentou soma das operações 3,45% menor e menor média do ciclo completo em todos os tamanhos. O Windows apresentou menores médias de alocação e escrita; o Linux, de leitura e liberação. A recomendação do Linux aplica-se ao ciclo deste microbenchmark, no hardware e nas condições declaradas. Não é uma recomendação geral para toda aplicação.

## Conteúdo

- `documentos/relatorio_benchmark.docx`: resumo expandido editável, com as seções do template.
- `documentos/ficha_de_pre_registro_experimental.docx`: análise do problema, hipóteses e auditoria do protocolo.
- `codigo/microbenchmark.py`: cópia integral, sem alterações, do código recebido em `codigo.txt`.
- `codigo/analisar.py`: validação, estatísticas e gráficos reproduzíveis.
- `codigo/coletar_ambiente.py`: coleta de metadados para novas execuções.
- `dados/`: dois CSVs e dois TXT originais, preservados.
- `tabelas/`: estatísticas por bloco, comparação, resumo global, dados consolidados e validação.
- `graficos/`: médias e desvios padrão, ciclo completo e variação na sequência.
- `configuracoes_ambientes.md`: configurações informadas e informações ainda não registradas.
- `requirements.txt`: versões usadas na análise.

## Reproduzir a análise dos dados existentes

Use Python com suporte às versões em `requirements.txt`. Na pasta que contém este README:

```bash
python -m venv .venv
```

Ative no Windows com `.venv\Scripts\activate` ou no Linux com `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
python codigo/analisar.py
```

Em instalações Linux nas quais `python` não existe, utilize `python3` para criar o ambiente. O script resolve os caminhos a partir de sua própria localização. Ele reescreve somente tabelas e gráficos e não altera os arquivos em `dados/`.

## Reproduzir a coleta

O código original usa apenas a biblioteca padrão. A versão declarada no protocolo foi Python 3.14.3 nos dois sistemas; confirmar a versão e a arquitetura antes de repetir. Use o mesmo arquivo `microbenchmark.py` e compare seu SHA-256. Use dual boot no mesmo computador e execute apenas um sistema por vez, conforme protocolo.

Crie uma pasta nova para cada sessão, fora de `dados/`, por exemplo `execucoes/windows_sessao_01`. A partir dessa pasta, execute os scripts com seus caminhos completos:

```bash
python /caminho/entrega_benchmark/codigo/coletar_ambiente.py
python /caminho/entrega_benchmark/codigo/microbenchmark.py
```

No Windows, use caminhos locais correspondentes, entre aspas quando houver espaços. Ambos os scripts escrevem no diretório atual. O microbenchmark sobrescreve arquivos de mesmo nome; uma pasta nova preserva as sessões anteriores. Os resultados serão `resultados_windows.csv` e `tempo_total_windows.txt`, ou os equivalentes Linux. Antes de analisar uma nova sessão, faça uma cópia da entrega e substitua nela os quatro arquivos em `dados/`.

O protocolo registra Windows primeiro e Linux segundo, blocos de 100 a 1000, incremento de 100 e 100 repetições. Feche aplicações desnecessárias. Registre build/kernel, arquitetura do Python, RAM livre, alimentação, perfil de energia, temperatura e processos ativos. A ficha menciona “100 interações” para estabilização, mas o código não implementa aquecimento separado: todas as 100 repetições por bloco entram no CSV. Não afirme que houve aquecimento sem evidência adicional. Para nova coleta, defina e registre o procedimento antes de observar os resultados. Se alterar o código para aquecimento ou qualquer outra finalidade, mantenha uma versão separada e execute a mesma versão em ambos os sistemas.

## O que o código mede

O campo `bloco_MB` representa MiB: `mb * 1024 * 1024` bytes. Cada teste executa `bytearray(n)`, `bloco[:] = padrao`, `sum(bloco)` e `bloco.clear(); del bloco`, nessa ordem. Alocação inclui a inicialização do bytearray com zeros. Escrita mede atribuição por fatia de um padrão pré-criado. Leitura inclui a soma dos bytes pelo Python. Liberação mede a limpeza e a remoção da referência; não comprova liberação imediata de toda a memória física pelo sistema.

O padrão também ocupa memória e pode haver alocações temporárias. O tamanho do bloco não representa o pico total do processo. O valor calculado em `soma` não é verificado pelo código original. Para este padrão, o valor esperado seria `170 * bloco_bytes`; inserir uma verificação mudaria a versão do código e exigiria nova coleta comparável.

O relógio é `perf_counter_ns`; intervalos são convertidos para milissegundos. Impressão e escrita do CSV ficam fora dos quatro intervalos. O TXT mede a duração total da sessão e inclui preparação de padrões, saída no terminal e gravação do CSV. Por isso, ele não coincide com a soma dos tempos de operações.

## Análise e limitações

Validação: cabeçalho, 1000 registros, combinações exatas de bloco e teste, inteiros nos identificadores, valores numéricos finitos não negativos, ausência de vazios e duplicidades. O sistema é atribuído pela origem do arquivo, pois não há uma coluna de sistema no CSV. O nome do arquivo e o TXT são compatíveis, mas não comprovam a origem independentemente.

Calculam-se média, mediana, desvio padrão amostral (`ddof=1`), CV, mínimo, máximo, quartis, percentil 95 e sinalização por 1,5 IQR. Nenhum dado é removido. Os gráficos usam média ± um desvio padrão, não intervalo de confiança. A comparação percentual usa `(Windows - Linux) / Windows * 100`; valores positivos indicam menor tempo no Linux. O tempo do ciclo é primeiro somado em cada linha; só depois são calculadas média e dispersão. Há igual quantidade de testes de cada tamanho, dando peso igual aos dez blocos na média global.

Há um pico de 10827,3737 ms no ciclo do Windows, bloco 900, teste 60. O ciclo médio desse bloco é 2680,5033 ms com desvio padrão de 854,6178 ms, contra 2483,3261 ± 11,1493 ms no Linux. As medianas desse bloco são 2553,5883 e 2477,8737 ms, respectivamente. As medianas do ciclo favorecem o Linux nos dez tamanhos.

O conjunto contém uma sessão por sistema. As repetições internas não substituem sessões independentes; não há evidência para atribuir o pico a um serviço, temperatura ou paginação. Ordem fixa, caches, alocador, runtime Python e estado do sistema podem influenciar a comparação. Não foram feitos testes de significância ou alegações de superioridade universal.

## Revisão antes da submissão

Confirmar evento e curso/afiliação dos autores, não informados nos anexos. Confirmar arquitetura do Python, build do Windows, kernel do Fedora, data da coleta e controle efetivo de energia, processos e estabilização. As configurações do relatório foram transcritas da ficha, não medidas neste ambiente de análise. A ficha complementar é retrospectiva e não substitui nem altera o pré-registro original datado de 14/09/2026.
