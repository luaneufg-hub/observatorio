# População residente por município, Censo 2022 (IBGE/SIDRA, tabela 4709, variável 93), para a densidade empresarial.
# Baixar: https://apisidra.ibge.gov.br/values/t/4709/n6/all/v/93/p/2022 (XML ou JSON)
# Saída: public/dados/ibge/populacao-municipio.json → { cod: pessoas }
#        lib/dados/retratos/populacao-uf.json        → { UF: pessoas } (soma dos municípios)
# Uso: python3 scripts/retrato-populacao.py <arquivo.xml|json>
import sys, json, re
arq = sys.argv[1]
txt = open(arq, encoding='utf-8').read()
mun = {}
if txt.lstrip().startswith('['):
    for r in json.loads(txt)[1:]:
        if r.get('V', '').isdigit(): mun[r['D1C']] = int(r['V'])
else:
    for cod, v in re.findall(r'<D1C>(\d{7})</D1C>.*?<V>(\d+)</V>', txt, flags=re.S):
        mun[cod] = int(v)
json.dump({'fonte': 'IBGE · Censo Demográfico 2022 · população residente (SIDRA, tabela 4709)', 'ano': 2022, 'mun': mun},
          open('public/dados/ibge/populacao-municipio.json', 'w'), separators=(',', ':'))
print(len(mun), 'municípios; total', sum(mun.values()))
UF = {11:'RO',12:'AC',13:'AM',14:'RR',15:'PA',16:'AP',17:'TO',21:'MA',22:'PI',23:'CE',24:'RN',25:'PB',26:'PE',27:'AL',28:'SE',29:'BA',
      31:'MG',32:'ES',33:'RJ',35:'SP',41:'PR',42:'SC',43:'RS',50:'MS',51:'MT',52:'GO',53:'DF'}
uf = {}
for cod, v in mun.items(): uf[UF[int(cod[:2])]] = uf.get(UF[int(cod[:2])], 0) + v
json.dump({'fonte': 'IBGE · Censo Demográfico 2022 · população residente (soma dos municípios)', 'ano': 2022, 'uf': dict(sorted(uf.items())), 'br': sum(uf.values())},
          open('lib/dados/retratos/populacao-uf.json', 'w'), ensure_ascii=False, indent=1)
