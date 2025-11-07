## [cite_start]3. Requisitos Funcionais [cite: 26]

| ID | Nome | Descrição | Critérios de Aceitação |
| :--- | :--- | :--- | :--- |
| **RF01** | Formulário de pré-triagem/cadastro | [cite_start]Permitir o **cadastro de doadores**, coletando dados pessoais e sensíveis com **consentimento explícito**, em conformidade com a LGPD[cite: 27]. | [cite_start]Deve haver formulário com campos obrigatórios (**e-mail, telefone, cidade**)[cite: 27]. [cite_start]Dados sensíveis (tipo sanguíneo, sexo, data de nascimento) só podem ser usados com consentimento[cite: 27]. [cite_start]Cadastro pode ser salvo mesmo com recusas parciais[cite: 27]. [cite_start]Termo de consentimento aceito deve ficar acessível ao doador[cite: 27]. [cite_start]Validação de consentimento antes do envio[cite: 27]. |
| **RF02** | Gerir perfil do doador | [cite_start]Permitir ao doador visualizar, editar e **excluir/anonimizar seus dados e consentimentos** de forma segura[cite: 28]. | [cite_start]Acesso restrito mediante autenticação[cite: 28]. [cite_start]Edição de todos os campos e consentimentos individuais[cite: 28]. [cite_start]Opção de **exclusão com confirmação e aviso de impacto**[cite: 28]. [cite_start]Login bloqueado após exclusão e confirmação enviada ao doador[cite: 28]. |
| **RF03** | Enviar mensagens personalizadas | [cite_start]Permitir **segmentação e envio de mensagens** apenas a doadores com **consentimento ativo**[cite: 28]. | [cite_start]Segmentação por tipo sanguíneo (com consentimento), cidade, interesse e classificação[cite: 28]. [cite_start]Mensagens devem conter **link de descadastramento**[cite: 28]. [cite_start]Envio apenas a contatos com consentimento ativo[cite: 28]. [cite_start]Registro de entregas, falhas e cancelamentos[cite: 28]. [cite_start]Link de descadastramento obrigatório[cite: 28]. |
| **RF04** | Apresentar indicadores estratégicos | [cite_start]Exibir **dashboards agregados e anonimizados** com dados de doadores e campanhas para apoiar decisões de coleta[cite: 28]. | [cite_start]Indicadores: potenciais doadores agregados por cidade, distribuição por sexo/faixa etária, taxa de *opt-in* por canal[cite: 28]. [cite_start]Filtros por cidade e período[cite: 28]. [cite_start]Tempo de carregamento **≤ 5s**[cite: 28]. [cite_start]Exibir faixa de confiança estatística[cite: 28]. [cite_start]Exibir o **status de necessidade de tipos sanguíneos** (verde/amarelo/vermelho), sem identificar indivíduos[cite: 28]. |
| **RF05** | Rankear oportunidades de coleta | [cite_start]Gerar **ranking de cidades** com maior potencial de coleta, considerando critérios configuráveis[cite: 28]. | [cite_start]Ranking deve considerar múltiplos critérios (potencial, crescimento, engajamento)[cite: 28]. [cite_start]Usuário pode **ajustar pesos dos critérios**[cite: 28]. [cite_start]Destaque automático para "top cidades"[cite: 28]. |
| **RF06** | Prever adesão | [cite_start]Calcular **previsões de adesão a campanhas por cidade** com base em dados históricos e perfis agregados[cite: 28]. | [cite_start]Exibir estimativas de comparecimento e percentuais por perfil[cite: 28]. [cite_start]Incluir margem de erro e notas explicativas[cite: 28]. [cite_start]Permitir simulação de cenários por data[cite: 28]. |
| **RF07** | Agendamento de grupos | [cite_start]Permitir que **multiplicadores agendem grupos de doação** (**mínimo 10 pessoas**)[cite: 29]. | [cite_start]Cadastro do grupo com data, cidade e responsável[cite: 29]. [cite_start]Confirmação enviada ao multiplicador[cite: 29]. |
| **RF08** | Distribuição de conteúdo educativo | [cite_start]Disponibilizar informações e **materiais educativos** sobre doação de sangue[cite: 29]. | [cite_start]Conteúdos **acessíveis publicamente no site**[cite: 29]. [cite_start]Organização por tema (impedimentos, preparo, mitos)[cite: 29]. |

