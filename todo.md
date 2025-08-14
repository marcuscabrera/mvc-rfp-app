## Tarefas do Projeto SaaS de Automação de Respostas a RFPs

### Fase 1: Análise de requisitos e planejamento da arquitetura
- [ ] Ler e compreender os requisitos detalhados do projeto (já feito).
- [x] Criar um documento de visão geral e justificativa.
- [x] Detalhar a arquitetura de alto nível (backend, frontend, AI/ML, base de dados, autenticação).
- [x] Descrever fluxos de autenticação SSO com Azure EntraID.
- [x] Indicar integrações AI (Gemini API como primária, Gemma 3n como fallback/contextual).
- [x] Incluir um diagrama de componentes e um de fluxo do usuário (em Markdown pseudo-code ou descrição textual).

### Fase 2: Modelagem de dados e design da API
- [x] Listar as principais entidades, atributos, relacionamentos e regras.
- [x] Descrever as constraints essenciais e sugestões de indexes em bancos SQL.
- [x] Definir os endpoints da API REST.

### Fase 3: Desenvolvimento do backend Flask
- [x] Configurar o ambiente de desenvolvimento Flask.
- [x] Implementar os endpoints críticos (Login via EntraID, Upload de documentos, Extração de perguntas, Geração de respostas).
- [x] Implementar fallback de modelos de IA.

### Fase 4: Desenvolvimento do frontend React
- [x] Configurar o ambiente de desenvolvimento React.
- [x] Modelar o front-end de um chat interativo para geração e edição de respostas.

### Fase 5: Implementação de autenticação e segurança
- [x] Implementar autenticação SSO com Azure EntraID.
- [ ] Implementar políticas de segurança (MFA, SSO, log auditing, etc.).

### Fase 6: Integração com IA e processamento de documentos
- [ ] Integrar com Gemini API para extração de perguntas e geração de respostas.
- [ ] Integrar com Gemma 3n como fallback/contextual.
- [ ] Implementar processamento de documentos.

### Fase 7: Configuração de infraestrutura e deploy
- [ ] Fornecer um checklist de variáveis de ambiente obrigatórias.
- [ ] Explicar a configuração inicial do Azure EntraID, Gemini API e Gemma 3n.
- [ ] Descrever o pipeline de CI/CD.

### Fase 8: Implementação de testes automatizados
- [ ] Modelar estratégias de testes automatizados (unitários, integração, mocks para external APIs).
- [ ] Listar comandos básicos para rodar a suíte de testes e validação do código.

### Fase 9: Documentação técnica e de usuário
- [ ] Gerar um README inicial detalhado.
- [ ] Explicar como contribuir e abrir issues/PRs.
- [ ] Apresentar exemplos de uso dos principais endpoints.
- [ ] Documentar a arquitetura, modelagem de dados, stack tecnológica, exemplos de código, configuração e testes.

### Fase 10: Entrega final e demonstração
- [ ] Preparar a entrega final do sistema e da documentação.
- [ ] Realizar uma demonstração do sistema.

