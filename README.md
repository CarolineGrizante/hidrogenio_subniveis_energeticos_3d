<div align="center">

# Orbitais do Hidrogênio · Explorador 3D

**Visualização interativa em 3D e simulação computacional da função de onda $\psi_{n,l,m}(r, \theta, \phi)$ e densidade de probabilidade $\vert{}\psi\vert{}^2$ do átomo de hidrogénio.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-WebGL_3D-black?style=for-the-badge&logo=three.js&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Single_File-orange?style=for-the-badge&logo=html5&logoColor=white)


</div>

---

## Sobre o Projeto

O **Orbitais do Hidrogénio · Explorador 3D** é uma ferramenta didática projetada para transformar equações abstratas da mecânica quântica em representações visuais intuitivas e manipuláveis em tempo real. 

O repositório conta com **duas abordagens complementares**:
1. **Versão Web (`index.html`):** Aplicação autocontida construída com **Three.js (WebGL)**, rodando diretamente no navegador com renderização volumétrica/nuvem de pontos, controle de câmera orbital e troca instantânea de estados quânticos.
2. **Versão Python:** Script científico para geração, amostragem estatística e análise numérica das funções de onda em ambiente desktop.

---

## Funcionalidades Principais

*  **Visualização 3D em Tempo Real:** Rotação livre ($360^\circ$), zoom e panorâmica para inspecionar simetrias esféricas, halteres ($p$), trevos ($d$) e geometrias complexas ($f$).
*  **Seleção de Números Quânticos:** Explore diferentes combinações de:
  * **Número Quântico Principal ($n$):** Nível de energia e tamanho radial ($n = 1, 2, 3, 4...$).
  * **Número Quântico Azimutal ($l$):** Subnível e formato do orbital ($s, p, d, f$, onde $0 \le l < n$).
  * **Número Quântico Magnético ($m_l$):** Orientação espacial no eixo cartesiano ($-l \le m_l \le +l$).
*  **Codificação por Fase ou Densidade:** Distinção visual entre regiões de fase positiva ($+$) e negativa ($-$) da função de onda, além dos planos/superfícies nodais onde $\vert{}\psi\vert{}^2 = 0$.
* **Zero Dependências na Web:** O arquivo `index.html` já inclui o motor **Three.js** embutido — basta abrir no navegador ou hospedar no **GitHub Pages**.

---

## 📂 Estrutura do Repositório

```text
├── index.html                   # Aplicação Web 3D interativa (Three.js embutido)
├── orbitais.py                  # Versão Python para simulação e plotagem científica
├── Projeto_ComputaçãoGráfica    # Artigo sobre o tema
└── README.md                    # Documentação do projeto
