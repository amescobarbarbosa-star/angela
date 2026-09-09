const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fi = require("react-icons/fi");

// Extract {attrs, inner, viewBox} from a react-icons component's rendered markup.
function decompose(IconComp) {
  const markup = ReactDOMServer.renderToStaticMarkup(React.createElement(IconComp));
  const m = markup.match(/^<svg([^>]*)>([\s\S]*)<\/svg>$/);
  if (!m) throw new Error("Could not parse icon svg: " + markup);
  const attrsStr = m[1];
  const inner = m[2];
  const vb = attrsStr.match(/viewBox="([^"]+)"/);
  const viewBox = vb ? vb[1] : "0 0 24 24";
  const gAttrs = attrsStr
    .replace(/\swidth="[^"]*"/, "")
    .replace(/\sheight="[^"]*"/, "")
    .replace(/\sviewBox="[^"]*"/, "")
    .replace(/\sxmlns="[^"]*"/, "")
    .trim();
  return { gAttrs, inner, viewBox };
}

// Render an icon inside a filled circle as a PNG data URI.
// iconName: key of react-icons/fi, e.g. "FiUpload"
async function circleIcon({ iconName, circleColor, iconColor, size = 256, iconScale = 0.46 }) {
  const IconComp = fi[iconName];
  if (!IconComp) throw new Error("Unknown icon " + iconName);
  const { gAttrs, inner, viewBox } = decompose(IconComp);
  const parts = viewBox.split(/\s+/).map(Number);
  const vw = parts[2] || 24;
  const iconPx = size * iconScale;
  const offset = (size - iconPx) / 2;
  const scale = iconPx / vw;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
    <circle cx="${size / 2}" cy="${size / 2}" r="${size / 2}" fill="#${circleColor}"/>
    <g transform="translate(${offset},${offset}) scale(${scale})" ${gAttrs} color="#${iconColor}">${inner}</g>
  </svg>`;
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

module.exports = { circleIcon };
