"use strict";

const MIN_DISPLAY_FILTER_LENGTH = 5;
const MAX_DISPLAY_FILTER_LENGTH = 30;

const diffSelectors = Array.from(document.getElementsByClassName("diff-selector"));

const buttonIdMap = diffSelectors.reduce((acc, button) => {
  const buttonId = button.dataset.id;

  acc[buttonId] = button;

  return acc;
}, {});

const renderCarouselControl = dir => {
  const navButton = document.createElement("a");
  const navIcon = document.createElement("span");

  navButton.className = `${dir} carousel-control`;
  navButton.href = "#original-text-carousel";
  navButton.dataset.slide = dir === "left" ? "prev" : "next";

  navIcon.className = `glyphicon glyphicon-chevron-${dir}`;

  navButton.appendChild(navIcon);

  return navButton;
};

const leftNavButton = renderCarouselControl("left");
const rightNavButton = renderCarouselControl("right");
const carouselAnchor = document.getElementById("carousel-anchor");

const diffShortcutAnchor = document.getElementById("diff-shortcut-anchor");

const renderDiff = (docId, diffFilterLength) => {
  const filterLength = diffFilterLength > MIN_DISPLAY_FILTER_LENGTH ? diffFilterLength : MIN_DISPLAY_FILTER_LENGTH;

  Object.entries(buttonIdMap).filter(x => x[0] !== docId).forEach(buttonIdPair => {
    const button = buttonIdPair[1];

    button.className = button.className.replace("active", "");
  });

  if (!buttonIdMap[docId].className.endsWith("active")) {
    buttonIdMap[docId].className += " active";
  }

  const diffPages = diffDocs[docId];

  const zipped = (() => {
    const lenDiff = diffPages.length - orgPages.length;

    if (lenDiff < 0) {
      const res = orgPages.slice(diffPages.length - lenDiff - 1).map(x => [x, ""]);

      return diffPages.map((t, i) => [orgPages[i], t]).concat(res);
    } else {
      const res = diffPages.slice(orgPages.length + lenDiff).map(x => ["", x]);

      return orgPages.map((t, i) => [t, diffPages[i]]).concat(res);
    }
  })();

  const diffBits = zipped.map(zip => {
    const [ original, diff ] = zip;

    const diffWords = isRedacted ? JsDiff.diffWords(original, diff) : JsDiff.diffWords(diff, original);

    return diffWords.filter(x => !/^\s*$/.test(x.value)).map(part => {
      const backgroundColor = part.added ? "black" : part.removed ? "red" : "";
      const textColor = part.added ? "white" : part.removed ? "black" : "grey";

      return [part.added !== undefined, part.removed !== undefined, [part.value.trim(), textColor, backgroundColor]] ;
    }).filter(x => x[2][0].length >= filterLength);
  });

  const carouselPages = diffBits.map(x => {
    return x.reduce((acc, bit) => {
      const [ _0, _1, [ value, color, backgroundColor ] ] = bit;

      const span = document.createElement('span');

      span.style.backgroundColor = backgroundColor;
      span.style.color = color;

      span.innerHTML = value;

      acc.appendChild(span);

      return acc;
    }, document.createDocumentFragment())
  }).map((frag, i) => {
    const carouselPage = document.createElement("div");
    const carouselContent = document.createElement("div");
    const carouselContentText = document.createElement("div");

    const docPage = document.createElement("h4");
    const docDom = document.createElement("p");

    carouselPage.className = `item ${i === 0 ? "active" : ""}`;
    carouselContent.className = "carousel-content";
    carouselContentText.className = "carousel-content-text";

    docDom.className = "document";

    docPage.appendChild(document.createTextNode(`Page: ${i + 1}`))
    docDom.appendChild(frag);

    carouselContentText.appendChild(docPage);
    carouselContentText.appendChild(docDom);
    carouselContent.appendChild(carouselContentText);
    carouselPage.appendChild(carouselContent);

    return carouselPage;
  });

  const indicators = carouselPages.map((_, i) => {
    const indicator = document.createElement("li");

    indicator.dataset.target = "#original-text-carousel";
    indicator.dataset.slideTo = `${i}`;
    indicator.className = `carousel-indicator ${i === 0 ? "active" : ""}`;

    return indicator;
  })

  const carousel = document.createElement("div");
  const carouselIndicators = document.createElement("ol");
  const carouselInner = document.createElement("div");

  carousel.id = "original-text-carousel";
  carousel.className = "carousel slide";
  carousel.dataset.ride="carousel";
  carousel.dataset.interval="false";

  carouselIndicators.className = "carousel-indicators";
  carouselInner.className = "carousel-inner";

  indicators.forEach(ind => carouselIndicators.appendChild(ind));
  carouselPages.forEach(page => carouselInner.appendChild(page));

  carousel.appendChild(carouselIndicators);
  carousel.appendChild(carouselInner);
  carousel.appendChild(leftNavButton);
  carousel.appendChild(rightNavButton);

  carouselAnchor.appendChild(carousel);

  carouselAnchor.dataset.currentDiff = docId;

  return diffBits.map(bits => {
    return bits.filter(bit => {
      return (bit[0] === true || bit[1] === true) && bit[2][0].length > MIN_DISPLAY_FILTER_LENGTH;
    }).map(x => [x[0], x[2][0]]);
  });
};

