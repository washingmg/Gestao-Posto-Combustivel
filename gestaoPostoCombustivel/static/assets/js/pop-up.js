// Fechar mensagens ao clicar no botão X
document.addEventListener('DOMContentLoaded', function() {
    const closeButtons = document.querySelectorAll('.close-btn');
    closeButtons.forEach(button => {
    button.addEventListener('click', function() {
        this.parentElement.style.display = 'none';
        document.querySelector('.message-overlay').style.display = 'none';
    });
    });
    
    // Fechar automaticamente após 5 segundos
    const messageOverlay = document.querySelector('.message-overlay');
    if (messageOverlay) {
    setTimeout(() => {
        messageOverlay.style.display = 'none';
    }, 5000);
    }
});