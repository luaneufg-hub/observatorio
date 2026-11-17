# Unidades de atendimento do Sebrae (painel "Mapa de Unidades SAS", Qlik do Sebrae, atualizado mensalmente)
# Entrada: a tabela "Detalhamento por Ponto de Atendimento" exportada em Excel.
# Saída:
#   public/dados/sebrae/unidades.json           → [cod IBGE, tipo, nome, lon, lat, coordenada real 0/1] por unidade
#   lib/dados/retratos/sebrae-unidades-uf.json  → totais por UF e por tipo
# Cada unidade é ligada ao município pelo nome da cidade (com variantes e distritos abaixo) ou, se o nome não
# bate, pela coordenada. Sem coordenada ou com coordenada fora do município informado, usa o centro do município.
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
 ('MT','BOA ESPERANCA DO NORTE'):'SORRISO'}
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
TIPOS=['Agência de Atendimento SEBRAE','Sala do Empreendedor','Espaço SEBRAE (Parceiros)','Parcerias de Atendimento','Parceiro Sebrae']
ROTULOS=['Agência Sebrae','Sala do Empreendedor','Espaço Sebrae (parceiros)','Parceria de atendimento','Parceiro Sebrae']
data=sys.argv[2] if len(sys.argv)>2 else datetime.date.today().isoformat()
fonte='Sebrae · Mapa de Unidades SAS (unidades ativas)'
out.sort(key=lambda r:(TIPOS.index(r['tipo']),r['cod']))
lin=[[r['cod'],TIPOS.index(r['tipo']),r['nome'],r['lon'],r['lat'],1 if r['coordReal'] else 0] for r in out]
os.makedirs('public/dados/sebrae',exist_ok=True)
json.dump({'fonte':fonte,'atualizadoEm':data,'tipos':ROTULOS,'campos':['cod','tipo','nome','lon','lat','coordReal'],'u':lin},open('public/dados/sebrae/unidades.json','w'),ensure_ascii=False,separators=(',',':'))
uf=collections.defaultdict(lambda:[0]*len(TIPOS)); br=[0]*len(TIPOS)
for r in out:
    i=TIPOS.index(r['tipo']); uf[r['uf']][i]+=1; br[i]+=1
json.dump({'fonte':fonte,'atualizadoEm':data,'tipos':ROTULOS,'br':br,'uf':dict(sorted(uf.items())),'semMunicipio':len(prob)},open('lib/dados/retratos/sebrae-unidades-uf.json','w'),ensure_ascii=False,indent=1)
print(len(lin),'unidades;',sum(r[5] for r in lin),'com coordenada real; por tipo',br)