---

## [cite_start]4. Requisitos Não Funcionais (Modelo FURPS+) [cite: 30]

| Categoria | ID | Requisito | Descrição |
| :--- | :--- | :--- | :--- |
| **Functionality** | F1 | Segurança e conformidade | [cite_start]O sistema deve cumprir integralmente a **LGPD** e as políticas de segurança do GDF (**POSIC**)[cite: 31]. |
| | F2 | Controle de acesso | [cite_start]Usuários autenticados com **perfis distintos** (doador, administrador/multiplicador)[cite: 31]. |
| | F3 | Autorização granular | [cite_start]Permissões específicas para visualizar, editar e excluir dados[cite: 31]. |
| **Usability** | U1 | Interface responsiva | [cite_start]O sistema deve se adaptar a tamanhos de tela padrão de **dispositivo móvel, tablet e desktop**[cite: 31]. |
| | U2 | Acessibilidade | [cite_start]Conformidade com boas práticas **WCAG 2.1**[cite: 31]. |
| | U3 | Idioma | [cite_start]Textos em **português**[cite: 31]. |
| **Reliability** | R1 | Integridade de dados | [cite_start]Garantir **persistência dos dados** em falhas ou interrupções[cite: 31]. |
| | R2 | Auditoria e rastreabilidade | [cite_start]Todas as ações críticas devem ser **registradas em logs**[cite: 31]. |
| **Performance** | P1 | Tempo de resposta | [cite_start]Dashboards e previsões devem carregar em **até 5 segundos**[cite: 32]. |
| | P2 | Escalabilidade | [cite_start]Suporte a **grandes volumes de dados** e envio massivo simultâneo[cite: 32]. |
| **Supportability** | S1 | Sustentabilidade | [cite_start]**Custos de operação e manutenção devem ser nulos ou mínimos**[cite: 32]. |
| | S2 | Independência de produção | [cite_start]O sistema deve operar **sem integração com o SISTHEMO**[cite: 32]. |
| | S3 | Atualização modular | [cite_start]Permitir manutenção e atualizações **sem interrupção total do serviço**[cite: 32]. |
| **+ Constraints** | C1 | Proibição de APIs internas | [cite_start]**Nenhuma comunicação direta com sistemas internos** será permitida[cite: 32]. |
| | C2 | Redirecionamento ao Agenda DF | [cite_start]Agendamentos individuais devem ocorrer **exclusivamente via Agenda DF**[cite: 32]. |
| | C3 | Proteção contra ransomware | [cite_start]Armazenar dados de forma **criptografada e isolada de redes internas**[cite: 32]. |

---

## [cite_start]5. Regras de Negócio [cite: 33]
1.  [cite_start]**Consentimentos devem ser explícitos, datados e versionados**[cite: 34].
2.  [cite_start]O uso de canais (e-mail, SMS, telefone) só é permitido mediante autorização[cite: 35, 36].
3.  [cite_start]Dados sensíveis (como tipo sanguíneo) só podem ser usados para segmentação com consentimento[cite: 37, 38].
4.  [cite_start]Exclusão de conta implica **remoção imediata**, agendamento de exclusão definitiva (≤90 dias) e bloqueio de login[cite: 39].
5.  [cite_start]Dashboards e relatórios só podem exibir **dados agregados e anonimizados**[cite: 40, 41, 43].
6.  [cite_start]**Nenhum dado individual pode ser exportado**[cite: 44].
7.  [cite_start]Toda comunicação deve conter **link de descadastramento**[cite: 45].
8.  [cite_start]**Logs de campanhas e ações do usuário** devem ser registrados para auditoria[cite: 46].
9.  [cite_start]Rankings e previsões **não podem identificar indivíduos**[cite: 47].
10. [cite_start]O sistema deve operar de forma **independente da infraestrutura interna** do Hemocentro[cite: 48].

---

## [cite_start]6. Conclusão [cite: 49]