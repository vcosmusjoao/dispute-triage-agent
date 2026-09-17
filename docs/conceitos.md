# Conceitos — meu diário de aprendizado

> Este arquivo cresce junto com o projeto. Cada conceito novo que a gente
> destrincha vira um bloco aqui. A regra: o Claude escreve a versão dele,
> mas eu (João) reescrevo com as MINHAS palavras no espaço **✏️ TUA VEZ** —
> porque o que fixa na memória é escrever, não ler.
>
> Ordem = mais ou menos a ordem em que aprendi. É pra reler antes de
> entrevista e lembrar do "porquê", não só do "o quê".

---

## Legenda

- 🧱 **Tijolo** = um conceito-base.
- 🅰️ **Ponte Angular** = como isso se traduz pro que eu já sei (Angular/Nest/NgRx/RxJS/TS).
- 💻 **No projeto** = onde isso aparece no código de verdade.
- ✏️ **TUA VEZ** = eu reescrevo com minhas palavras.

---

## 🧱 1. Chave (key)

Um `dict` no Python é uma caixa de gavetas etiquetadas. A **chave** é a
etiqueta da gaveta; o **valor** é o que está dentro.

```python
pessoa = {"nome": "João", "idade": 30}
#          └ chave ┘         └ chave ┘
#                   └valor┘          └valor┘
```

Quando alguém diz "o state tem 5 chaves", quer dizer "a caixa tem 5 gavetas
etiquetadas e preenchidas".

- 🅰️ **Ponte Angular:** idêntico a um object do JS/TS — `{nome: "João"}`. As chaves são `nome`, `idade`.
- 💻 **No projeto:** todo dict que a gente passa/retorna. Ex.: `{"score": 0.7, "signal_reasons": [...]}`.

> ✏️ **TUA VEZ:**
> _(reescreve aqui com tuas palavras)_

---

## 🧱 2. State (estado)

**State = estado = "como as coisas estão agora, neste momento".** É uma foto
da situação atual. O estado da água (líquida/gelo), o saldo da conta hoje, o
save do Mario (`{vidas: 3, moedas: 40}`). Muda com o tempo.

Em software, é a caixa de gavetas que guarda todos os dados que descrevem a
situação atual do sistema.

- 🅰️ **Ponte Angular:** o `state` do NgRx (o conteúdo do store). Mesmíssima palavra, mesmíssima ideia.
- 💻 **No projeto:** `DisputeState` em `app/agent/state.py` — a caixa que viaja pelo grafo.

> ✏️ **TUA VEZ:**
> _(reescreve aqui com tuas palavras)_

---

## 🧱 3. A caixa que viaja (como o grafo preenche o state)

No nosso grafo existe **uma única caixa de state** que passa de nó em nó, e
cada nó **preenche mais gavetas**. Ela começa quase vazia e vai engordando:

```
Começo:    { dispute }                                          → 1 gaveta
classify:  + reason_code_meaning, required_evidence             → 3 gavetas
assess:    + score, signal_reasons                              → 5 gavetas
decide:    + recommendation, confidence, why                    → 8 gavetas
draft:     + draft_rebuttal   (só se recommendation == "fight") → 9 gavetas
```

Se cair no `accept`, o `draft` nem roda → a gaveta `draft_rebuttal` nunca é
criada. Isso só é possível porque `DisputeState` foi declarado com
`total=False` (= "as gavetas são opcionais, a caixa pode estar incompleta").

- 🅰️ **Ponte Angular:** como o store do NgRx que vai sendo atualizado por vários reducers ao longo do tempo — só que aqui o caminho é fixo, não dirigido por cliques.
- 💻 **No projeto:** `dispute_graph.invoke({"dispute": ...})` em `app/main.py` dispara essa viagem.

> ✏️ **TUA VEZ:**
> _(reescreve aqui com tuas palavras)_

---

## 🧱 4. Componente vs Action vs Reducer (o ritual do NgRx)

O NgRx existe pra mudar dados compartilhados de um jeito **previsível e
rastreável** — não pra "lidar com condições". A regra rígida é:

| Quem | Papel | No NgRx |
|------|-------|---------|
| **Componente/tela** | só **anuncia** que algo aconteceu (não toca no state) | `store.dispatch(action)` |
| **Action** | é o **anúncio em si** — um papelzinho com nome + dado | `createAction('[Cart] Add Item')` |
| **Reducer** | **pega o anúncio e produz a próxima versão da caixa** (o único com "a caneta") | `createReducer(...)` |

O reducer é uma **função pura**: recebe o state, devolve um state novo, sem
mutar o antigo.

- 🅰️ **Ponte pro LangGraph:** o **nó** (`classify`, `assess`...) **é o reducer** — recebe a caixa, devolve a próxima versão dela. No LangGraph NÃO existe o "papelzinho" (action) separado: o caminho já está fiado no grafo.
- 💻 **No projeto:** cada função em `app/agent/nodes/` é um reducer.

> ✏️ **TUA VEZ:**
> _(reescreve aqui com tuas palavras)_

---

## 🧱 5. Função pura

_(a preencher quando a gente aprofundar)_

> ✏️ **TUA VEZ:**

---

## 🧱 6. Edge e conditional edge

_(a preencher — a ligação entre os nós e o "switch" que decide o caminho)_

> ✏️ **TUA VEZ:**

---

## Por preencher (próximos conceitos)

- [ ] `.invoke()` passo a passo (o que roda, em que ordem)
- [ ] Structured output / tool-use da Claude (como pedir JSON confiável)
- [ ] Fallback e por que `classify` tem um `try/except` largo
- [ ] Pydantic vs TypedDict (validação em runtime vs só no editor)
