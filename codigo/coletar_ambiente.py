"""Registra o ambiente da próxima execução, sem executar o benchmark."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time

def command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    except Exception as exc:
        return {'erro': str(exc)}

source = Path(__file__).with_name('microbenchmark.py')
clock = time.get_clock_info('perf_counter')
info = {
    'data_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'sistema': platform.system(), 'versao': platform.version(),
    'arquitetura_so': platform.machine(), 'python': sys.version,
    'implementacao_python': platform.python_implementation(),
    'arquitetura_python_bits': struct.calcsize('P')*8,
    'processador': platform.processor(), 'cpus_logicas': os.cpu_count(),
    'relogio': {'implementacao': clock.implementation, 'resolucao_s': clock.resolution,
                'monotonico': clock.monotonic},
    'sha256_microbenchmark': hashlib.sha256(source.read_bytes()).hexdigest(),
    'itens_a_registrar_manualmente': ['alimentação elétrica', 'perfil de energia',
          'aplicações abertas', 'temperatura', 'intervalo de estabilização', 'data e ordem das execuções']
}
if platform.system() == 'Linux':
    for name in ['os-release']:
        p = Path('/etc')/name
        if p.exists(): info[name] = p.read_text()
    p = Path('/proc/meminfo')
    if p.exists(): info['memoria'] = p.read_text()
    info['cpu'] = command(['lscpu'])
    info['kernel'] = command(['uname', '-r'])
elif platform.system() == 'Windows':
    info['hardware'] = command(['powershell', '-NoProfile', '-Command',
        '$c=Get-CimInstance Win32_ComputerSystem; $p=Get-CimInstance Win32_Processor; '
        '$o=Get-CimInstance Win32_OperatingSystem; '
        '[pscustomobject]@{RAM_bytes=$c.TotalPhysicalMemory;CPU=$p.Name;'
        'SO=$o.Caption;Build=$o.BuildNumber;RAM_livre_KB=$o.FreePhysicalMemory} | ConvertTo-Json'])
out = Path(f'ambiente_{platform.system().lower()}.json')
out.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Arquivo criado: {out}')
