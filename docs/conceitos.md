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
>Chave é basicamente uma maneira de traduzir pra um atributo do objeto, como ex: obj1={nome:"João"} o obj1 possue a chave nome que também pode ser entendidta como key, atributo, chave...

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
> _State nada mais é que uma visão do momento atual daquele sistema, como sistemas grandes geralmente precisam compartilhar dados como: usuario logado, é usado o método de state que possuem suas proprias convenções sobre quem pode ou não mudar esses dados, tendo actions, reducers, store, cada um com sua função, e o LangGraph faz algo similar.

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
> O Grafo vai preenchendo o state atraves desse invoke() que diferente do NgRx que é movido a cliques (actions) que chamam os reducers, no grafo isso é feito de forma fixa, e também o fato de no tipo do state estar declarado com total= False permite que o objeto possa ser entregue incompleto (nem todos as chaves sempre estarão preenchidas/disponiveis, dependendo da logica)

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
> Entendi que o reducer é uma função que devolve um state novo, mas ela não altera o state antigo. No NgRx temos actions que nada mais são disparadas pelas telas (atraves dos clicks), elas servem pra anunciar/notificar o reducer que algo precisa ser alterado. No LangGraph não existe action, uma vez que o proprio invoke faz isso.

---

## 🧱 5. Função pura

_(a preencher quando a gente aprofundar)_

> ✏️ **TUA VEZ:**

---

## 🧱 6. Edge e conditional edge

Um **edge** (aresta) fixo é simples: "depois do nó A, sempre roda o nó B" —
`graph.add_edge("classify", "assess")`. Sem decisão nenhuma.

Um **conditional edge** é esse mesmo "depois de A" só que com uma bifurcação.
Em vez de apontar direto pro próximo nó, ele aponta pra uma **função Python
comum** que:

1. recebe o state atual (já com o que o nó anterior acabou de preencher);
2. lê uma gaveta dele;
3. devolve uma **string-chave** (não o nome do nó em si).

```python
def _route_after_decide(state: DisputeState) -> str:
    return "draft" if state["recommendation"] == "fight" else END
```

Essa string é procurada num dict que você declara junto com a edge —
`{"draft": "draft", END: END}` — e o valor encontrado é o nome do nó real
pra onde o LangGraph vai. A função não "manda" pra lugar nenhum sozinha; ela
só devolve uma chave, e o mapa é que resolve o destino. Isso é o que dá o
nome "roteamento por state": o caminho que o grafo percorre em cada
execução depende só do que já está escrito na caixa naquele momento —
nenhuma outra lógica externa entra aqui.

No pipeline de disputas: `decide` roda e escreve `recommendation`. A
conditional edge lê esse campo — se `"fight"`, despacha pro nó `draft`
(que gera a carta de verdade); se `"accept"`, despacha direto pro `END`,
e o `draft` nunca roda. Como o `draft_rebuttal` só é escrito dentro do nó
`draft`, no caminho accept essa gaveta **nunca chega a existir** na caixa —
é por isso que `final_state.get("draft_rebuttal")` em `app/main.py` devolve
`None` de graça, sem nenhum `if` explícito pra isso.

- 🅰️ **Ponte Angular:** mais perto de um `switch` dentro de um `effect` do
  que de qualquer coisa reativa/Observable — não tem stream nem
  subscription, é só "olha o state, devolve uma chave, o mapa resolve o
  próximo passo".
- 💻 **No projeto:** `_route_after_decide` e o `add_conditional_edges` em
  `app/agent/graph.py`; o campo que ele lê (`recommendation`) é escrito por
  `decide` em `app/agent/nodes/decide.py`.

> ✏️ **TUA VEZ:**

---

## 🧱 7. Structured output (tool-use) + o bug do `max_tokens`

Em vez de pedir texto pra Claude e sair com regex atrás dos dados, a gente
dá uma **"ferramenta" (tool) com um schema** — as gavetas que a resposta
*tem* que ter. A Claude responde preenchendo esse schema, e volta um JSON
pronto pra virar objeto. Muito mais confiável que parsear texto solto.

Mas não é mágica — dois modos de falha clássicos:

1. **Truncamento:** se `max_tokens` for baixo, o JSON é cortado no meio e
   vem incompleto. Foi o que aconteceu com a gente: `max_tokens=300`, a
   Claude escreveu um `meaning` gigante, estourou o limite
   (`stop_reason: max_tokens`) e o `required_evidence` nunca chegou →
   `KeyError`. Conserto: folga no `max_tokens` + pedir resposta concisa.
2. **Campo faltando:** o modelo às vezes omite um campo. Conserto: validar
   e ter um fallback.

- 🅰️ **Ponte:** o `input_schema` do tool é tipo um DTO/`class-validator`
  que você entrega PRA Claude preencher, em vez de validar o que chega. E o
  fallback é o equivalente a um `try/catch` que devolve um valor-padrão
  quando o serviço externo falha.
