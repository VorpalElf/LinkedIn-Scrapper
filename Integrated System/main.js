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
        // Fetch and display jobs
        fetch('http://192.168.1.143:5000/jobs')
          .then(res => res.json())
          .then(jobs => {
            const jobResults = document.getElementById('job-results');
            const jobTable = document.getElementById('job-table');
            if (jobs && jobs.length > 0) {
              // Build table
              let html = '<table><thead><tr>';
              Object.keys(jobs[0]).forEach(key => {
                html += `<th>${key}</th>`;
              });
              html += '</tr></thead><tbody>';
              jobs.forEach(job => {
                html += '<tr>';
                Object.values(job).forEach(val => {
                  html += `<td>${val}</td>`;
                });
                html += '</tr>';
              });
              html += '</tbody></table>';
              jobTable.innerHTML = html;
              jobResults.style.display = 'block';
            } else {
              jobTable.innerHTML = '<p>No jobs found.</p>';
              jobResults.style.display = 'block';
            }
          });
      })
      .catch(error => {
        spinner.style.display = 'none'; // Hide spinner
        console.error('Error:', error);
        alert('Error running JobSpy: ' + error.message);
      });
    });
  }
});

