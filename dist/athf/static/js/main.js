console.log("asdf");
navMenu = document.getElementById("nav-menu");
navMenu.addEventListener("click", function (e) {
  e.target.classList.toggle("open");
});

// function getTinasGpa(coursesTaken = 5, coursesRemaining = 2, curGpa = 2.8) {
//   let breakPoint = 4;
//   Array.from({ length: 10 }).forEach((_, i) => {
//     let sumCompleted = curGpa * coursesTaken;
//     let iteratorGpa = i / 10 + 3;
//     let potentialAddedSum = iteratorGpa * coursesRemaining;
//     let totalClasses = coursesTaken + coursesRemaining;
//     let av = (potentialAddedSum + sumCompleted) / totalClasses;
//     if (iteratorGpa < breakPoint && av >= 3) {
//       breakPoint = iteratorGpa;
//     }
//     // console.log(`if you average 3.${i}, you'll get an overall average of ${av}`)
//   });
//
//   console.log(
//     `${breakPoint} is the lowest GPA you can get for the ${coursesRemaining} courses to get a 3.0 by fall 2026.`,
//   );
// }
// // getTinasGpa();
