// Source: squidfunk.github.io/mkdocs-material/reference/math (delimiter shape)
// Why document$: Material's instant loading swaps the page body, so math must
// be re-rendered on every navigation through Material's own observable.
// ASCII only is a deliberate policy: this file is served to the browser and
// reviewed as text, so bytes, code points and displayed content must agree.
document$.subscribe(({ body }) => {
  renderMathInElement(body, {
    delimiters: [
      { left: "$$",  right: "$$",  display: true  },
      { left: "$",   right: "$",   display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true  }
    ]
  });
});
