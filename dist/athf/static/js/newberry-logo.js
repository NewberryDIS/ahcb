class NewberryLogo extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({
      mode: "open",
    });
    const wrapper = document.createElement("div");
    wrapper.innerHTML = `<div class="newberry-logo host">
  <a href="https://www.newberry.org" target="_blank">
    <svg
      version="1.1"
      id="svg1"
      width="50.484196"
      height="48.6637"
      viewBox="0 0 50.484196 48.6637"
      xmlns="http://www.w3.org/2000/svg"
      xmlns:svg="http://www.w3.org/2000/svg">
      <defs
        id="defs1" />
      <g
        id="g1"
        transform="translate(0,-1.3762177)">
        <path
          d="M 0,31.853984 V 13.669408 L 8.7001194,8.7540012 c 4.7850656,-2.7034739 8.7225656,-4.915407 8.7500006,-4.915407 0.02743,0 0.04988,1.1024991 0.04988,2.4499981 0,1.4572855 0.03798,2.4499982 0.09372,2.4499982 0.05155,0 2.80289,-1.6483703 6.114094,-3.663045 3.311205,-2.0146748 6.092779,-3.6793166 6.181277,-3.6992042 0.0885,-0.019888 3.850906,2.3636557 8.360906,5.2967627 l 8.200001,5.332922 0.05,15.54127 0.05,15.541269 1.967098,0.05 1.967099,0.05 -3.745139,3.425676 -3.745138,3.425677 -6.971961,-0.02568 -6.97196,-0.02568 -0.05,-18.990414 -0.05,-18.990414 -2.833733,-1.731973 -2.833739,-1.7319733 -2.836801,1.7224013 -2.836801,1.722401 -0.0045,19.024986 -0.0045,19.024986 H 8.8000005 0 Z"
          id="path1" />
      </g>
    </svg>
  </a>

  <a href="https://collections.newberry.org" id="dc-text" target="_blank" style="text-decoration: none;">
    <span>
      Digital
    </span>
    <span>
      Collections 
    </span>
  </a>
</div>`;
    const style = document.createElement("style");
    style.textContent = `
.newberry-logo {
--static-color: var(--fg-color);
  --hover-color: var(--accent-color);
  display: flex;
  justify-content: start;
  align-items: center;
  gap: 3px;
  & * {
  transition: 300ms;
  }
}

svg, text, path {
  fill: var(--static-color);
}
a:hover :is(svg, path, text) {
  fill: var(--hover-color);
}
a {
  color: var(--static-color);
}
a:hover {
  color: var(--hover-color);
}
#dc-text {
  font-family: 'styrene';
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: start;
  & span {
    line-height: 1rem;
    position: relative;
  }
}
@media screen and (max-width: 600px){
  #dc-text {
    display: none;
  }
}
                `;
    this.shadowRoot.appendChild(wrapper);
    this.shadowRoot.appendChild(style);
  }
}

customElements.define("newberry-logo", NewberryLogo);
