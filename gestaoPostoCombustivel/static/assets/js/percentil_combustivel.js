// Script para calcular e exibir a porcentagem de combustível

document.addEventListener('DOMContentLoaded', function () {
    const fuelElements = document.querySelectorAll('.fuel');

    fuelElements.forEach(fuelElement => {
    const quantidadeDisponivel = parseFloat(fuelElement.dataset.quantidadeDisponivel);
    const capacidadeMaxima = parseFloat(fuelElement.dataset.capacidadeMaxima);

    let porcentagem = 0;
    if (capacidadeMaxima > 0) {
        porcentagem = (quantidadeDisponivel / capacidadeMaxima) * 100;
        porcentagem = Math.min(porcentagem, 100); 
        porcentagem = Math.round(porcentagem); 
    }

    const barElement = fuelElement.querySelector('.bar');
    const percentageElement = fuelElement.querySelector('.percentage');

    
    barElement.style.width = porcentagem + '%';

    if (porcentagem <= 25) {
    barElement.classList.add('critical');    
    // alert('⚠️ Nível crítico de combustível! Porcentagem abaixo de 25%.');
    } else if (porcentagem <= 49) {
    barElement.classList.add('orange');      
    } else if (porcentagem <= 75) {
    barElement.classList.add('yellow');      
    } else {
    barElement.classList.add('normal');      
    }
    
    percentageElement.textContent = porcentagem + '%';
    });
});