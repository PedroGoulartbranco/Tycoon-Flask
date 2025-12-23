const moeda = document.getElementById("moeda_clicavel")
let mostrar_moedas = document.getElementById("mostrar_moedas")
let paragrafo_10 = document.getElementById("top_10")
let mostrar_cliques = document.getElementById("mostrar_cliques")

let texto_multiplicador = document.getElementById("texto_multiplicador")
let botao_multiplicador = document.getElementById("botao_multiplicador")
let mostrar_multiplicador = document.getElementById("mostrar_multiplicador")
let mostrar_nivel_multiplicador = document.getElementById("mostrar_nivel_multiplicador")

let texto_automatico_titulo = document.getElementById("texto_automatico_titulo")
let mostrar_nivel_automatico = document.getElementById("mostrar_nivel_automatico")
let mostrar_automatico_info = document.getElementById("mostrar_automatico_info")
let botao_comprar_automatico_html = document.getElementById("botao_comprar_automatico")

let multiplicador_cliques = 0
let preco_multiplicador = 0

let preco_automatico = 0
let numero_de_automaticos = 0

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


moeda.addEventListener("click", (evento) => {
    fetch('http://127.0.0.1:5000/clique', {
    
        method: 'POST'
    
    })
    
        .then(response => response.json())
    
        .then(data => {
            mostrar_moedas.innerHTML = data.dinheiro
            mostrar_cliques.innerHTML = data.cliques

            mostrar_numerozinho = document.createElement("div")
            mostrar_numerozinho.className = "numero-flutuante"
            mostrar_numerozinho.innerHTML = `+${data.valor_clique}`

            mostrar_numerozinho.style.left = `${evento.pageX - 10}px`
            mostrar_numerozinho.style.top = `${evento.pageY - 10}px`

            document.body.appendChild(mostrar_numerozinho)

            setTimeout(() => {
                mostrar_numerozinho.remove();
            }, 800);

            atualizarTabela()
        })
    
})

function botao_comprar(numero_botao) {
    fetch(`http://127.0.0.1:5000/comprar/${numero_botao}`, {
    
        method: 'POST',

    
    })
    
        .then(response => response.json())
    
        .then(data => {
            atualizar_dinheiro()
            if (data.sucesso == true) {
                mostrar_moedas.innerHTML = data.novo_dinheiro
                atualizar_preco_multiplicor()
            } else {
                alert(data.erro)
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
            mostrar_multiplicador.innerHTML = `${multiplicador_cliques + 1}x`
            if (multiplicador_cliques == 10){
                botao_multiplicador.innerHTML = `Máximo`
                botao_multiplicador.classList = 'btn btn-success'
            } else {
                botao_multiplicador.innerHTML = `R$${preco_multiplicador}`
            }
            mostrar_nivel_multiplicador.innerHTML = `Multiplica o click <br>Nível: ${multiplicador_cliques + 1}/10`
            if (multiplicador_cliques == 0) {
                texto_multiplicador.innerHTML = `Click ${multiplicador_cliques + 2}x`
            } else if (multiplicador_cliques == 10) {
                 texto_multiplicador.innerHTML = `Click 10x Máximo Alcançado`
            }
            else {
                texto_multiplicador.innerHTML = `Click ${multiplicador_cliques + 2}x`
            }
            
        })
    
        .catch(error => console.log(error));
}

function botao_comprar_automatico() {
    fetch('http://127.0.0.1:5000/comprar_clique_automatico', {
    
        method: 'POST'
    
    })
    
        .then(response => response.json())
    
        .then(data => {
            atualizar_dinheiro()
            if (data.sucesso == true) {
                mostrar_moedas.innerHTML = data.novo_dinheiro
                atualizar_preco_do_automatico()
            } else {
                alert(data.erro)
            }
        })
    
        .catch(error => console.log(error));
}

function atualizar_preco_do_automatico(){
    fetch('http://127.0.0.1:5000/ver_automaticos_1')
    
        .then(response => response.json())
    
        .then(data => {
            numero_de_automaticos = data.numero_automatico
            preco_automatico = data.preco
            
            if (numero_de_automaticos >= 10) {
                botao_comprar_automatico_html.innerHTML = `Máximo`
                texto_automatico_titulo.innerHTML = `Automático 10x Alcançado`
                botao_comprar_automatico_html.classList = 'btn btn-success'
            } else {
                botao_comprar_automatico_html.innerHTML = `R$${preco_automatico}`
                texto_automatico_titulo.innerHTML = `Automático ${numero_de_automaticos + 1}x`
            }

            mostrar_automatico_info.innerHTML = `${numero_de_automaticos}`
            mostrar_nivel_automatico.innerHTML = `Clique Automático <br>Nível ${numero_de_automaticos}/10`
        })
    
        .catch(error => console.log(error));
}

setInterval(() => { 
    if (numero_de_automaticos > 0) {
        let dinheiro_na_tela = parseInt(mostrar_moedas.innerHTML)
        mostrar_moedas.innerHTML = dinheiro_na_tela + numero_de_automaticos
    }
}, 1000)

function atualizar_dinheiro() {
    fetch('http://127.0.0.1:5000/atualizar_dinheiro')
    
        .then(response => response.json())
    
        .then(data => {
            mostrar_moedas.innerHTML = data.dinheiro
            if (data.tempo_off >= 1) {
                alert(`Você ficou ${data.tempo_off} fora, você ganhou ${data.dinheiro}`)
            } 
        })
    
        .catch(error => console.log(error));
}

setInterval(atualizar_dinheiro, 20000)

atualizar_preco_do_automatico()
atualizar_dinheiro()

atualizar_preco_multiplicor()

setInterval(atualizarTabela, 2000)

atualizarTabela()

