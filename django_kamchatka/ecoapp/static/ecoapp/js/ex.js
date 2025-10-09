
document.querySelectorAll('input[name="tours"]').forEach(function(checkbox) {
  checkbox.addEventListener('change', function() {
    const transportDiv = document.getElementById('transport-for-' + checkbox.value);
    if (transportDiv) {
      transportDiv.style.display = checkbox.checked ? 'inline-block' : 'none';
    }
  });
});
