"""
Leia o README.md na mesma pasta.
"""

import time

import pyautogui

# pyautogui.position()

pyautogui.hotkey("ctrl", "shift", "o")

time.sleep(2)

pyautogui.write("firefox /tmp/scielo_tmp/output_1.xml", interval=0.02)
pyautogui.press("enter")

time.sleep(1)

# click in article minimiza
pyautogui.click(314, 1289)

# seleciona
pyautogui.moveTo(321, 1289)
pyautogui.dragTo(321 + 200, 1289, button="left", duration=0.5)

# clica expande
pyautogui.click(314, 1289)

# copia

pyautogui.hotkey("ctrl", "c")

# Volta para o terminal
pyautogui.hotkey("alt", "tab")

pyautogui.write("google-chrome https://www.diffchecker.com/", interval=0.02)
pyautogui.press("enter")

time.sleep(2)

# Clica no lado esquerdo
pyautogui.click(635, 1458)

# Cola
pyautogui.hotkey("ctrl", "v")

# Volta para o terminal
pyautogui.hotkey("alt", "tab")

# Abre segundo arquivo
pyautogui.write("firefox /tmp/scielo_tmp/output_2.xml", interval=0.02)
pyautogui.press("enter")

time.sleep(1)

# click in article minimiza
pyautogui.click(314, 1289)

# seleciona
pyautogui.moveTo(321, 1289)
pyautogui.dragTo(321 + 200, 1289, button="left", duration=0.5)

# clica expande
pyautogui.click(314, 1289)

# copia
pyautogui.hotkey("ctrl", "c")

# Volta para o terminal
pyautogui.keyDown("alt")
pyautogui.press("tab")
pyautogui.press("tab")
pyautogui.keyUp("alt")

time.sleep(1)

# Clica no lado direito
pyautogui.click(1580, 1458)

# Cola
pyautogui.hotkey('ctrl', 'v')

# Clica em Find Difference
pyautogui.click(1222, 1663)

# ------------------

# for 3 to 7, porque temos 7 arquivos para serem comparados.

for i in range(3, 8):
    # Volta para o terminal
    pyautogui.keyDown("alt")
    pyautogui.press("tab")
    pyautogui.press("tab")
    pyautogui.keyUp("alt")

    pyautogui.write("google-chrome https://www.diffchecker.com/", interval=0.02)
    pyautogui.press("enter")

    time.sleep(2)

    # Clica no lado esquerdo
    pyautogui.click(635, 1458)

    # Cola

    pyautogui.hotkey("ctrl", "v")

    # Volta para o terminal
    pyautogui.hotkey("alt", "tab")

    # Abre segundo arquivo
    pyautogui.write(f"firefox /tmp/scielo_tmp/output_{i}.xml", interval=0.02)
    pyautogui.press("enter")


    time.sleep(1)

    # click in article minimiza
    pyautogui.click(314, 1289)

    # seleciona
    pyautogui.moveTo(321, 1289)
    pyautogui.dragTo(321 + 200, 1289, button="left", duration=0.5)

    # clica expande
    pyautogui.click(314, 1289)

    # copia
    pyautogui.hotkey("ctrl", "c")

    # Volta para o terminal
    pyautogui.keyDown("alt")
    pyautogui.press("tab")
    pyautogui.press("tab")
    pyautogui.keyUp("alt")

    time.sleep(1)

    # Clica no lado direito
    pyautogui.click(1580, 1458)

    # Cola
    pyautogui.hotkey("ctrl", "v")

    # Clica em Find Difference
    pyautogui.click(1222, 1663)
