const states = document.querySelectorAll(".card-img-name");
states.forEach((s) => {
  // console.log("wandering....");
  s.addEventListener("click", clickWander);
});
function clickWander(e) {
  const grandparent = e.target.parentNode.parentNode;
  if (["state-ny", "state-ga"].includes(grandparent.id)) {
    // console.log("wandering....");
    e.preventDefault();
    // e.stopPropagation();
    e.target.classList.toggle("clicked");
    boppin(e.target.classList.contains("clicked"));
  }
}

document.body.style.setProperty("--top", 0);
document.body.style.setProperty("--left", "-20px");
let expander = 0;
function boppin(go) {
  if (go) {
    intervalId = setInterval(() => {
      expander++;
      let newTop = Math.round(Math.random() * (20 + expander) - 10);
      let newLeft = Math.round(Math.random() * (20 + expander) - 10);
      document.body.style.setProperty("--top", `${newTop}px`);
      document.body.style.setProperty("--left", `${newLeft}px`);
      // document.body.style.setProperty('--expander', expander)
    }, 250);
  } else {
    clearInterval(intervalId);
  }
}
