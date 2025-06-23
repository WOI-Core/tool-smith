document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('taskForm');
    const statusEl = document.getElementById('status');
    const fileDropdown = document.getElementById('fileDropdown');
    const fileContent = document.getElementById('fileContent');
    const fileExplorer = document.getElementById('fileExplorer');

    const downloadBtn = document.createElement('button');
    downloadBtn.textContent = 'Download ZIP';
    downloadBtn.style.marginTop = '10px';
    downloadBtn.style.display = 'none';
    form.appendChild(downloadBtn);

    const uploadBtn = document.createElement('button');
    uploadBtn.textContent = 'Upload to grader';
    uploadBtn.style.marginTop = '10px';
    uploadBtn.style.display = 'none';
    form.appendChild(uploadBtn);

    let latestBlob = null;
    let latestFileName = '';

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        statusEl.style.color = 'black';
        statusEl.textContent = 'Generating... please wait';

        const contentName = document.getElementById('contentName').value.trim();
        const casesSize = parseInt(document.getElementById('casesSize').value.trim());
        const detail = document.getElementById('detail').value.trim();

        if (!contentName || !casesSize) {
            statusEl.style.color = 'red';
            statusEl.textContent = 'Please fill in content name and number of test cases.';
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/tool-smith', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content_name: contentName,
                    cases_size: casesSize,
                    detail: detail
                }),
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }

            const blob = await response.blob();
            latestBlob = blob;
            latestFileName = `${contentName}_tasks.zip`;

            const zip = await JSZip.loadAsync(blob);
            fileDropdown.innerHTML = "";
            fileExplorer.style.display = "block";

            Object.keys(zip.files).forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                fileDropdown.appendChild(option);
            });

            fileDropdown.onchange = async function () {
                const file = zip.files[this.value];
                if (file) {
                    const text = await file.async("string");
                    fileContent.textContent = text;
                }
            };

            fileDropdown.dispatchEvent(new Event('change'));

            statusEl.style.color = 'green';
            statusEl.textContent = 'Task generated! You can now download the ZIP or browse files below.';

            downloadBtn.style.display = 'inline-block';
            uploadBtn.style.display = 'inline-block';

        } catch (error) {
            statusEl.style.color = 'red';
            statusEl.textContent = 'Error: ' + error.message;
        }
    });

    downloadBtn.addEventListener('click', function () {
        if (latestBlob) {
            const downloadUrl = URL.createObjectURL(latestBlob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = latestFileName;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(downloadUrl);
        }
    });
});
