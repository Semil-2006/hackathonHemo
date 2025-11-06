// Função para carregar um componente HTML
function carregarComponente(id, arquivo) {
  // Retorna a promise para permitir sincronização (ex.: esperar o componente estar no DOM)
  return fetch(arquivo)
    .then(res => {
      if (!res.ok) throw new Error(`Erro ao carregar ${arquivo}`);
      return res.text();
    })
    .then(html => {
      const el = document.getElementById(id);
      if (!el) throw new Error(`Elemento com id ${id} não encontrado na página.`);
      el.innerHTML = html;
      // Dispara um evento customizado informando que este componente foi carregado
      document.dispatchEvent(new CustomEvent('componentLoaded', { detail: { id } }));
      return html;
    })
    .catch(err => {
      console.error(err);
      // Repropaga o erro para quem chamou, caso queira tratá-lo
      throw err;
    });
}

// Esperar o DOM estar pronto
document.addEventListener("DOMContentLoaded", () => {
  // Retornamos/encadeamos as promises quando necessário. A chamada padrão ainda funciona
  carregarComponente("header", "components/header.html");
  carregarComponente("footer", "components/footer.html");
  carregarComponente("apresentation", "components/apresentation.html");
  carregarComponente("content_home", "components/content_home.html");
  carregarComponente("button", "components/button.html");
  carregarComponente("welcome_text", "components/welcome_text.html");
  carregarComponente("list_campanhas", "components/list_campanhas.html");
  carregarComponente("carousel", "components/carousel.html");
  carregarComponente("about", "components/about.html");
  carregarComponente("speaking_ballon", "components/speaking_ballon.html");
  carregarComponente("questions", "components/questions.html");
  // Exemplo extra: carregarComponente("sidebar", "components/sidebar.html");
});
