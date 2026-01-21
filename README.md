# 🏎️ Hot Wheels Data Repository

Uma base de dados abrangente e estruturada de castings, releases, séries e marcas de carros Hot Wheels, coletada da Hot Wheels Fandom Wiki.

**Status:** Em desenvolvimento | **Objetivo:** Servir como espinha dorsal para análises e futuras aplicações

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [📁 Estrutura dos Dados](#estrutura-dos-dados)
- [Como Começar](#como-começar)
- [Adicionando/Editando Dados](#adicionandoditando-dados)
- [Contribuindo via Git](#contribuindo-via-git)
- [Exemplos de Dados](#exemplos-de-dados)

---

## 🎯 [Visão Geral](#visão-geral)

Este projeto é impulsionado por dados organizados em arquivos JSON. Ajudamos a expandir e refinar essas informações através de contribuições diretas.

**Como você pode ajudar:**
- Preencher informações faltantes
- Corrigir dados existentes
- Adicionar novos detalhes e especificações
- Complementar descrições multilíngues

---

## [📁 Estrutura dos Dados](#estrutura-dos-dados)

```
data/
├── castings/        # Modelos de carros
├── releases/        # Lançamentos específicos por ano
├── series/          # Séries temáticas/anuais
└── brands/          # Fabricantes de veículos
```

### Castings (`data/castings/`)

Arquivo JSON para cada modelo de carro Hot Wheels.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `casting_id` | string | ID único do modelo |
| `name` | string | Nome do casting |
| `description` | object | Descrições em `en-us` e `pt-br` |
| `designer` | string | Quem desenhou o modelo |
| `debut_year` | number | Ano de estreia |
| `manufacturer` | string | Fabricante do veículo real |
| `releases` | array | Lista de lançamentos deste casting |

**Exemplo:** `data/castings/bugatti-veyron.json`

### Releases (`data/releases/{year}/`)

Arquivo JSON para cada lançamento único de um casting.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `release_id` | string | ID único do lançamento |
| `toy_number` | string | Número do brinquedo |
| `casting_id` | string | Referência ao casting |
| `year` | number | Ano do lançamento |
| `series_id` | string | Série a que pertence |
| `series_index` | number | Posição na série |
| `specs` | object | Cores, rodas, base, etc. |
| `country` | string | País de fabricação |
| `notes` | string | Observações adicionais |
| `images` | object | URLs das imagens |

**Exemplo:** `data/releases/2026/jbb15-bugatti-veyron.json`

### Series (`data/series/{year}/`)

Arquivo JSON para cada série anual ou temática.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `series_id` | string | ID único da série |
| `year` | number | Ano da série |
| `name` | string | Nome da série |
| `total_releases` | number | Total de lançamentos |
| `max_index` | number | Índice máximo |
| `releases` | array | Lista de releases pertencentes |

**Exemplo:** `data/series/2026/multipack-exclusive.json`

### Brands (`data/brands/`)

Arquivo JSON para cada marca de veículo.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `brand_id` | string | ID único (minúsculas-com-hífens) |
| `name` | string | Nome da marca |
| `country` | string | País de origem |
| `founded_year` | number\|null | Ano de fundação |
| `castings` | array | Paths dos castings associados |
| `description` | object | Descrições em `en-us` e `pt-br` |

**Exemplo:** `data/brands/chevrolet.json`

---

## 🚀 [Como Começar](#como-começar)

### Pré-requisitos

- Git instalado
- Editor de texto (VS Code, Notepad++, etc.)
- Acesso à [Hot Wheels Fandom Wiki](https://hotwheels.fandom.com/)

### Preparação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/hotwheels-data-repo.git
cd hotwheels-data-repo

# Crie uma branch para suas mudanças
git checkout -b feature/data-update-seu-foco
```

---

## ✏️ [Adicionando/Editando Dados](#adicionandoditando-dados)

### Passo 1: Identifique o Que Fazer

Procure por:
- ❌ Campos vazios (`""` ou `null`)
- 🌍 Descrições faltando em `pt-br` ou `en-us`
- 🎨 Especificações incompletas (cores, rodas, bases)
- 📸 Imagens faltando

### Passo 2: Localize o Arquivo Correto

| Tipo de Dado | Localização | Exemplo |
|--------------|------------|---------|
| Informações do carro | `data/castings/` | `mini-morris.json` |
| Lançamento específico | `data/releases/{ano}/` | `data/releases/2026/jbb15-mini-morris.json` |
| Marca | `data/brands/` | `chevrolet.json` |
| Série | `data/series/{ano}/` | `data/series/2026/mainline.json` |

### Passo 3: Edite o JSON

Abra o arquivo em seu editor e preencha os campos vazios.

⚠️ **Importante:** Mantenha o JSON válido! Cuidado com:
- Vírgulas (`,`) após valores
- Chaves (`{}`) e colchetes (`[]`)
- Aspas (`"`) para strings

### Passo 4: Adicione Imagens Corretamente

Sempre use URLs completas e diretas da Wikia:
```json
"images": {
  "0": "https://static.wikia.nocookie.net/hotwheels/images/0/07/Mini_Morris_2021_Mainline_Red.jpg",
  "1": "https://static.wikia.nocookie.net/hotwheels/images/1/12/Mini_Morris_2021_Red_Side.jpg"
}
```

### Passo 5: Criando uma Nova Marca (Opcional)

Se precisar criar uma marca que não existe:

```bash
# Crie o arquivo
touch data/brands/nova-marca.json
```

**Conteúdo padrão:**
```json
{
  "brand_id": "nova-marca",
  "name": "Nova Marca",
  "country": "Unknown",
  "founded_year": null,
  "castings": [
    "data/castings/seu-novo-casting.json"
  ],
  "description": {
    "en-us": "Manufacturer of Nova Marca vehicles.",
    "pt-br": "Fabricante de veículos Nova Marca."
  }
}
```

---

## 🔄 [Contribuindo via Git](#contribuindo-via-git)

### Fluxo Completo

```bash
# 1. Atualize seu repositório local
git pull origin main

# 2. Crie uma branch descritiva
git checkout -b feature/data-update-bugatti-veyron

# 3. Faça suas edições nos arquivos JSON

# 4. Verifique o que mudou
git status

# 5. Adicione as mudanças
git add .

# 6. Faça commit com mensagem clara
git commit -m "feat(data): Adiciona especificações completas para Bugatti Veyron 2024"

# 7. Envie sua branch
git push origin feature/data-update-bugatti-veyron
```

### Abrindo um Pull Request

1. Vá para [GitHub - seu repositório](https://github.com)
2. Clique em **"New Pull Request"**
3. Selecione sua branch de feature
4. Descreva as mudanças:
   - Quais carros foram atualizados?
   - Que informações foram adicionadas?
   - Fontes consultadas?
5. Clique em **"Create Pull Request"**

**Exemplo de descrição:**
```
## Alterações
- ✅ Bugatti Veyron: Adicionadas cores faltantes e imagens
- ✅ McLaren P1: Completadas descrições em português
- ✅ Novo casting: Ferrari LaFerrari

## Fontes
- Hot Wheels Fandom Wiki
- Catálogos 2024-2026

Closes #42
```

---

## 📖 [Exemplos de Dados](#exemplos-de-dados)

### Exemplo: Casting Completo

```json
{
  "casting_id": "mini-morris",
  "name": "Mini Morris",
  "description": {
    "en-us": "Classic British-built Mini Morris compact car, iconic design from the 1960s.",
    "pt-br": "Clássico Mini Morris construído na Grã-Bretanha, design icônico dos anos 60."
  },
  "designer": "Alejandro Ortiz",
  "debut_year": 2021,
  "manufacturer": "BMC (British Motor Corporation)",
  "releases": [
    "data/releases/2021/mini-morris-red.json",
    "data/releases/2022/mini-morris-blue.json"
  ]
}
```

### Exemplo: Release Completo

```json
{
  "release_id": "2021-mini-morris-red",
  "toy_number": "FYC78",
  "casting_id": "mini-morris",
  "year": 2021,
  "series_id": "mainline-2021",
  "series_index": 42,
  "specs": {
    "color": "Red",
    "tampo": "White stripes on hood and sides",
    "base_color": "Chrome",
    "base_type": "Metal",
    "window_color": "Clear",
    "interior_color": "Black",
    "wheel_type": {
      "0": "Real Riders 5-Spoke"
    }
  },
  "country": "Malaysia",
  "notes": "First release in the mainline. Base code(s): G23, G24",
  "images": {
    "0": "https://static.wikia.nocookie.net/hotwheels/images/0/07/Mini_Morris_2021_Mainline_Red.jpg",
    "1": "https://static.wikia.nocookie.net/hotwheels/images/1/12/Mini_Morris_2021_Red_Side.jpg"
  }
}
```

---

## 🤝 Contribuições Bem-Vindas

Seu trabalho faz diferença! Cada dado adicionado nos aproxima de um banco de dados completo e confiável.

**Dúvidas?** Abra uma issue ou entre em contato com os mantenedores.

---

## 📄 Licença

[Insira informação de licença aqui]

---

**Obrigado por ajudar a construir este vasto banco de dados! 🙏🏎️**

