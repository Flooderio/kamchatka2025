document.querySelectorAll('.activity input').forEach(option => {
  option.addEventListener('change', function() {
    const activityId = this.closest('.activity').id.split('-')[1];
    const transportDiv = document.getElementById(`transport-for-${activityId}`);
    transportDiv.style.display = this.checked ? 'block' : 'none';
  });
});
