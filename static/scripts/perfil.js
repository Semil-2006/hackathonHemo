// Espera o DOM carregar antes de rodar
document.addEventListener("DOMContentLoaded", () => {
    
    // 1. Carrega os componentes (header/footer)
    if (typeof loadComponent === 'function') {
        
        // Carrega os componentes globais
        loadComponent("header", "components/header.html");
        loadComponent("footer", "components/footer.html");

    } else {
        console.error("A função 'loadComponent' não foi encontrada. Verifique se 'global.js' está sendo carregado corretamente.");
    }
    
    // 2. Chama a função opcional para carregar os dados do perfil (se existir)
    if (typeof carregarDadosDoPerfil === 'function') {
        try {
            carregarDadosDoPerfil();
        } catch (err) {
            console.error('Erro ao executar carregarDadosDoPerfil():', err);
        }
    }
    
    // 3. Configura handlers para edição do perfil (se existirem os botões)
    const editBtn = document.getElementById('edit-button');
    const saveBtn = document.getElementById('save-button');
    const cancelBtn = document.getElementById('cancel-button');

    function toggleEditMode(on) {
        document.querySelectorAll('.view-only').forEach(el => {
            el.style.display = on ? 'none' : '';
        });
        document.querySelectorAll('.edit-only').forEach(el => {
            el.style.display = on ? '' : 'none';
        });
        if (editBtn) editBtn.style.display = on ? 'none' : '';
        if (saveBtn) saveBtn.style.display = on ? '' : 'none';
        if (cancelBtn) cancelBtn.style.display = on ? '' : 'none';
    }

    if (editBtn) {
        editBtn.addEventListener('click', () => toggleEditMode(true));
    }
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            // Reload the page to discard unsaved changes
            window.location.reload();
        });
    }
    // saveBtn is a submit button inside the form; no handler needed here
});
