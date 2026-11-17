import time
import psutil
import math
import numpy as np
from scipy.special import eval_genlaguerre, sph_harm_y
import pyvista as pv

# ==============================================================================
# 1. MÓDULO MATEMÁTICO: FUNÇÃO DE ONDA REAL COM SEPARAÇÃO DE FASE (+ / -)
# ==============================================================================

def calcular_funcao_de_onda_real(n, l, m, grade_x, grade_y, grade_z):
    """
    Calcula o valor real da Função de Onda Psi_nlm(x, y, z) para o átomo de hidrogênio.
    Utiliza definições analíticas diretas até l=3 (orbitais s, p, d, f) para garantir
    geometria perfeita e evitar trocas de ângulos do sph_harm_y.
    """
    # 1. Coordenadas esféricas e distância radial
    raio_distancia = np.sqrt(grade_x**2 + grade_y**2 + grade_z**2)
    raio_seguro = np.where(raio_distancia == 0, 1e-10, raio_distancia)
    
    # Cosseno do ângulo polar theta (z / r) e seno de theta
    cos_theta = np.clip(grade_z / raio_seguro, -1.0, 1.0)
    sin_theta = np.sqrt(1.0 - cos_theta**2)
    
    # Ângulo azimutal phi
    phi = np.arctan2(grade_y, grade_x)
    
    # 2. Parte Radial R_nl(r)
    raio_bohr = 1.0
    rho_radial = 2.0 * raio_distancia / (n * raio_bohr)
    
    fatorial_norm = (2.0 / (n * raio_bohr))**3 * (math.factorial(n - l - 1) / (2.0 * n * math.factorial(n + l)))
    fator_normalizacao_radial = np.sqrt(fatorial_norm)
    
    polinomio_laguerre = eval_genlaguerre(n - l - 1, 2 * l + 1, rho_radial)
    funcao_radial = fator_normalizacao_radial * np.exp(-rho_radial / 2.0) * (rho_radial**l) * polinomio_laguerre

    # 3. Harmónicas Esféricas Reais Diretamente Definidas
    if l == 0:  # Orbitais s
        harmonica_real = np.full_like(grade_x, 0.5 * np.sqrt(1.0 / np.pi))
        
    elif l == 1:  # Orbitais p
        if m == 0:     # p_z
            harmonica_real = 0.5 * np.sqrt(3.0 / np.pi) * cos_theta
        elif m == 1:   # p_x
            harmonica_real = 0.5 * np.sqrt(3.0 / np.pi) * sin_theta * np.cos(phi)
        elif m == -1:  # p_y
            harmonica_real = 0.5 * np.sqrt(3.0 / np.pi) * sin_theta * np.sin(phi)
            
    elif l == 2:  # Orbitais d
        if m == 0:     # d_z^2 (2 lóbulos no eixo Z + anel no plano XY)
            harmonica_real = 0.25 * np.sqrt(5.0 / np.pi) * (3.0 * cos_theta**2 - 1.0)
        elif m == 1:   # d_xz
            harmonica_real = 0.5 * np.sqrt(15.0 / np.pi) * sin_theta * cos_theta * np.cos(phi)
        elif m == -1:  # d_yz
            harmonica_real = 0.5 * np.sqrt(15.0 / np.pi) * sin_theta * cos_theta * np.sin(phi)
        elif m == 2:   # d_x^2-y^2
            harmonica_real = 0.25 * np.sqrt(15.0 / np.pi) * (sin_theta**2) * np.cos(2.0 * phi)
        elif m == -2:  # d_xy
            harmonica_real = 0.25 * np.sqrt(15.0 / np.pi) * (sin_theta**2) * np.sin(2.0 * phi)

    elif l == 3:  # Orbitais f
        if m == 0:     # f_z^3 (4f_z^3 / 5f_z^3)
            harmonica_real = 0.3730681261 * (5.0 * (cos_theta**3) - 3.0 * cos_theta)
        elif m == 1:   # f_xz^2
            harmonica_real = 0.25 * np.sqrt(42.0 / np.pi) * sin_theta * (5.0 * cos_theta**2 - 1.0) * np.cos(phi)
        elif m == -1:  # f_yz^2
            harmonica_real = 0.25 * np.sqrt(42.0 / np.pi) * sin_theta * (5.0 * cos_theta**2 - 1.0) * np.sin(phi)
        elif m == 2:   # f_z(x^2-y^2)
            harmonica_real = 0.25 * np.sqrt(105.0 / np.pi) * (sin_theta**2) * cos_theta * np.cos(2.0 * phi)
        elif m == -2:  # f_xyz
            harmonica_real = 0.25 * np.sqrt(105.0 / np.pi) * (sin_theta**2) * cos_theta * np.sin(2.0 * phi)
        elif m == 3:   # f_x(x^2-3y^2)
            harmonica_real = 0.25 * np.sqrt(35.0 / (2.0 * np.pi)) * (sin_theta**3) * np.cos(3.0 * phi)
        elif m == -3:  # f_y(3x^2-y^2)
            harmonica_real = 0.25 * np.sqrt(35.0 / (2.0 * np.pi)) * (sin_theta**3) * np.sin(3.0 * phi)
            
    else:  # Fallback corrigido para l >= 4 (Orbitais g, h, ...)
        theta = np.arccos(cos_theta)
        if m == 0:
            harmonica_real = np.real(sph_harm_y(l, 0, theta, phi))
        elif m > 0:
            y_pos = sph_harm_y(l, m, theta, phi)
            y_neg = sph_harm_y(l, -m, theta, phi)
            harmonica_real = np.real((1.0 / np.sqrt(2)) * (y_neg + ((-1)**m) * y_pos))
        else:
            m_abs = abs(m)
            y_pos = sph_harm_y(l, m_abs, theta, phi)
            y_neg = sph_harm_y(l, -m_abs, theta, phi)
            harmonica_real = np.real((1.0j / np.sqrt(2)) * (y_neg - ((-1)**m_abs) * y_pos))

    # 4. Função de Onda Real Completa Psi_nlm
    psi = funcao_radial * harmonica_real

    # Inverte o sinal EXCLUSIVAMENTE no orbital 4s (4,0,0) para a casca externa ficar Azul
    if n == 4 and l == 0 and m == 0:
        psi = -psi

    return psi


