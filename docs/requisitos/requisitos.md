## 1. Requisitos Funcionais 

| ID | Nome | Descrição | Critérios de Aceitação |
|----|------|-----------|----------------------|
| RF01 | Formulário de pré-triagem/cadastro | Permitir o cadastro de doadores, coletando dados pessoais e sensíveis com consentimento explícito, em conformidade com a LGPD. | - Deve haver formulário com campos obrigatórios (e-mail, telefone, cidade).<br>- Dados sensíveis (tipo sanguíneo, sexo, data de nascimento) só podem ser usados com consentimento.<br>- Cadastro pode ser salvo mesmo com recusas parciais, Termo de consentimento aceito deve ficar acessível ao doador<br>- Campos claros e objetivos.<br>- Validação de consentimento antes do envio. |
| RF02 | Gerir perfil do doador | Permitir ao doador visualizar, editar e excluir/anonimizar seus dados e consentimentos de forma segura. | - Acesso restrito mediante autenticação.<br>- Edição de todos os campos e consentimentos individuais.<br>- Opção de exclusão com confirmação e aviso de impacto.<br>- Login bloqueado após exclusão e confirmação enviada ao doador. |
| RF03 | Enviar mensagens personalizadas | Permitir segmentação e envio de mensagens apenas a doadores com consentimento ativo. | - Segmentação por tipo sanguíneo (com consentimento), cidade, interesse e classificação.<br>- Mensagens devem conter link de descadastramento.<br>- Dashboard exibe dados agregados (taxa de opt-in, número de doadores).<br>- Logs de entrega e falhas devem ser registrados<br>- Envio apenas a contatos com consentimento ativo.<br>- Registro de entregas, falhas e cancelamentos.<br>- Link de descadastramento obrigatório. |
| RF04 | Apresentar indicadores estratégicos | Exibir dashboards agregados e anonimizados com dados de doadores e campanhas para apoiar decisões de coleta. | - Indicadores: potenciais doadores por cidade, distribuição por sexo/faixa etária, taxa de opt-in por canal.<br>- Filtros por cidade e período.<br>- Tempo de carregamento ≤ 5s.<br>- Exibição de faixa de confiança estatística<br>- Exibir o status de necessidade de tipos sanguíneos, sem identificar indivíduos.<br>- Exibição visual (verde/amarelo/vermelho) para cada tipo sanguíneo.<br>- Atualização periódica de forma segura. |
| RF05 | Prever adesão por cidade | Calcular previsões de adesão a campanhas com base em dados históricos e perfis agregados. | - Exibir estimativas de comparecimento e percentuais por perfil.<br>- Incluir margem de erro e notas explicativas.<br>- Permitir simulação de cenários por data. |
| RF06 | Rankear oportunidades de coleta | Gerar ranking de cidades com maior potencial de coleta, considerando critérios configuráveis. | - Ranking deve considerar múltiplos critérios (potencial, crescimento, engajamento).<br>- Usuário pode ajustar pesos dos critérios.<br>- Destaque automático para “top cidades”. |
| RF07 | Agendamento de grupos | Permitir que multiplicadores agendem grupos de doação (mínimo 10 pessoas). | - Cadastro do grupo com data, cidade e responsável.<br>- Confirmação enviada ao multiplicador. |
| RF08 | Distribuição de conteúdo educativo | Disponibilizar informações e materiais educativos sobre doação de sangue. | - Conteúdos acessíveis publicamente no site.<br>- Organização por tema (impedimentos, preparo, mitos). |

---

## 2. Requisitos Não Funcionais (Modelo FURPS+) 

| Categoria | ID | Requisito | Descrição |
|----------|----|----------|-----------|
| Functionality | F1 | Segurança e conformidade | O sistema deve cumprir integralmente a LGPD e as políticas de segurança do GDF (PoSIC). |
|  | F2 | Controle de acesso | Usuários autenticados com perfis distintos (doador, administrador/multiplicador). |
|  | F3 | Autorização granular | Permissões específicas para visualizar, editar e excluir dados. |
| Usability | U1 | Interface responsiva | O sistema deve se adaptar a tamanhos de tela padrão de dispositivo móvel (largura máxima: 576px), tablet (largura mínima: 577px; e largura máxima: 1024px) e desktop (largura mínima: 1025px). |
|  | U2 | Acessibilidade | Conformidade com boas práticas WCAG 2.1. |
|  | U3 | Idioma | Textos em português. |
| Reliability | R1 | Integridade de dados | Garantir persistência dos dados em falhas ou interrupções. |
|  | R2 | Auditoria e rastreabilidade | Todas as ações críticas devem ser registradas em logs. |
| Performance | P1 | Tempo de resposta | Dashboards e previsões devem carregar em até 5 segundos. |
|  | P2 | Escalabilidade | Suporte a grandes volumes de dados e envio massivo simultâneo. |
| Supportability | S1 | Sustentabilidade | Custos de operação e manutenção devem ser nulos ou mínimos. |
|  | S2 | Independência de produção | O sistema deve operar sem integração com o SISTHEMO. |
|  | S3 | Atualização modular | Permitir manutenção e atualizações sem interrupção total do serviço. |
| + Constraints | C1 | Proibição de APIs internas | Nenhuma comunicação direta com sistemas internos será permitida. |
|  | C2 | Redirecionamento ao Agenda DF | Agendamentos individuais devem ocorrer exclusivamente via Agenda DF. |
|  | C3 | Proteção contra ransomware | Armazenar dados de forma criptografada e isolada de redes internas. |

---

## 3. Regras de Negócio 

1. Consentimentos devem ser explícitos, datados e versionados. 
2. O uso de canais (e-mail, SMS, telefone) só é permitido mediante autorização. 
3. Dados sensíveis (como tipo sanguíneo) só podem ser usados para segmentação com consentimento. 
4. Exclusão de conta implica remoção imediata, agendamento de exclusão definitiva (≤90 dias) e bloqueio de login. 
5. Dashboards e relatórios só podem exibir dados agregados e anonimizados. 
6. Nenhum dado individual pode ser exportado. 
7. Toda comunicação deve conter link de descadastramento. 
8. Logs de campanhas e ações do usuário devem ser registrados para auditoria. 
9. Rankings e previsões não podem identificar indivíduos. 
10. O sistema deve operar de forma independente da infraestrutura interna do Hemocentro. 

---