// main.js
// Send a GET request to the /JobSpy endpoint in backend.py

document.addEventListener('DOMContentLoaded', function() {
  const jobForm = document.getElementById('job-form');
  const spinner = document.getElementById('loading-spinner'); // Use the spinner from HTML

  if (jobForm) {
    jobForm.addEventListener('submit', function(event) {
      event.preventDefault(); // Prevent form from submitting normally

      spinner.style.display = 'block'; // Show spinner

      // Collect form data
      const formData = new FormData(jobForm);
      const data = {};

      // Handle checkboxes with same name (site_name)
      data.site_name = [];
      for (const [key, value] of formData.entries()) {
        if (key === 'site_name') {
          data.site_name.push(value);
        } else if (key in data) {
          // For other repeated keys
          if (!Array.isArray(data[key])) data[key] = [data[key]];
          data[key].push(value);
        } else {
          data[key] = value;
        }
      }

      // Convert checkbox values to boolean
      data.fetch_description = jobForm.fetch_description.checked;
      data.rotate_proxies = jobForm.rotate_proxies.checked;

      // Send as JSON to backend
      fetch('http://192.168.1.143:5000/JobSpy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      .then(response => {
        spinner.style.display = 'none'; // Hide spinner
        if (!response.ok) throw new Error('Network response was not ok');
        return response.text();
      })
      .then(data => {
        console.log('JobSpy response:', data);
        alert('Job extraction complete! Check jobs_numbered.csv for results.');
      })
      .catch(error => {
        spinner.style.display = 'none'; // Hide spinner
        console.error('Error:', error);
        alert('Error running JobSpy: ' + error.message);
      });
    });
  }
});

