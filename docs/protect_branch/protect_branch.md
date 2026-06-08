# Step-by-Step: Proteção da Branch Main

**Objetivo:** Garantir que nenhum código seja enviado diretamente para a branch `main`. Todo o código deve passar primeiro pela branch `develop`.

## Passo 1: Criar o Código da GitHub Action
O GitHub não tem uma configuração nativa para permitir merges apenas de uma branch específica. Para resolver isso, criamos um fluxo automatizado (GitHub Action) para bloquear as outras origens.

1. No seu computador, abra a raiz (root) do seu projeto.
2. Crie uma pasta chamada `.github`. Dentro dela, crie outra pasta chamada `workflows`.
3. Crie um arquivo chamado `protect_main.yml` dentro de `workflows`.
4. Cole o seguinte código:

```yaml
name: Protect Main Branch

on:
  pull_request:
    branches:
      - main 

jobs:
  check-source-branch:
    runs-on: ubuntu-latest
    steps:
      - name: Check if the source branch is develop
        if: github.head_ref != 'develop' 
        run: |
          echo "Erro: Você só pode fazer merge na main a partir da branch develop!"
          exit 1
```

## Passo 2: Acionar a Action pela Primeira Vez
O GitHub precisa "ver" a action rodar uma vez antes de liberar a regra nas configurações de segurança.

1. Faça o commit e o push deste novo arquivo para o seu repositório no GitHub.
2. Vá para o site do GitHub e abra um Pull Request de teste (por exemplo, da develop para a main).
3. Espere a verificação automática rodar na tela do PR. Depois disso, você já pode fechar esse Pull Request.

## Passo 3: Configurar as Regras (Rulesets) no GitHub
Agora vamos configurar o repositório (repositório) para usar a nossa Action como uma regra obrigatória.

1. No seu repositório do GitHub, clique na aba Settings (Configurações).
2. No menu lateral esquerdo, clique em Rulesets (fica na seção Code and automation).
3. Clique no botão New branch ruleset.
4. Em Ruleset Name, digite main.
5. Na seção Target branches (Branches de destino):
   - Clique em Add target -> Include by pattern.
   - Digite main na caixa.
6. Na seção Branch rules (Regras da branch), marque as seguintes opções:
   - ✅ Require a pull request before merging (Isso impede envios diretos do terminal).
   - ✅ Require status checks to pass (Isso ativa o nosso código).
7. Dentro da caixa escura de "status checks", clique no botão + Add checks.
8. Procure pelo nome check-source-branch (que é o nome da tarefa que criamos no Passo 1) e selecione.
9. Clique em Create (Criar) ou Save (Salvar).