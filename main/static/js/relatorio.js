document.getElementById("imp").addEventListener("click", function () {
  window.print();
});

/*function formatPlaca() {
  var placa = document.getElementById("placaFiltro");
  placa.value = placa.value.toUpperCase();
}*/

document
  .getElementById("filtrarPlaca")
  .addEventListener("click", function () {
    var pesquisa = document.getElementById("placaFiltro").value;
    if (pesquisa.trim() !== "") {
      filtrarPlaca(pesquisa);
    } else {
      removerFiltro();
    }
  });

function filtrarPlaca(pesquisa) {
  var linhas = document.querySelectorAll("#excel-table tbody tr");
  var pesquisaLowerCase = pesquisa.toLowerCase();

  for (var i = 0; i < linhas.length; i++) {
    var pesquisaPlaca = linhas[i]
      .querySelector(".placa")
      .textContent.toLowerCase();
    var pesquisaVisitante = linhas[i]
      .querySelector(".visit")
      .textContent.toLowerCase();
    var pesquisaEmpresa = linhas[i]
      .querySelector(".empresa")
      .textContent.toLowerCase();
    if (
      pesquisaPlaca.includes(pesquisaLowerCase) ||
      pesquisaVisitante.includes(pesquisaLowerCase) ||
      pesquisaEmpresa.includes(pesquisaLowerCase)
    ) {
      linhas[i].style.display = "";
    } else {
      linhas[i].style.display = "none";
    }
  }
}

document
  .getElementById("btnFiltrar")
  .addEventListener("click", function () {
    var dataFiltro = document.getElementById("dataFiltro").value;
    if (dataFiltro.trim() !== "") {
      dataFiltro = formatarData(dataFiltro);
      filtrarPorData(dataFiltro);
    } else {
      removerFiltro();
    }
  });

function filtrarPorData(data) {
  var linhas = document.querySelectorAll("#excel-table tbody tr");

  for (var i = 0; i < linhas.length; i++) {
    var dataTd = linhas[i].querySelector(".data").textContent;
    if (dataTd !== data) {
      linhas[i].style.display = "none";
    } else {
      linhas[i].style.display = "";
    }
  }
}

function removerFiltro() {
  var linhas = document.querySelectorAll("#excel-table tbody tr");
  for (var i = 0; i < linhas.length; i++) {
    linhas[i].style.display = "";
  }
}

document.getElementById("back").addEventListener("click", function () {
  window.location.href = "/home";
});

document.addEventListener("DOMContentLoaded", function () {
  var editables = document.querySelectorAll("[contenteditable=true]");

  editables.forEach(function (editable) {
    if (
      editable.classList.contains("horaE") ||
      editable.classList.contains("horaS")
    ) {
      formatarHora(editable);
    }
    editable.addEventListener("input", function () {
      var parentRow = editable.closest("tr");
      var rowData = {
        cod: parentRow.getAttribute("data-cod"),
        nome: parentRow.getAttribute("data-nome"),
        data: parentRow.getAttribute("data-data"),
        horaE: parentRow.querySelector(".horaE").textContent,
        veic: parentRow.querySelector(".veic").textContent,
        placa: parentRow.querySelector(".placa").textContent,
        visit: parentRow.querySelector(".visit").textContent,
        rg: parentRow.querySelector(".rg").textContent,
        empresa: parentRow.querySelector(".empresa").textContent,
        horaS: parentRow.querySelector(".horaS").textContent,
        setor: parentRow.querySelector(".setor").textContent,
        obs: parentRow.querySelector(".obs").textContent,
      };

      fetch("/atualizar_dados", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(rowData),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data.message);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });
});

function formatarData(data) {
  var partes = data.split("-");
  return [partes[2], partes[1], partes[0]].join("-");
}

function formatarHora(editable) {
  var valor = editable.textContent.replace(/\D/g, "");
  var novoValor = "";
  if (valor.length >= 1) {
    novoValor += valor.substring(0, 2);
  }
  if (valor.length > 2) {
    novoValor += ":" + valor.substring(2);
  }
  editable.textContent = novoValor;
}