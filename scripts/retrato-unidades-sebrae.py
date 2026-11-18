# Unidades de atendimento do Sebrae (painel "Mapa de Unidades SAS", Qlik do Sebrae, atualizado mensalmente)
# Entrada: a tabela "Detalhamento por Ponto de Atendimento" exportada em Excel.
# Saída:
#   public/dados/sebrae/unidades.json           → [cod IBGE, tipo, nome, lon, lat, coordenada real 0/1] por unidade
#   lib/dados/retratos/sebrae-unidades-uf.json  → totais por UF e por tipo
# Cada unidade é ligada ao município pelo nome da cidade (com variantes e distritos abaixo) ou, se o nome não
# bate, pela coordenada. Sem coordenada ou com coordenada fora do município informado, usa o centro do município.
# Complemento (scripts/fontes/unidades-complemento.csv): agências e escritórios regionais que faltam no SAS,
# conferidos em fontes oficiais (nov. 2026) — o RS só tinha a agência de Porto Alegre e o AM só as de Manaus.
#   rs → site do Sebrae RS, "Encontre o Sebrae" (sebraers.com.br/atendimento-encontre-o-sebrae), endereço por cidade
#   am → Agência Sebrae de Notícias AM, 20 maio 2026: "Sebrae Amazonas inaugura 10º escritório regional em Autazes"
#   nacional → sede do Sebrae Nacional (SGAS 605, Asa Sul; coordenada do CEP 70200-904, exclusivo do Sebrae Nacional)
# Sem coordenada: ficam no centro do município.
# Uso: python3 scripts/retrato-unidades-sebrae.py <planilha.xlsx> [data AAAA-MM-DD]
import sys, datetime
import pandas as pd, json, unicodedata, re, glob, os, collections
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
R='public/geo'
idx=json.load(open(f'{R}/municipios-index.json'))
info={m[0]:m for m in idx}
def norm(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper()
    s=re.sub(r"[^A-Z ]"," ",s); return re.sub(r"\s+"," ",s).strip()
mapa={(m[2],norm(m[1])):m[0] for m in idx}
# nomes antigos/variantes -> nome IBGE
ALIAS={('CE','ITAPAJE'):'ITAPAGE',('MG','BRAZOPOLIS'):'BRASOPOLIS',('MG','DONA EUZEBIA'):'DONA EUSEBIA',('MT','POXOREU'):'POXOREO',
 ('PA','ELDORADO DO CARAJAS'):'ELDORADO DOS CARAJAS',('PA','MOJUI DOS CAMPOS'):'MOJUI DOS CAMPOS',('PA','SANTA IZABEL DO PARA'):'SANTA ISABEL DO PARA',
 ('PB','SAO VICENTE DO SERIDO'):'SERIDO',('PE','BELEM DO SAO FRANCISCO'):'BELEM DE SAO FRANCISCO',('PE','IGUARACY'):'IGUARACI',
 ('PI','NAZARIA'):'NAZARIA',('RN','AREZ'):'ARES',('RN','BOA SAUDE'):'JANUARIO CICCO',('RN','SERRA CAIADA'):'PRESIDENTE JUSCELINO',
 ('SP','EMBU DAS ARTES'):'EMBU',('SP','FLORINEA'):'FLORINIA',('SP','MOGI MIRIM'):'MOJI MIRIM',('SP','SAO LUIZ DO PARAITINGA'):'SAO LUIS DO PARAITINGA',
 ('TO','TABOCAO'):'FORTALEZA DO TABOCAO',('MS','PARAISO DAS AGUAS'):'PARAISO DAS AGUAS',
 # distritos -> município sede
 ('ES','ARACE'):'DOMINGOS MARTINS',('MG','SERRA DO CIPO'):'SANTANA DO RIACHO',('AM','SANTO ANTONIO DO MATUPI'):'MANICORE',
 ('MT','BOA ESPERANCA DO NORTE'):'SORRISO',('RS','SANTANA DO LIVRAMENTO'):'SANT ANA DO LIVRAMENTO',('PE','LAGOA DO ITAENGA'):'LAGOA DE ITAENGA'}
geoms=[];cods=[]
for f in glob.glob(f'{R}/municipios/*.json'):
    for ft in json.load(open(f))['features']:
        geoms.append(shape(ft['geometry']));cods.append(ft['properties']['cod'])
tree=STRtree(geoms)
def pip(lon,lat):
    p=Point(lon,lat)
    for i in tree.query(p):
        if geoms[i].contains(p): return cods[i]
    # mais perto (pontos na costa)
    i=tree.nearest(p); return cods[i] if geoms[i].distance(p)<0.05 else None
d=pd.read_excel(sys.argv[1]).drop_duplicates('ID Unidade')
d=d.rename(columns={'Tipo de Ponto de Atendimento':'tipo','Descrição':'desc'})
d=d[(d.UF!='-')&(d['tipo']!='-')].copy()
def xy(s):
    try: a=json.loads(s); return float(a[0]),float(a[1])
    except: return None,None
d['lon'],d['lat']=zip(*[xy(s) for s in d.PontoUnidadeCompleto])
out=[];prob=[]
for r in d.itertuples():
    k=(r.UF,norm(r.Cidade)); k2=(r.UF,ALIAS.get(k,k[1]))
    cod=mapa.get(k) or mapa.get(k2)
    pc=pip(r.lon,r.lat) if r.lon is not None and r.lon==r.lon else None
    if cod is None: cod=pc; origem='coord'
    else: origem='nome'
    usa_coord = pc is not None and pc==cod
    if cod is None: prob.append((r.UF,r.Cidade,r.lon,r.lat)); continue
    m=info[cod]
    lon,lat=(r.lon,r.lat) if usa_coord else (m[4],m[5])
    out.append(dict(cod=cod,uf=m[2],tipo=r.tipo,nome=str(r.desc).strip(),lon=round(lon,5),lat=round(lat,5),coordReal=usa_coord))
print('ok',len(out),'sem municipio',len(prob)); print(prob)
# complemento de fontes oficiais (agências / escritórios regionais que faltam no SAS)
FONTES=['Sebrae · Mapa de Unidades SAS','Site do Sebrae RS · Encontre o Sebrae (nov. 2026)','Agência Sebrae de Notícias AM (20 maio 2026)','Sebrae Nacional · SGAS 605, Asa Sul (CEP 70200-904)']
for r in out: r['fonte']=0
comp=pd.read_csv('scripts/fontes/unidades-complemento.csv')
ja={(r['uf'],r['cod']) for r in out if r['tipo']=='Agência de Atendimento SEBRAE'}
for r in comp.itertuples():
    k=(r.uf,norm(r.cidade)); cod=mapa.get(k) or mapa.get((r.uf,ALIAS.get(k,k[1])))
    if cod is None: print('complemento sem município:',r.uf,r.cidade); continue
    # RS e AM: só onde o SAS não tem agência no município; o Sebrae Nacional entra sempre
    if r.fonte in ('rs','am') and (r.uf,cod) in ja: continue
    m=info[cod]
    tem=r.lon==r.lon and r.lat==r.lat  # não é NaN
    out.append(dict(cod=cod,uf=r.uf,tipo='Agência de Atendimento SEBRAE',nome=r.nome,lon=float(r.lon) if tem else m[4],lat=float(r.lat) if tem else m[5],coordReal=bool(tem),fonte={'rs':1,'am':2,'nacional':3}[r.fonte]))
TIPOS=['Agência de Atendimento SEBRAE','Sala do Empreendedor','Espaço SEBRAE (Parceiros)','Parcerias de Atendimento','Parceiro Sebrae']
ROTULOS=['Agência Sebrae','Sala do Empreendedor','Espaço Sebrae (parceiros)','Parceria de atendimento','Parceiro Sebrae']
data=sys.argv[2] if len(sys.argv)>2 else datetime.date.today().isoformat()
fonte='Sebrae · Mapa de Unidades SAS (unidades ativas)'
out.sort(key=lambda r:(TIPOS.index(r['tipo']),r['cod']))
lin=[[r['cod'],TIPOS.index(r['tipo']),r['nome'],r['lon'],r['lat'],1 if r['coordReal'] else 0,r['fonte']] for r in out]
os.makedirs('public/dados/sebrae',exist_ok=True)
json.dump({'fonte':fonte,'atualizadoEm':data,'tipos':ROTULOS,'fontes':FONTES,'campos':['cod','tipo','nome','lon','lat','coordReal','fonte'],'u':lin},open('public/dados/sebrae/unidades.json','w'),ensure_ascii=False,separators=(',',':'))
uf=collections.defaultdict(lambda:[0]*len(TIPOS)); br=[0]*len(TIPOS)
for r in out:
    i=TIPOS.index(r['tipo']); uf[r['uf']][i]+=1; br[i]+=1
json.dump({'fonte':fonte,'atualizadoEm':data,'tipos':ROTULOS,'complemento':sum(1 for r in out if r['fonte']),'br':br,'uf':dict(sorted(uf.items())),'semMunicipio':len(prob)},open('lib/dados/retratos/sebrae-unidades-uf.json','w'),ensure_ascii=False,indent=1)
print(len(lin),'unidades;',sum(r[5] for r in lin),'com coordenada real; por tipo',br)