# ==============================================================================
# 2. MÓDULO DE DESEMPENHO COMPUTACIONAL
# ==============================================================================

def medir_desempenho_computacional(funcao_alvo, *argumentos):
    processo_atual = psutil.Process()
    memoria_inicial_mib = processo_atual.memory_info().rss / (1024 * 1024)
    
    tempo_inicio = time.perf_counter()
    resultado = funcao_alvo(*argumentos)
    tempo_fim = time.perf_counter()
    
    memoria_final_mib = processo_atual.memory_info().rss / (1024 * 1024)
    
    tempo_execucao_ms = (tempo_fim - tempo_inicio) * 1000.0
    consumo_memoria_mib = max(0.0, memoria_final_mib - memoria_inicial_mib)
    
    return resultado, tempo_execucao_ms, consumo_memoria_mib


# ==============================================================================
# 3. MÓDULO GRÁFICO: RENDERIZADOR LADO A LADO (COMPLETO VS CORTE TRANSVERSAL)
# ==============================================================================

def gerar_orbital_3d(n, l, m, resolucao_grid=128, limite_espacial=None):
    # Cálculo automático do limite dinâmico baseado no raio médio do orbital (~ n^2)
    if limite_espacial is None:
        if l == 0:
            limite_espacial = float(n**2 * 3.5 + 5.0)
        else:
            limite_espacial = float(n**2 * 2.5 + 5.0)

    subniveis_nomes = {0: 's', 1: 'p', 2: 'd', 3: 'f'}
    nome_subnivel = subniveis_nomes.get(l, f'l={l}')
    
    print("\n" + "="*75)
    print(f" GERANDO ORBITAL: {n}{nome_subnivel} (n={n}, l={l}, m={m})")
    print(f" Resolução do Grid: {resolucao_grid}x{resolucao_grid}x{resolucao_grid} voxels")
    print(f" Limite Espacial: [-{limite_espacial:.1f}, +{limite_espacial:.1f}] a_0")
    print("="*75)
    
    # 1. Grade cartesiana 3D
    eixo_espacial = np.linspace(-limite_espacial, limite_espacial, resolucao_grid, dtype=np.float32)
    grade_x, grade_y, grade_z = np.meshgrid(eixo_espacial, eixo_espacial, eixo_espacial, indexing='ij')
    
    # 2. Calcular a Função de Onda Real
    psi_real, tempo_ms, memoria_mib = medir_desempenho_computacional(
        calcular_funcao_de_onda_real, n, l, m, grade_x, grade_y, grade_z
    )
    
    print(f" [Métricas de Desempenho]:")
    print(f"    -> Tempo de Processamento: {tempo_ms:.2f} ms ({(tempo_ms/1000):.2f} s)")
    print(f"    -> Consumo de Memória RAM: {memoria_mib:.2f} MiB")
    
    # 3. Estruturação do Volume no PyVista
    volume_grade = pv.ImageData()
    volume_grade.dimensions = (resolucao_grid, resolucao_grid, resolucao_grid)
    volume_grade.origin = (-limite_espacial, -limite_espacial, -limite_espacial)
    espacamento = (2.0 * limite_espacial) / (resolucao_grid - 1)
    volume_grade.spacing = (espacamento, espacamento, espacamento)
    
    volume_grade.point_data["psi"] = psi_real.astype(np.float32).flatten(order="F")
    
    # 4. Limiar de Isossuperfície Adaptativo Ajustado
    pico_maximo = np.max(np.abs(psi_real))
    
    # Calibração do isovalor para expor o anel fino e separar os lóbulos
    if l == 3 and m == 0:
        fator_isovalor = 0.18
    elif n >= 4:
        fator_isovalor = 0.12
    else:
        fator_isovalor = 0.08
        
    limiar_isovalor = fator_isovalor * pico_maximo
    
    iso_pos_completa = volume_grade.contour(isosurfaces=[limiar_isovalor], scalars="psi")
    iso_neg_completa = volume_grade.contour(isosurfaces=[-limiar_isovalor], scalars="psi")
    
    # Gerar corte transversal no plano Z=0 para expor as camadas e nós radiais internos
    iso_pos_cortada = iso_pos_completa.clip(normal='z', origin=(0, 0, 0)) if iso_pos_completa.n_cells > 0 else None
    iso_neg_cortada = iso_neg_completa.clip(normal='z', origin=(0, 0, 0)) if iso_neg_completa.n_cells > 0 else None

    # 5. Configurar Janela com 2 Subplots Sincronizados
    janela_grafica = pv.Plotter(
        shape=(1, 2), 
        title=f"Visualizador de Orbitais Atômicos - {n}{nome_subnivel} (Resolução: {resolucao_grid}^3)"
    )
    
    # --- SUBPLOT 1 (Esquerda): VISTA EXTERNA COMPLETA ---
    janela_grafica.subplot(0, 0)
    janela_grafica.set_background("#1e1e24")
    
    if iso_pos_completa.n_cells > 0:
        janela_grafica.add_mesh(
            iso_pos_completa, color="#ff3333", smooth_shading=True, opacity=0.85, specular=0.4
        )
    if iso_neg_completa.n_cells > 0:
        janela_grafica.add_mesh(
            iso_neg_completa, color="#3366ff", smooth_shading=True, opacity=0.85, specular=0.4
        )
        
    janela_grafica.add_text("Visão Completa 3D", position="upper_left", font_size=10, color="white")
    janela_grafica.add_axes(line_width=3)
    janela_grafica.show_grid(color="#555555")

    # --- SUBPLOT 2 (Direita): CORTE TRANSVERSAL ---
    janela_grafica.subplot(0, 1)
    janela_grafica.set_background("#1e1e24")
    
    if iso_pos_cortada and iso_pos_cortada.n_cells > 0:
        janela_grafica.add_mesh(
            iso_pos_cortada, color="#ff3333", smooth_shading=True, opacity=0.95, specular=0.4
        )
    if iso_neg_cortada and iso_neg_cortada.n_cells > 0:
        janela_grafica.add_mesh(
            iso_neg_cortada, color="#3366ff", smooth_shading=True, opacity=0.95, specular=0.4
        )
        
    texto_direito = (
        f"Corte Transversal (Nós Radiais Internos)\n"
        f"Tempo: {tempo_ms:.1f} ms | RAM: {memoria_mib:.2f} MiB"
    )
    janela_grafica.add_text(texto_direito, position="upper_left", font_size=10, color="white")
    janela_grafica.add_axes(line_width=3)
    janela_grafica.show_grid(color="#555555")

    # Sincroniza rotação e zoom dos dois quadros
    janela_grafica.link_views()
    
    print("\n[!] Janela 3D aberta. Feche a janela gráfica para voltar ao menu.")
    janela_grafica.show()


