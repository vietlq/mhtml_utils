// https://developer.mozilla.org/en-US/docs/Web/XPath/Introduction_to_using_XPath_in_JavaScript
// https://www.w3schools.com/jsref/met_document_queryselector.asp
// https://stackoverflow.com/questions/614797/xpath-find-a-node-that-has-a-given-attribute-whose-value-contains-a-string
// https://stackoverflow.com/questions/103325/what-is-the-correct-xpath-for-choosing-attributes-that-contain-foo

let img_iterator = document.evaluate('//img[contains(@alt, " v ")]', document);
let li_iterator = document.evaluate('//li[./span[contains(text(), " v ")]]', document);
let span_iterator = document.evaluate('//li/span[contains(text(), " v ")]', document);
let thisNode = span_iterator.iterateNext();

while (thisNode) {
    console.log(thisNode.innerText);
    thisNode = span_iterator.iterateNext();
}
