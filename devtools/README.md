# pyautogui Teste de leitura e comparação das diferenças dos XML

Estamos usando a ferramenta [pyautogui](https://pyautogui.readthedocs.io/en/latest/quickstart.html), que é uma ferramenta de automação, para agilizar a abertura de todos os XML resultantes da conversão gerada a partir de `html_to_xml.py`.

Ou seja, obtemos 6 arquivos:

```
# coloquei tudo na pasta /tmp/scielo_tmp
# mkdir /tmp/scielo_tmp
```

Temos:

```
/tmp/scielo_tmp/output_1.xml
/tmp/scielo_tmp/output_2.xml
/tmp/scielo_tmp/output_3.xml
/tmp/scielo_tmp/output_4.xml
/tmp/scielo_tmp/output_5.xml
/tmp/scielo_tmp/output_6.xml
```

## Instalação

Instale digitando

```
pip install pyautogui
```

## Teste de posicionamento do mouse

Dependendo do tamanho do seu monitor você precisará fazer alguns ajustes na posição do mouse, para isso rode o comando:

```python
import pyautogui

pyautogui.position()
```

A partir dai você terá uma noção de ajuste da posição do mouse na sua tela, e **altere o código** com esses ajustes.


## Rodando o teste

Este teste específico, `read_diffchecker_xml_test.py`, requer que você tenha um terminal com opção de divisão de tela, exemplo, Terminator ou Tilix.

* Terminal
* Firefox aberto
* Google-Chrome aberto
* Os arquivos `output_*.xml` já devem existir na pasta `/tmp/scielo_tmp/`

Então rode

```
python read_diffchecker_xml_test.py
```

## Falhas

Este script não é perfeito, e depende de ajustes:

* Depende do seu monitor
* É necessário ajustar a posição do mouse
* Talvez seja necessário clicar em algum ponto da tela que o script não tenha clicado, exemplo, botão "Find Difference" no Chrome.

