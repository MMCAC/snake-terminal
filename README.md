# 🐍 Snake Terminal

Jogo da cobrinha no terminal, feito em Python para Windows.

## Como jogar

```
python snake.py
```

## Controles

| Tecla | Ação |
|-------|------|
| `W` / `↑` | Mover para cima |
| `S` / `↓` | Mover para baixo |
| `A` / `←` | Mover para esquerda |
| `D` / `→` | Mover para direita |
| `Q` | Sair |

## Regras

- Coma as estrelas `★` para crescer e ganhar pontos
- Não bata nas paredes nem em si mesmo
- A velocidade aumenta a cada 5 pontos (até o nível 10)
- O recorde é salvo automaticamente em `record.json`

## Requisitos

- Python 3.8+
- Windows (usa `msvcrt` para leitura de teclas)
