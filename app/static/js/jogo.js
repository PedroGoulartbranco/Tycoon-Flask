const moeda = document.getElementById("moeda_clicavel")
let mostrar_moedas = document.getElementById("mostrar_moedas")
let paragrafo_10 = document.getElementById("top_10")
let mostrar_cliques = document.getElementById("mostrar_cliques")

let texto_multiplicador = document.getElementById("texto_multiplicador")
let botao_multiplicador = document.getElementById("botao_multiplicador")
let mostrar_multiplicador = document.getElementById("mostrar_multiplicador")
let mostrar_nivel_multiplicador = document.getElementById("mostrar_nivel_multiplicador")

let multiplicador_cliques = 0
let preco_multiplicador = 0

function atualizarTabela() {
    fetch('http://127.0.0.1:5000/top10')

    .then(response => response.json())

    .then(data => {
        paragrafo_10.innerHTML = ""
        data.forEach((usuario, indice) => {
            if (usuario.nome === usuario_logado) {
                paragrafo_10.innerHTML += ` 👉 ${indice + 1}º - ${usuario.nome} -> $${usuario.dinheiro} 👈 <br>`
            }
            else {
                paragrafo_10.innerHTML += `${indice + 1}º - ${usuario.nome} -> $${usuario.dinheiro}<br>`
            }
        });
    })

    .catch(error => console.log(error));
}


moeda.addEventListener("click", () => {
    fetch('http://127.0.0.1:5000/clique', {
    
        method: 'POST'
    
    })
    
        .then(response => response.json())
    
        .then(data => {
            mostrar_moedas.innerHTML = data.dinheiro
            mostrar_cliques.innerHTML = data.cliques
            atualizarTabela()
        })
    
})

function botao_comprar(numero_botao) {
    fetch(`http://127.0.0.1:5000/comprar/${numero_botao}`, {
    
        method: 'POST',

    
    })
    
        .then(response => response.json())
    
        .then(data => {
            console.log(data)
            if (data.sucesso == true) {
                mostrar_moedas.innerHTML = data.novo_dinheiro
                atualizar_preco_multiplicor()
            } else {
                alert("Saldo insuficiente")
            }
        })
    
        .catch(error => console.log(error));
}

function atualizar_preco_multiplicor() {
    fetch('http://127.0.0.1:5000/ver_multiplicador')
    
        .then(response => response.json())
    
        .then(data => {
            //multiplicador_cliques += data.multiplicador
            multiplicador_cliques = data.multiplicador
            preco_multiplicador = data.preco
            mostrar_multiplicador.innerHTML = `${multiplicador_cliques}x`
            botao_multiplicador.innerHTML = `R$${preco_multiplicador}`
            mostrar_nivel_multiplicador.innerHTML = `Multiplica o click <br>Nível: ${multiplicador_cliques}/10`
            if (multiplicador_cliques == 0) {
                texto_multiplicador.innerHTML = `Click ${multiplicador_cliques + 2}x`
            } else {
                alert(multiplicador_cliques)
                texto_multiplicador.innerHTML = `Click ${multiplicador_cliques + 1}x`
            }
            
        })
    
        .catch(error => console.log(error));
}

console.log(multiplicador_cliques)

atualizar_preco_multiplicor()

setInterval(atualizarTabela, 2000)

atualizarTabela()