- 💻 **No projeto:** `_CLASSIFY_TOOL` em `app/agent/nodes/classify.py`; o
  `try/except` largo que cai no `REASON_CODES`.

> ✏️ **TUA VEZ:**
> _(reescreve aqui com tuas palavras)_

---

## 🧱 8. Server Component vs Client Component (Next.js App Router)

Isso aqui **não tem equivalente direto no Angular** — é o conceito mais
genuinamente novo da Milestone 5, vale prestar atenção.

No Angular, toda a aplicação é renderizada no cliente (mesmo com Angular
Universal fazendo SSR, o resultado final ainda é "hidrata tudo e o
framework roda inteiro no browser"). No Next.js App Router, cada arquivo
`page.tsx`/componente é, **por padrão, um Server Component**: ele roda *só*
no servidor, nunca manda o próprio código JS pro navegador — só o HTML já
pronto. Isso é ótimo pra performance (menos JS baixado) mas tem uma
limitação dura: **Server Component não pode ter `useState`, `onClick`, nem
nada que dependa do navegador** — porque ele nunca roda lá.

Quando você precisa de interatividade (estado, clique, `useEffect`), você
declara isso explicitamente com a diretiva `"use client"` no topo do
arquivo. Isso vira um "Client Component" — aí sim o React manda o JS dele
pro browser e ele funciona como você já conhece de SPA.

```tsx
"use client";  // sem isso, useState() nem compila aqui

export default function Home() {
  const [jsonText, setJsonText] = useState("");
  // ...
}
```

No nosso projeto, `app/page.tsx` inteiro precisou de `"use client"` porque
ele tem estado (o texto do JSON, o resultado, loading) e um `useEffect`
pra buscar os samples. Já `VerdictResult.tsx` **não** precisou da diretiva
- ele só recebe `verdict` como prop e desenha HTML, sem estado próprio nem
handler de evento. Mas como ele é importado *dentro* de um Client
Component (`page.tsx`), ele acaba entrando no mesmo pacote JS de qualquer
jeito - a diretiva marca a **fronteira**, não cada arquivo individualmente.

- 🅰️ **Ponte Angular:** não tem. O mais próximo, conceitualmente, é pensar
  no Server Component como um template renderizado no backend e devolvido
  como HTML puro (tipo uma view server-side clássica), e no Client
  Component como o Angular de sempre - roda no browser, tem change
  detection, reage a eventos.
- 💻 **No projeto:** `"use client"` no topo de
  `frontend/src/app/page.tsx`; `VerdictResult.tsx` fica sem a diretiva de
  propósito, pra mostrar que nem tudo precisa virar Client Component.

> ✏️ **TUA VEZ:**

---

## 🧱 9. `useState` (o "estado do componente" do React)

Isso aqui **tem** ponte direta com Angular, só que inversa: em vez de um
campo de classe (`this.jsonText = ""`) que o Angular observa via change
detection (zone.js ou signals), o React exige que você **anuncie**
explicitamente "isso aqui é estado" chamando `useState`:

```tsx
const [jsonText, setJsonText] = useState("");
//     ^valor atual  ^função pra trocar o valor
```

`useState("")` devolve um par: o valor atual (`jsonText`) e uma função
(`setJsonText`) que, quando chamada, **manda o React re-renderizar** o
componente com o novo valor. Diferente do Angular, onde você muda
`this.jsonText = "novo valor"` direto e o framework detecta a mudança por
fora, no React você nunca muda a variável na mão - só chama o `setState`
que o próprio hook te deu.

Por que essa página não precisou de nada tipo NgRx/store? Porque todo o
estado (`jsonText`, `verdict`, `loading`, `error`, `samples`) é **local a
um único componente** - ninguém mais na árvore precisa ler ou escrever
nisso. Sempre que o estado é usado por várias telas/componentes distantes
é que passa a valer a pena um store global; aqui seria over-engineering.

- 🅰️ **Ponte Angular:** `useState` é o campo de classe do seu
  `@Component`; `setJsonText(...)` é o que, no Angular, aconteceria
  sozinho depois de você atribuir o campo (a change detection já cobre
  isso pra você). No React, você tem que pedir o re-render explicitamente
  chamando a função setter.
- 💻 **No projeto:** todos os `useState` no topo de
  `frontend/src/app/page.tsx`.

> ✏️ **TUA VEZ:**

---

## Por preencher (próximos conceitos)

- [ ] `.invoke()` passo a passo (o que roda, em que ordem)
- [x] ~~Structured output / tool-use da Claude~~ → virou o tijolo 7
- [ ] Fallback e por que `classify` tem um `try/except` largo
- [ ] Pydantic vs TypedDict (validação em runtime vs só no editor)
- [x] ~~Server vs Client Component~~ → virou o tijolo 8
- [x] ~~useState~~ → virou o tijolo 9
- [ ] Props (o `@Input()` do React) - de onde vêm `samples`, `jsonText`, etc. em `DisputeForm`
