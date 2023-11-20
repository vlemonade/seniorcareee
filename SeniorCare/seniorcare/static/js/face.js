document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureButton = document.getElementById('capture-btn');  
    const retakeButton = document.getElementById('retake-btn');
    const submitLink = document.getElementById('submit-btn');
    let capturedImage;  
    const seniorId = document.body.dataset.seniorId;

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (err) {
            console.log("An error occurred: " + err);
        });

    captureButton.addEventListener('click', function () {
        video.pause();
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        capturedImage = canvas.toDataURL('image/jpeg');  

        retakeButton.style.display = 'block';
        submitLink.style.display = 'block';

        captureButton.style.display = 'none';
    });

    retakeButton.addEventListener('click', function () {
        video.play();

        retakeButton.style.display = 'none';
        submitLink.style.display = 'none';

        captureButton.style.display = 'block';
    });

    submitLink.addEventListener('click', function (event) {
        event.preventDefault();

        const csrfTokenElement = document.getElementsByName("csrfmiddlewaretoken")[0];
        if (csrfTokenElement) {
            const csrfToken = csrfTokenElement.value;

            console.log(csrfToken);

            fetch(`/facial_recognition/${seniorId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",  
                    "X-CSRFToken": csrfToken,
                },
                body: `captured_image=${encodeURIComponent(capturedImage)}`, 
            })
            .then(response => response.json())
            .then(data => {
                if (data.match) {
                    window.location.href = `/match/${seniorId}/`;
                } else {
                    window.location.href = `/unmatch/${seniorId}/`;
                }
            })
            .catch(error => {
                console.error("Error during fetch:", error);
            });
        } else {
            console.error("CSRF token element not found.");
        }
    });
});
