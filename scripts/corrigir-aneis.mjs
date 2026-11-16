// Corrige polígonos da malha municipal em que ilhas foram gravadas como anéis extras de um único Polygon
// (o primeiro anel nem sempre é o contorno principal). Cada anel vira contorno externo ou buraco
// conforme a profundidade de contenção (par = externo, ímpar = buraco do anel que o contém).
// Uso: node scripts/corrigir-aneis.mjs entrada.json saida.json
import fs from 'node:fs';

const [, , ent, sai] = process.argv;
const j = JSON.parse(fs.readFileSync(ent, 'utf8'));

const area = (r) => {
  let a = 0;
  for (let i = 0, k = r.length - 1; i < r.length; k = i++) a += (r[k][0] - r[i][0]) * (r[k][1] + r[i][1]);
  return Math.abs(a / 2);
};
const dentro = ([x, y], r) => {
  let c = false;
  for (let i = 0, k = r.length - 1; i < r.length; k = i++) {
    const [xi, yi] = r[i];
    const [xk, yk] = r[k];
    if (yi > y !== yk > y && x < ((xk - xi) * (y - yi)) / (yk - yi) + xi) c = !c;
  }
  return c;
};
// ponto de teste: média dos dois primeiros vértices (evita cair exatamente sobre um vértice compartilhado)
const ponto = (r) => [(r[0][0] + r[1][0]) / 2, (r[0][1] + r[1][1]) / 2];

let corrigidos = 0;
for (const f of j.features) {
  const g = f.geometry;
  const aneis = g.type === 'Polygon' ? g.coordinates : g.coordinates.flat();
  if (aneis.length < 2) continue;
  const info = aneis.map((r) => ({ r, a: area(r) })).sort((x, y) => y.a - x.a);
  for (const x of info) {
    const p = ponto(x.r);
    x.pais = info.filter((y) => y !== x && y.a > x.a && dentro(p, y.r));
  }
  const externos = [];
  for (const x of info) {
    if (x.pais.length % 2 === 0) {
      x.poli = [x.r];
      externos.push(x);
    } else {
      const pai = x.pais.reduce((m, y) => (y.a < m.a ? y : m));
      (pai.poli || externos[0].poli).push(x.r);
    }
  }
  const novo = externos.length === 1 ? { type: 'Polygon', coordinates: externos[0].poli } : { type: 'MultiPolygon', coordinates: externos.map((x) => x.poli) };
  const antes = g.type === 'Polygon' ? 1 : g.coordinates.length;
  if (novo.type !== g.type || externos.length !== antes) corrigidos++;
  f.geometry = novo;
}
fs.writeFileSync(sai, JSON.stringify(j));
console.log(`${corrigidos} municípios com ilhas reorganizadas`);