# ==============================================================================
# 4. MENU INTERATIVO (LAYOUT IDÊNTICO À IMAGEM GUIA)
# ==============================================================================

if __name__ == "__main__":
    while True:
        print("==========================================================================")
        print("    VISUALIZADOR DE ORBITAIS DE HIDROGÊNIO")
        print("==========================================================================")
        
        try:
            n = int(input("\n1. Digite o número quântico principal n (>= 1, ex: 1, 2, 3, 4, 5, 6 ou 7): "))
            if n < 1:
                print("Erro: 'n' deve ser maior ou igual a 1.")
                continue
                
            print(f"   -> Subníveis disponíveis para n={n}: l de 0 até {n-1} (0=s, 1=p, 2=d, 3=f)")
            l = int(input(f"2. Digite o número quântico azimutal l (0 a {n-1}): "))
            if l < 0 or l >= n:
                print(f"Erro: Para n={n}, 'l' deve estar entre 0 e {n-1}.")
                continue
                
            print(f"   -> Orientação magnética disponível para l={l}: m de {-l} até {l}")
            m = int(input(f"3. Digite o número quântico magnético m ({-l} a {l}): "))
            if abs(m) > l:
                print(f"Erro: Para l={l}, 'm' deve estar entre {-l} e {l}.")
                continue
                
            res_input = input("4. Resolução do grid (ENTER para 128, limite de 100 a 1000): ").strip()
            if res_input:
                resolucao = int(res_input)
                if resolucao < 100 or resolucao > 1000:
                    print("Atenção: Escolha uma resolução entre 100 e 1000.")
                    continue
            else:
                resolucao = 128
            
            if resolucao >= 500:
                print(f"\n[AVISO]: A resolução {resolucao}^3 exigirá processamento intenso de CPU e memória RAM.")
                print("Aguarde o cálculo ser concluído...")

            gerar_orbital_3d(n=n, l=l, m=m, resolucao_grid=resolucao)
            
            opcao = input("\nDeseja gerar outro orbital? (s/n): ").strip().lower()
            if opcao != 's':
                print("\nPrograma finalizado com sucesso.")
                break

        except ValueError:
            print("\nEntrada inválida! Digite apenas números inteiros.")
        except Exception as e:
            print(f"\nOcorreu um erro durante a execução: {e}")