const displayDiffShortcuts = diffs => {
  const flatPageDiffs = diffs
    .reduce((acc, bits, i) => {
      return acc.concat(bits.map(x => {
        const [ isAdded, value ] = x;

        const span = document.createElement('span');

        span.innerHTML = value.replace(/<br>/g, "\n").trim().replace(/\n/g, "<br>");

        return [i, isAdded, span];
      }));
    }, []);

  const diffListItems = flatPageDiffs.map(pageDiff => {
    const [ pageNum, isAdded, content ] = pageDiff;
    const diffListElement = document.createElement("li");
    const diffListHeader = document.createElement("div");
    const pageNumber = document.createElement("h4");
    const redactionIndicator = document.createElement("span");

    const addIcon = document.createElement("i");
    const removeIcon = document.createElement("i");

    addIcon.className = "glyphicon glyphicon-pencil"

    removeIcon.className = "glyphicon glyphicon-erase"
    removeIcon.style.color = "red";

    diffListHeader.className = "row";

    pageNumber.innerHTML = `<a>Page: ${pageNum + 1}</a>`;
    pageNumber.className = "diff-shortcut-number list-group-item-heading col-sm-6";

    redactionIndicator.appendChild(isAdded ? addIcon : removeIcon);

    redactionIndicator.className = "outer-span pull-right";

    diffListElement.className = "list-group-item";

    pageNumber.dataset.target = "#original-text-carousel";
    pageNumber.dataset.slideTo = `${pageNum}`;

    content.className = "list-group-item-text";

    diffListHeader.appendChild(pageNumber);
    diffListHeader.appendChild(redactionIndicator);

    diffListElement.appendChild(diffListHeader);
    diffListElement.appendChild(content);

    return diffListElement;
  });

  const diffShortcutList = diffListItems.reduce((acc, item) => {
    acc.appendChild(item);

    return acc;
  }, document.createElement("ol"));

  diffShortcutList.id = "diff-shortcut";
  diffShortcutList.className = "list-group";

  diffShortcutAnchor.appendChild(diffShortcutList);
};

(() => {
  const renderAll = (docId, diffLength) => {
    if (carouselAnchor.lastChild) {
      carouselAnchor.removeChild(carouselAnchor.lastChild);
    }

    if (diffShortcutAnchor.lastChild) {
      diffShortcutAnchor.removeChild(diffShortcutAnchor.lastChild);
    }

    displayDiffShortcuts(renderDiff(docId, diffLength));
  };

  renderAll(Object.keys(diffDocs)[0], MIN_DISPLAY_FILTER_LENGTH);

  diffSelectors.forEach(button => {
    button.addEventListener("click", e => {
      const targetId = e.target.dataset.id;

      if (carouselAnchor.dataset.currentDiff !== targetId) {
        renderAll(targetId, document.getElementById("diff-len-slider").value);
      }
    })
  });

  const slider = new Slider("#diff-len-slider", {
    formatter: value => {
      return `Current diff length: ${value}`;
    }
  });

  slider.on("slideStop", v => renderAll(carouselAnchor.dataset.currentDiff, v));
})();
