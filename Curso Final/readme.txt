<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de Soluções de IA da Cooperativa</title>
    <style>
        /* CSS INLINE */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f7f6;
            color: #333;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
        }

        .radar-container {
            display: flex;
            gap: 40px;
            max-width: 1400px;
            margin: 0 auto;
            background: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }

        #ai-radar-visualization {
            flex: 2;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }

        .legend-and-details {
            flex: 1;
            padding-left: 20px;
        }

        /* ESTILIZAÇÃO DO RADAR (SVG) */
        .radar-ring {
            stroke: #ccc;
            fill: none;
            stroke-dasharray: 5 5; /* Linhas pontilhadas */
        }
        
        .radar-axis {
            stroke: #aaa;
            stroke-width: 1;
        }

        /* Cores para os Horizontes - Cor da Borda do Círculo */
        .H1 { fill: #007bff; } /* Azul - Curto Prazo */
        .H2 { fill: #ffc107; } /* Amarelo - Médio Prazo */
        .H3 { fill: #dc3545; } /* Vermelho - Longo Prazo */
        
        .solution-point {
            opacity: 0.8;
            transition: all 0.2s ease-in-out;
            stroke: #333;
            stroke-width: 1.5px;
            cursor: pointer;
        }

        .solution-point:hover {
            opacity: 1;
            stroke-width: 3px;
        }

        /* ESTILIZAÇÃO DA LEGENDA */
        .legend-list {
            list-style: none;
            padding: 0;
        }

        .legend-list li {
            margin-bottom: 8px;
            font-size: 14px;
        }

        .dot {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            border: 1.5px solid #333;
        }

        #solution-details {
            margin-top: 30px;
            padding: 15px;
            border: 1px solid #eee;
            border-left: 5px solid #007bff;
            border-radius: 4px;
            min-height: 150px;
        }
        
        .tooltip {
            position: absolute;
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            padding: 5px 10px;
            border-radius: 4px;
            pointer-events: none;
            display: none;
            z-index: 1000;
            font-size: 12px;
        }
    </style>
</head>
<body>

    <header>
        <h1>Radar de Soluções de Inteligência Artificial</h1>
        <p>Posicionamento de 21 Soluções com base em **Adoção**, **Impacto** e **Maturidade (Horizonte)**.</p>
        <p style="font-size: 0.8em; color: #777;">*(O gráfico abaixo é um modelo simplificado que mapeia o Impacto no eixo X e Adoção no eixo Y.)*</p>
    </header>

    <main class="radar-container">
        <div id="ai-radar-visualization">
            </div>

        <div class="legend-and-details">
            <h2>Legenda do Radar</h2>
            <ul class="legend-list">
                <li><span class="dot H1"></span> **H1:** Curto Prazo (Alta Maturidade)</li>
                <li><span class="dot H2"></span> **H2:** Médio Prazo (Maturidade Média)</li>
                <li><span class="dot H3"></span> **H3:** Longo Prazo (Emergente)</li>
            </ul>
            
            <hr>
            
            <h2>Detalhes da Solução</h2>
            <div id="solution-details">
                <p>Passe o mouse ou clique em um ponto no radar para ver os detalhes da solução aqui.</p>
            </div>
        </div>
    </main>
    
    <div id="tooltip" class="tooltip"></div>

    <script>
        // DADOS DE TESTE (GERADOS NA INTERAÇÃO ANTERIOR)
        const aiSolutionsForTesting = [
            { name: "Databricks", adoption: "Em Uso", adoptionScore: 90, impact: "Alto", impactScore: 95, horizon: "H1", maturityScore: 90, description: "Análise de Big Data, criação de modelos preditivos e aceleração na tomada de decisão." },
            { name: "API GPT (OpenAI)", adoption: "Disponível", adoptionScore: 60, impact: "Médio/Alto", impactScore: 75, horizon: "H2", maturityScore: 60, description: "Integração de IA generativa para automação de tarefas, análise de documentos e chatbots internos." },
            { name: "Copilot Chat", adoption: "Disponível", adoptionScore: 60, impact: "Médio", impactScore: 55, horizon: "H1", maturityScore: 90, description: "Assistente geral via navegador/Teams para geração de texto, análise de reuniões e informações de mercado." },
            { name: "Copilot 365", adoption: "Disponível", adoptionScore: 60, impact: "Médio", impactScore: 55, horizon: "H1", maturityScore: 90, description: "Habilita IA no Word, Excel, PowerPoint e outros para criação, análise e automação de conteúdo." },
            { name: "Teams Premium", adoption: "Disponível", adoptionScore: 60, impact: "Médio", impactScore: 55, horizon: "H1", maturityScore: 90, description: "Otimização de reuniões com resumos inteligentes, tagueamento, segurança e legendas com tradução." },
            { name: "GitHub Copilot", adoption: "Em Uso", adoptionScore: 90, impact: "Alto", impactScore: 95, horizon: "H1", maturityScore: 90, description: "Assistente de IA para desenvolvimento de software, aumentando a produtividade e qualidade do código." },
            { name: "API do OCR", adoption: "Em Uso", adoptionScore: 90, impact: "Alto", impactScore: 95, horizon: "H1", maturityScore: 90, description: "Automação da extração de dados de documentos, acelerando processos como abertura de contas e crédito." },
            { name: "IA Generativa na Base de Conhecimento", adoption: "Em Uso", adoptionScore: 90, impact: "Médio/Alto", impactScore: 75, horizon: "H2", maturityScore: 60, description: "Aplica IA generativa aos documentos (ServiceNow) para reduzir tempo de busca e elaborar resumos assertivos." },
            { name: "Vitrine de Modelos", adoption: "Disponível", adoptionScore: 60, impact: "Médio/Alto", impactScore: 75, horizon: "H2", maturityScore: 60, description: "Compartilhamento de modelos de ML homologados para democratizar o uso e acelerar a aplicação de inteligência preditiva." },
            { name: "Portal Rag", adoption: "Disponível", adoptionScore: 60, impact: "Médio", impactScore: 55, horizon: "H2", maturityScore: 60, description: "Uso de IA Generativa e RAG para buscas e geração de informações em arquivos, customizando respostas da IA." },
            { name: "Fala Diana", adoption: "Piloto (Beta)", adoptionScore: 30, impact: "Médio", impactScore: 55, horizon: "H3", maturityScore: 30, description: "Plataforma de dados conversacionais para interagir com informações do Hyperion de forma ágil." },
            { name: "IA integrada ao Gupy", adoption: "Em Uso", adoptionScore: 90, impact: "Médio/Alto", impactScore: 75, horizon: "H1", maturityScore: 90, description: "Automação e otimização do recrutamento e seleção, identificando candidatos com maior aderência." },
            { name: "Copilot Studio", adoption: "Disponível", adoptionScore: 60, impact: "Médio", impactScore: 55, horizon: "H3", maturityScore: 30, description: "Ferramenta para criação de agentes inteligentes personalizados (copilotos) sem necessidade de programação avançada." },
            { name: "Power Automate com IA", adoption: "Em Uso", adoptionScore: 90, impact: "Médio/Alto", impactScore: 75, horizon: "H1", maturityScore: 90, description: "Automação de processos rotineiros, integrando OCR, classificação de dados e análise de sentimentos." },
            { name: "Modelo Biribinha - Analista de Crédito Virtual", adoption: "Em Uso", adoptionScore: 90, impact: "Alto", impactScore: 95, horizon: "H1", maturityScore: 90, description: "Análise e concessão de crédito 100% automática, com redução de até 99% no tempo do fluxo." },
            { name: "Crédito Fácil com IA", adoption: "Em Uso", adoptionScore: 90, impact: "Alto", impactScore: 95, horizon: "H1", maturityScore: 90, description: "Definição de valores e limites de crédito com redução de 66% na inadimplência e aumento na concessão." },
            { name: "Modelos de Propensão para Consórcios", adoption: "Em Uso", adoptionScore: 90, impact: "Alto", impactScore: 95, horizon: "H1", maturityScore: 90, description: "Identificação de associados com maior propensão à contratação, qualificando leads e aumentando a eficiência comercial." },
            { name: "MIA (Monest IA)", adoption: "Em Uso", adoptionScore: 90, impact: "Alto", impactScore: 95, horizon: "H1", maturityScore: 90, description: "Ferramenta para recuperação de crédito, analisando perfis e sugerindo acordos personalizados para aumentar as taxas de recuperação." },
            { name: "Canva IA", adoption: "Disponível", adoptionScore: 60, impact: "Médio", impactScore: 55, horizon: "H2", maturityScore: 60, description: "Funcionalidades de IA para criação visual rápida (Magic Write, geração de imagens, remoção de fundos)." },
            { name: "TheoGPT", adoption: "Em Uso", adoptionScore: 90, impact: "Médio", impactScore: 55, horizon: "H1", maturityScore: 90, description: "Assistente virtual conversacional para colaboradores sobre produtos, serviços e processos internos." },
            { name: "Perplexity.AI", adoption: "Disponível", adoptionScore: 60, impact: "Baixo/Médio", impactScore: 35, horizon: "H3", maturityScore: 30, description: "Plataforma de busca baseada em IA que apresenta resumos concisos com fontes citadas, ideal para pesquisa." }
        ];

        const config = {
            w: 600, // Largura total do SVG
            h: 600, // Altura total do SVG
            padding: 50, // Margem interna
            maxScore: 100, // Pontuação máxima
            numRings: 4 // Número de anéis (níveis)
        };

        function drawRadar(data, cfg) {
            const container = document.getElementById('ai-radar-visualization');
            container.innerHTML = '';
            
            const width = cfg.w;
            const height = cfg.h;
            const radius = (Math.min(width, height) / 2) - cfg.padding;
            const center = { x: width / 2, y: height / 2 };

            // 1. Cria o SVG principal
            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute('width', width);
            svg.setAttribute('height', height);
            container.appendChild(svg);
            
            // 2. Cria o grupo para centralizar o radar
            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
            g.setAttribute('transform', `translate(${cfg.padding}, ${cfg.padding})`);
            svg.appendChild(g);

            // 3. Desenha os Anéis (Círculos) e Rótulos
            for (let i = 1; i <= cfg.numRings; i++) {
                const r = radius * (i / cfg.numRings);
                
                // Anel
                const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                circle.setAttribute('cx', center.x - cfg.padding);
                circle.setAttribute('cy', center.y - cfg.padding);
                circle.setAttribute('r', r);
                circle.setAttribute('class', 'radar-ring');
                g.appendChild(circle);
                
                // Rótulo de Score (ex: 25, 50, 75)
                const scoreLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
                scoreLabel.setAttribute('x', center.x - cfg.padding + r + 5);
                scoreLabel.setAttribute('y', center.y - cfg.padding - 5);
                scoreLabel.setAttribute('font-size', '10px');
                scoreLabel.setAttribute('fill', '#999');
                scoreLabel.textContent = Math.round((i / cfg.numRings) * cfg.maxScore);
                g.appendChild(scoreLabel);
            }
            
            // 4. Desenha os Eixos de Referência
            const axes = [
                { name: "Adoção (Y)", angle: -90 }, // Para cima
                { name: "Impacto (X)", angle: 0 }    // Para direita
            ];
            
            axes.forEach(axis => {
                const axisLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
                axisLine.setAttribute('x1', center.x - cfg.padding);
                axisLine.setAttribute('y1', center.y - cfg.padding);
                
                // Ponto final (simplificado para ir até a borda)
                const x2 = center.x - cfg.padding + radius * Math.cos(axis.angle * Math.PI / 180);
                const y2 = center.y - cfg.padding + radius * Math.sin(axis.angle * Math.PI / 180);

                axisLine.setAttribute('x2', x2);
                axisLine.setAttribute('y2', y2);
                axisLine.setAttribute('class', 'radar-axis');
                g.appendChild(axisLine);
                
                // Rótulo do Eixo
                const axisLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
                axisLabel.setAttribute('x', x2 + (axis.angle === 0 ? 10 : 0));
                axisLabel.setAttribute('y', y2 + (axis.angle === -90 ? -10 : 10));
                axisLabel.setAttribute('fill', '#333');
                axisLabel.setAttribute('font-weight', 'bold');
                axisLabel.textContent = axis.name;
                g.appendChild(axisLabel);
            });


            // 5. Renderiza os PONTOS (Soluções)
            data.forEach(solution => {
                // Cálculo das Coordenadas (Simplificado: Impacto em X, Adoção em Y)
                
                // Normaliza o score de 0-100 para o raio (0-1) e multiplica pelo raio do radar.
                const r_impact = radius * (solution.impactScore / cfg.maxScore);
                const r_adoption = radius * (solution.adoptionScore / cfg.maxScore);

                // Mapeamento em um Quadrante (0,0 é o centro, 100,100 é o canto superior direito)
                // Usaremos um mapeamento em coordenadas retangulares dentro do círculo para simplificar:
                // X (Impacto): Mapeado de 0 a Radius
                // Y (Adoção): Mapeado de 0 a Radius
                
                // Calculando as posições:
                const cx = center.x - cfg.padding + r_impact;
                const cy = center.y - cfg.padding - r_adoption; // Subtrai porque Y=0 é o topo do SVG
                
                // Raio do Ponto (Variável pela Maturidade/Horizonte)
                const pointRadius = 7 + (solution.maturityScore / 100) * 3; // Ponto varia entre 7 e 10
                
                const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                circle.setAttribute('cx', cx);
                circle.setAttribute('cy', cy);
                circle.setAttribute('r', pointRadius);
                circle.setAttribute('class', `solution-point ${solution.horizon}`);
                circle.setAttribute('data-name', solution.name);
                
                // Adiciona a lógica de interatividade
                circle.addEventListener('mouseover', (e) => showTooltip(e, solution.name));
                circle.addEventListener('mousemove', (e) => moveTooltip(e));
                circle.addEventListener('mouseout', hideTooltip);
                circle.addEventListener('click', () => showDetails(solution));
                
                g.appendChild(circle);
                
                // Rótulo da Solução (Opcional, para não poluir o gráfico)
                /*
                const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
                label.setAttribute('x', cx + pointRadius + 2);
                label.setAttribute('y', cy + 5);
                label.setAttribute('font-size', '10px');
                label.setAttribute('fill', '#333');
                label.textContent = solution.name.split(' ')[0]; // Apenas a primeira palavra
                g.appendChild(label);
                */
            });
        }

        // --- Funções de Interatividade ---
        
        function showDetails(solution) {
            const detailsDiv = document.getElementById('solution-details');
            detailsDiv.innerHTML = `
                <h3 style="color: var(--color-h${solution.horizon.slice(1)});">${solution.name}</h3>
                <p><strong>Fase de Adoção:</strong> ${solution.adoption} (${solution.adoptionScore}%)</p>
                <p><strong>Impacto no Negócio:</strong> ${solution.impact} (${solution.impactScore}%)</p>
                <p><strong>Horizonte/Maturidade:</strong> ${solution.horizon} (${solution.maturityScore}%)</p>
                <p>${solution.description}</p>
            `;
            // Atualiza a cor da borda de destaque
            detailsDiv.style.borderLeftColor = getComputedStyle(document.documentElement).getPropertyValue(`--color-h${solution.horizon.slice(1)}`) || '';
        }

        const tooltip = document.getElementById('tooltip');

        function showTooltip(e, name) {
            tooltip.textContent = name;
            tooltip.style.display = 'block';
            moveTooltip(e);
        }

        function moveTooltip(e) {
            // Posiciona o tooltip próximo ao cursor
            tooltip.style.left = (e.pageX + 15) + 'px';
            tooltip.style.top = (e.pageY - 25) + 'px';
        }

        function hideTooltip() {
            tooltip.style.display = 'none';
        }
        
        // Inicializa o Radar
        document.addEventListener('DOMContentLoaded', () => {
             // Define as variáveis CSS para as cores (para uso na função showDetails)
            document.documentElement.style.setProperty('--color-h1', '#007bff');
            document.documentElement.style.setProperty('--color-h2', '#ffc107');
            document.documentElement.style.setProperty('--color-h3', '#dc3545');

            drawRadar(aiSolutionsForTesting, config);
        });
    </script>
</body>
</html>

