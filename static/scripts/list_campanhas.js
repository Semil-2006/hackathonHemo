let campanhaSelecionada = null;
let botaoSelecionado = null;

// Função para participar da campanha
function participarCampanha(botao, nomeCampanha, tipoSanguineo) {
  campanhaSelecionada = { nome: nomeCampanha, tipo: tipoSanguineo };
  botaoSelecionado = botao;

  const modalMessage = `Você está prestes a participar da campanha:<br><strong>${nomeCampanha}</strong><br><br>Tipo sanguíneo necessário: <strong>${tipoSanguineo}</strong>`;
  document.getElementById("modalMessage").innerHTML = modalMessage;
  document.getElementById("confirmModal").classList.remove("hidden");
}

// Função para confirmar participação
function confirmarParticipacao() {
  if (campanhaSelecionada && botaoSelecionado) {
    // Altera o botão para mostrar que participou
    botaoSelecionado.innerHTML = "Participando ✓";
    botaoSelecionado.classList.remove(
      "text-red-600",
      "hover:text-red-800",
      "hover:underline"
    );
    botaoSelecionado.classList.add("text-green-600", "font-bold");
    botaoSelecionado.disabled = true;
    botaoSelecionado.onclick = null;

    // Adiciona efeito visual na linha
    const linha = botaoSelecionado.closest("tr");
    linha.classList.add("bg-green-50");

    // Mostra mensagem de sucesso
    mostrarMensagemSucesso(
      `Você agora está participando da campanha: ${campanhaSelecionada.nome}`
    );
  }

  // No final da função confirmarParticipacao() no list_campanhas.js, adicione:
  if (typeof usuarioParticipou === "function") {
    usuarioParticipou(campanhaSelecionada.nome);
  }

  fecharModal();
}

// Função para fechar modal
function fecharModal() {
  document.getElementById("confirmModal").classList.add("hidden");
  campanhaSelecionada = null;
  botaoSelecionado = null;
}

// Função para mostrar mensagem de sucesso
function mostrarMensagemSucesso(mensagem) {
  // Cria elemento de mensagem
  const mensagemDiv = document.createElement("div");
  mensagemDiv.className =
    "fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-transform duration-300";
  mensagemDiv.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            ${mensagem}
        </div>
    `;

  document.body.appendChild(mensagemDiv);

  // Remove a mensagem após 3 segundos
  setTimeout(() => {
    mensagemDiv.remove();
  }, 3000);
}

// Fechar modal ao clicar fora
document.getElementById("confirmModal").addEventListener("click", function (e) {
  if (e.target === this) {
    fecharModal();
  }
});

// Fechar modal com ESC
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    fecharModal();
  }
});
