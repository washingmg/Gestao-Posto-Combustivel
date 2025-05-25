# ✈ Sistema de Passagens Aéreas

Desenvolvedores: Jhony Santos, Karleandro Silva, Lucas Farias, Rian Carlos, Washington Gaia.

---

## 📌 Descrição

Este projeto consiste em um **Sistema de Gestão de Postos de Combustível**, desenvolvido pelos discentes do curso de Ciência da Computação - UFAL Arapiraca, com foco acadêmico para simular a operação de uma plataforma de gerenciamento e vendas de combustiveis: Gasolina, Adtivada, Etanol e Diesel. Utiliza estórias de usuários para facilitar na construção de funções relevantes para o sistema.

O sistema foi desenvolvido com base nos princípios da arquitetura MVT, cuja abordagem é utilizada em Django para organizar a base de dados e o fluxo de trabalho em Desenvolvimeto Web. O padrão MVT é composta por **model**, **view** e **template**, que tornam o sistema mais robusto, organizado e seguro.

---

## 🛠️ Funcionalidades

1. **Realizar venda**:
   - O sistema será operado sob a perspectiva do funcionário e disponibilizará quatro tipos de combustíveis. Cada cum possui um preço específico. No momento da venda, o funcionário informará a quantidade, em litros, do combustível escolhido. O sistema calculará automaticamente o valor total, multiplicando a quantidade pelo preço correspondente. O pagamento poderá ser realizado em dinheiro, cartão (crédito/débito) e pix.
2. **Reabastecer**:
   - Cada bomba contará com dois tanques de combustível. À medida que as vendas forem realizadas, o nível dos tanques será reduzido. O sistema utilizará três cores — verde, amarelo e vermelho — para representar os diferentes níveis de combustível. Quando um tanque atingir o nível vermelho, indicando baixo volume, será necessário realizar o reabastecimento.
3. **Gerar Relatório**:
   - Será gerado um relatório em formato de tabela, contendo informações detalhadas sobre as vendas realizadas. Serão exibidos: data e hora da venda, bomba utilizada (A, B, C ou D), tipo de combustível, quantidade vendida em litros, forma de pagamento e o valor a ser pago (calculado com base na quantidade de litros). No canto inferior direito da tabela, será apresentado o valor total arrecadado.

---

## 💻 Tecnologias Utilizadas

1. **Linguagem Principal**: Python  
2. **Banco de Dados**: SQLite3  
3. **Front-End**: HTML, CSS e Javascript  
   - **3.1.** Linguagem de marcação: HTML  
   - **3.2.** Estilização: CSS  
   - **3.3.** Manipulação: Javascript para manipular o HTML e CSS  
4. **Back-End**: Framework Django (usado para estabelecer a comunicação com o banco de dados)  
5. **Sistema Operacional**: Compatível com Windows e Linux  

---

## 📂 Estrutura do Projeto
(Em desenvolvimento)
