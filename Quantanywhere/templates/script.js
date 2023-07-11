window.addEventListener("loader", function () {
    const element = document.getElementById("div-01");
    element.remove(); // Removes the div with the 'div-02' id
    setTimeout(function () {
        const element = document.getElementById("div-01");
        element.remove(); // Removes the div with the 'div-02' id
      div.classList.remove('loading-page'); // Remove the loading page element from the DOM
    }, 300);
  });
