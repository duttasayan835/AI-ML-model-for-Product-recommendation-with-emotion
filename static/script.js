// script.js
document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("video");
  const captureButton = document.getElementById("capture");
  const emotionDetected = document.getElementById("emotion-detected");
  const productSlider = document.getElementById("product-slider");

  // Access the video stream from the user's webcam
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      video.srcObject = stream;
    })
    .catch((err) => {
      console.error("Error accessing webcam: ", err);
    });

  captureButton.addEventListener("click", function () {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(function (blob) {
      const formData = new FormData();
      formData.append("image", blob);

      fetch("/detect_emotion", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            console.error("Error detected:", data.error);
            emotionDetected.textContent = "Error: " + data.error;
            productSlider.innerHTML = "";
          } else {
            emotionDetected.textContent = "Emotion Detected: " + data.emotion;

            // Clear previous products
            productSlider.innerHTML = "";

            // Add new products
            data.products.forEach((product) => {
              const productItem = document.createElement("div");
              productItem.className = "product-item";
              productItem.innerHTML = `
                              <img src="${product.image}" alt="${product.name}">
                              <a href="${product.link}" target="_blank">${product.name}</a>
                          `;
              productSlider.appendChild(productItem);
            });
          }
        })
        .catch((error) => console.error("Error:", error));
    }, "image/jpeg");
  });
});
