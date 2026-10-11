# Agente Especializado: Visual Specs - CoreMaterial Framework

## Missão
Extrair com máxima fidelidade todos os .materialrecipe e .visualstyleset do CoreMaterial.framework do macOS 26.6.1 para reprodução do Liquid Glass no HyprMac.

## Local de Trabalho
- Framework Principal: ~/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/
- Arquivos Alvo: *.materialrecipe, *.visualstyleset
- Recursos Relacionados: Assets.car, recursos de tipografia

## Extrair e Documentar

### 1. MATERIALS
Para cada .materialrecipe e .visualstyleset encontrado:
- Nome exato do arquivo (sem extensão)
- Recipe completo (estrutura XML/plist)
- Valores dark e light quando aplicável
- Source path completo

### 2. CORES
Extrair nomes semânticos com valores hexadecimais exatos:
- Procurar por definições de cor nos arquivos
- Mapear nomes semânticos para valores #RRGGBB
- Documentar fonte (arquivo e linha quando possível)

### 3. TIPOGRAFIA
Extrair estilos SF Pro:
- Font: nome exato da família SF Pro
- Size: tamanho em pontos
- Weight: peso numérico (400=regular, 600=semi-bold, etc.)
- Source: arquivo onde encontrado

### 4. ESPAÇAMENTO
Tokens de espaçamento em pontos:
- Nome do token (ex: spacing-small, padding-medium)
- Valor em pt
- Fonte

### 5. RAIOS
Componentes com valores de raio exatos:
- Nome do componente
- Valor em pt ou pixels
- Fonte

### 6. SOMBRAS
Definições de sombra:
- Offset (x y)
- Blur radius
- Cor RGBA
- Fonte

### 7. ASSETS
Recursos de Assets.car:
- Nome do asset
- Caminho no package
- Propósito/uso
- Dimensões (quando aplicável)

## EVIDÊNCIAS
Manter registro de:
- Path dos arquivos examinados
- Tipo (materialrecipe|visualstyleset|asset)
- Verificado (true/false)

## GAPS VS HYPRMAC
Identificar o que o HyprMac atualmente falta vs Tahoe 26

## PRIORIDADE DE IMPLEMENTAÇÃO
Lista ordenada do que implementar primeiro para máxima fidelidade

## SAÍDA ESPERADA
JSON estruturado conforme especificação no task original.