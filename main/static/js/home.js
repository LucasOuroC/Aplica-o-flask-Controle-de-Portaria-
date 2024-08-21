function formatPlaca(){
  var placa = document.getElementById('placa')
  placa.value = placa.value.toUpperCase()
} 

function characterCount(){
  var textarea = document.getElementById('obs')
  var charCount = document.getElementById('cont')
  charCount.textContent =  textarea.value.length + '/500 caracteres'
}

function rgMask(event) {
  let Rg = event.target.value;

  if (Rg !== null) {
    Rg = Rg.replace(/\D/g, "");

    Rg = Rg.replace(/^(\d{3})(\d)/, "$1.$2");
    Rg = Rg.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
    Rg = Rg.replace(/^(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");
  }

  event.target.value = Rg;
}

document.getElementById("imp").addEventListener("click", function () {
  window.location.href = "/relatorio";
});

const campoRg = document.getElementById("Rg");

campoRg.addEventListener("input", rgMask);