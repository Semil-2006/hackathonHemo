$(document).ready(function() {
    $('#cep').on('blur', function() {
        let cep = $(this).val().replace(/\D/g, '');
        if (cep.length === 8) {
            $.getJSON(`https://viacep.com.br/ws/${cep}/json/`, function(data) {
                if (!('erro' in data)) {
                    $('#endereco').val(data.logradouro);
                    $('#bairro').val(data.bairro);
                }
            });
        }
    });
});

function toggleDoacao() {
    const valor = document.getElementById("ja_doou").value;
    document.getElementById("primeiraDoacaoDiv").style.display = valor === "sim" ? "block" : "none";
    document.getElementById("interesseDiv").style.display = valor === "nao" ? "block" : "none";
}
