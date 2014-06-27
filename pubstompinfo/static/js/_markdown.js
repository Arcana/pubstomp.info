$(document).ready(function () {
    $('.markdown').each(function (i, elem) {
        elem.innerHTML = Markdown.getSanitizingConverter().makeHtml(elem.innerHTML);
    });
});
