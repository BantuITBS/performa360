function calculateDuration() {
    const startDate = new Date(document.getElementById('startDate').value);
    const endDate = new Date(document.getElementById('endDate').value);

    if (startDate && endDate && endDate >= startDate) {
        const timeDiff = Math.abs(endDate - startDate);
        const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
        document.getElementById('duration').value = daysDiff;
    } else {
        document.getElementById('duration').value = '';
    }
}

document.getElementById('startDate').addEventListener('change', calculateDuration);
document.getElementById('endDate').addEventListener('change', calculateDuration);

document.getElementById('trackingForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const program = document.getElementById('program').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const duration = document.getElementById('duration').value;
    const progress = document.getElementById('progress').value;

    document.getElementById('resultProgram').innerText = program;
    document.getElementById('resultStartDate').innerText = startDate;
    document.getElementById('resultEndDate').innerText = endDate;
    document.getElementById('resultDuration').innerText = duration;
    document.getElementById('resultProgress').innerText = progress;

    // Update progress bar
    const progressBarFill = document.getElementById('progressBarFill');
    progressBarFill.style.width = progress + '%';

    document.getElementById('result').style.display = 'block';
    document.getElementById('trackingForm').reset();
    document.getElementById('duration').value = '';
});
