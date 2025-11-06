// Função para carregar um componente HTML
function carregarComponente(id, arquivo) {
  fetch(arquivo)
    .then(res => {
      if (!res.ok) throw new Error(`Erro ao carregar ${arquivo}`);
      return res.text();
    })
    .then(html => {
      document.getElementById(id).innerHTML = html;
    })
    .catch(err => console.error(err));
}

// Esperar o DOM estar pronto
document.addEventListener("DOMContentLoaded", () => {
  carregarComponente("header", "components/header.html");
  carregarComponente("footer", "components/footer.html");
  carregarComponente("apresentation", "components/apresentation.html");
  carregarComponente("content_home", "components/content_home.html");
  carregarComponente("button", "components/button.html");
  carregarComponente("welcome_text", "components/welcome_text.html")
  carregarComponente("list_campanhas", "components/list_campanhas.html")
  carregarComponente("carousel", "components/carousel.html")
  // Exemplo extra: carregarComponente("sidebar", "components/sidebar.html");
});
