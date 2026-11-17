'use client';
// Pontos de atendimento por tipo (aparece logo abaixo do card do indicador "Pontos de atendimento"):
// agências (sede e escritórios regionais), Salas do Empreendedor e parceiros, com os mesmos pinos do mapa.
import Card, { Nota } from './Card';
import UNID from '@/lib/dados/retratos/sebrae-unidades-uf.json';
import { URL_SEDE, URL_ESCRITORIO, URL_PARCEIRO } from '@/lib/icones/pinosSebrae';

const n0 = (v) => v.toLocaleString('pt-BR');
const plural = (v, um, varios) => `${n0(v)} ${v === 1 ? um : varios}`;

/** contagem por tipo [agência, sala, espaço Sebrae, parceria, parceiro Sebrae] do Brasil, da UF ou do município */
function contar(base, uf, mun) {
  if (mun && base?.unidades) {
    const c = [0, 0, 0, 0, 0];
    for (const u of base.unidades) if (u.cod === mun.cod) c[u.tipo]++;
    return c;
  }
  return uf ? UNID.uf[uf] || [0, 0, 0, 0, 0] : UNID.br;
}

export default function TiposPontos({ base, uf, mun, lugar }) {
  const c = contar(base, uf, mun);
  const parceiros = c[2] + c[3] + c[4];
  const total = c[0] + c[1] + parceiros;
  const detalheParceiros = [
    c[2] && plural(c[2], 'Espaço Sebrae (Sebrae Aqui)', 'Espaços Sebrae (Sebrae Aqui)'),
    c[3] && plural(c[3], 'parceria de atendimento', 'parcerias de atendimento'),
    c[4] && plural(c[4], 'Parceiro Sebrae', 'Parceiros Sebrae'),
  ].filter(Boolean);
  const linhas = [
    { icone: URL_SEDE, alt: 'pino azul', rotulo: 'Agências Sebrae', sub: 'sede e escritórios regionais', v: c[0], cor: '#2A4FDA' },
    { icone: URL_ESCRITORIO, alt: 'pino rosa', rotulo: 'Salas do Empreendedor', v: c[1], cor: '#FF80C8' },
    { icone: URL_PARCEIRO, alt: 'pino verde', rotulo: 'Parceiros', sub: detalheParceiros.join(' · '), v: parceiros, cor: '#3D824F' },
  ];
  return (
    <Card
      icone="predio"
      rotulo={`Pontos de atendimento por tipo · ${lugar}`}
      quebrarRotulo
      info="Unidades ativas do Sebrae por tipo, com o mesmo pino do mapa. Agências reúnem a sede estadual e os escritórios regionais; parceiros reúnem os Espaços Sebrae (Sebrae Aqui), as parcerias de atendimento e os Parceiros Sebrae."
    >
      <ul className="mt-1 grid gap-2.5">
        {linhas.map((l) => (
          <li key={l.rotulo} className="grid grid-cols-[22px_minmax(0,1fr)_68px] items-start gap-x-2.5">
            <img src={l.icone} alt={l.alt} className="mt-0.5 h-[22px] w-auto justify-self-center" />
            <div className="min-w-0">
              <div className="text-[13.5px] font-semibold text-tema-tinta">{l.rotulo}</div>
              {l.sub && <div className="text-[11.5px] leading-snug text-tema-suave">{l.sub}</div>}
              <span className="mt-1 block h-1.5 overflow-hidden rounded-full bg-tema-linha">
                <span className="block h-full rounded-full" style={{ width: `${total ? Math.max(l.v ? 2 : 0, (l.v / total) * 100) : 0}%`, background: l.cor }} />
              </span>
            </div>
            <div className="text-right font-display text-[18px] font-extrabold leading-tight text-tema-tinta tabular-nums">{n0(l.v)}</div>
          </li>
        ))}
      </ul>
      <Nota>Fonte: Sebrae, Mapa de Unidades SAS (nov. 2026), com agências do RS e do AM conferidas nos sites oficiais</Nota>
    </Card>
  );
}
